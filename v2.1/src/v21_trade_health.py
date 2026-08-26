#!/usr/bin/env python3
"""Exact-strike and underlying thesis-health observer for V2.1 shadow research."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


def _num(v: Any, d: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def latest_contract(path: Path, symbol: str, now: datetime) -> dict[str, Any] | None:
    if not symbol or not path.exists() or path.stat().st_size == 0:
        return None
    found = None
    found_t = None
    with path.open("r", newline="", encoding="utf-8") as h:
        for row in csv.DictReader(h):
            if str(row.get("symbol")) != symbol:
                continue
            try:
                t = datetime.fromisoformat(str(row.get("generated_at")).replace("Z", "+00:00"))
            except Exception:
                continue
            if t <= now and (found_t is None or t > found_t):
                found, found_t = row, t
    return found


def evaluate(prior_state: Mapping[str, Any] | None, slot: datetime, position: Mapping[str, Any] | None, spot: float, expansion: Mapping[str, Any], recent_micro: Sequence[Mapping[str, Any]], contract: Mapping[str, Any] | None) -> dict[str, Any]:
    if not position:
        return {"status": "FLAT", "updated_at": slot.isoformat()}

    st = dict(prior_state or {})
    direction = str(position.get("direction"))
    entry_spot = _num(position.get("entry_spot"))
    entry_price = _num(position.get("entry_price"))
    qty = int(_num(position.get("quantity"), 65))
    premium = _num((contract or {}).get("bid"), _num((contract or {}).get("ltp")))
    spot_move = spot - entry_spot
    favorable_spot = spot_move if direction == "CE" else -spot_move
    option_move = premium - entry_price if premium else 0.0

    st["nifty_mfe"] = max(_num(st.get("nifty_mfe")), favorable_spot)
    st["nifty_mae"] = min(_num(st.get("nifty_mae")), favorable_spot)
    st["option_mfe"] = max(_num(st.get("option_mfe")), option_move)
    st["option_mae"] = min(_num(st.get("option_mae")), option_move)

    wanted = "BULLISH" if direction == "CE" else "BEARISH"
    opposite = "BEARISH" if wanted == "BULLISH" else "BULLISH"
    exp_dir = str(expansion.get("direction", "MIXED"))
    stage = str(expansion.get("stage", "BALANCE"))

    scores = [_num(x.get("direction_score")) for x in list(recent_micro)[-3:]]
    opp_votes = sum(1 for s in scores if (s <= -0.25 if wanted == "BULLISH" else s >= 0.25))

    if favorable_spot >= 5 and option_move >= 0:
        thesis = "HEALTHY"
    elif favorable_spot < -5 and exp_dir == opposite and opp_votes >= 2:
        thesis = "FAILED"
    elif stage == "ABSORPTION_WARNING" or favorable_spot < -2:
        thesis = "WEAKENING"
    else:
        thesis = "STALLED"

    if not premium:
        option_health = "NO_DATA"
    elif favorable_spot > 3 and option_move <= 0:
        option_health = "DIVERGING"
    elif favorable_spot <= 2 and option_move < 0:
        option_health = "DECAYING"
    elif option_move >= 0:
        option_health = "HEALTHY"
    else:
        option_health = "WEAK"

    shadow_exit = bool(thesis == "FAILED" and premium and premium < entry_price and opp_votes >= 3)
    return {
        **st,
        "status": "OPEN",
        "updated_at": slot.isoformat(),
        "direction": direction,
        "symbol": position.get("symbol"),
        "spot": round(spot, 3),
        "premium": round(premium, 3) if premium else None,
        "favorable_nifty_points": round(favorable_spot, 3),
        "option_move": round(option_move, 3),
        "market_thesis_health": thesis,
        "option_response_health": option_health,
        "shadow_early_exit": shadow_exit,
        "shadow_exit_reason": "PERSISTENT_MICRO_THESIS_FAILURE" if shadow_exit else None,
        "shadow_pnl": round(option_move * qty, 2) if premium else None,
    }
