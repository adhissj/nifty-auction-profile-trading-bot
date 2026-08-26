#!/usr/bin/env python3
"""Causal rolling OI diagnostics for V2.1 research.

This replaces the misleading ``15m == 30m == immediate`` research symptom with
explicit window deltas measured from stored snapshots.  The runner can log this
side-by-side with its legacy OI state before any promotion to trading authority.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence


def _num(v: Any, d: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _parse(v: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None


def read_snapshots(path: Path, limit: int = 240) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as h:
        rows = list(csv.DictReader(h))
    return rows[-limit:]


def _nearest_at_or_before(rows: Sequence[Mapping[str, Any]], target: datetime) -> Mapping[str, Any] | None:
    best = None
    best_t = None
    for row in rows:
        t = _parse(row.get("generated_at"))
        if t is None or t > target:
            continue
        if best_t is None or t > best_t:
            best, best_t = row, t
    return best


def _window_state(rows: Sequence[Mapping[str, Any]], now: datetime, minutes: int) -> dict[str, Any]:
    current = _nearest_at_or_before(rows, now)
    prior = _nearest_at_or_before(rows, now - timedelta(minutes=minutes))
    if not current or not prior:
        return {"minutes": minutes, "available": False, "score": 0.0}
    call_delta = _num(current.get("call_oi")) - _num(prior.get("call_oi"))
    put_delta = _num(current.get("put_oi")) - _num(prior.get("put_oi"))
    denom = abs(call_delta) + abs(put_delta)
    score = (put_delta - call_delta) / denom if denom else 0.0
    return {
        "minutes": minutes,
        "available": True,
        "call_oi_delta": call_delta,
        "put_oi_delta": put_delta,
        "score": round(score, 6),
        "direction": "BULLISH" if score > 0.10 else "BEARISH" if score < -0.10 else "MIXED",
    }


def compute(path: Path, now: datetime) -> dict[str, Any]:
    rows = read_snapshots(path)
    if not rows:
        return {"status": "NO_DATA", "fresh": False}
    current = _nearest_at_or_before(rows, now)
    current_t = _parse((current or {}).get("generated_at"))
    age = (now - current_t).total_seconds() if current_t else 999999.0

    states = {m: _window_state(rows, now, m) for m in (1, 3, 15, 30)}
    causal = [r for r in rows if (_parse(r.get("generated_at")) is not None and _parse(r.get("generated_at")) <= now)]
    gaps = [_num(r.get("call_oi_change")) - _num(r.get("put_oi_change")) for r in causal[-4:]]
    velocity = gaps[-1] - gaps[-2] if len(gaps) >= 2 else 0.0
    prior_velocity = gaps[-2] - gaps[-3] if len(gaps) >= 3 else 0.0
    acceleration = velocity - prior_velocity
    return {
        "status": "OK",
        "snapshot_age_seconds": round(age, 2),
        "fresh": age <= 90,
        "score_1m": states[1].get("score", 0.0),
        "score_3m": states[3].get("score", 0.0),
        "score_15m": states[15].get("score", 0.0),
        "score_30m": states[30].get("score", 0.0),
        "windows": {str(k): v for k, v in states.items()},
        "call_put_doi_gap": gaps[-1] if gaps else 0.0,
        "gap_velocity": velocity,
        "gap_acceleration": acceleration,
        "transition_force": -velocity,
    }
