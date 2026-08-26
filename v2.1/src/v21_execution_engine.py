#!/usr/bin/env python3
"""Shadow setup arming / early-execution state machine for V2.1.

It never places a paper trade. It records when pre-expansion evidence first
appears so future sessions can compare PREARM -> 3m confirmation -> 1m ignition
against the normal completed-5m decision without hindsight reconstruction.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Mapping


def _num(v: Any, d: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def step(state: Mapping[str, Any] | None, slot: datetime, expansion: Mapping[str, Any], zone_memory: Mapping[str, Any], rolling_oi: Mapping[str, Any], expiry_minutes: int = 12) -> dict[str, Any]:
    st = dict(state or {})
    active = dict(st.get("active") or {})
    stage = str(expansion.get("stage", "BALANCE"))
    direction = str(expansion.get("direction", "MIXED"))
    nearest = zone_memory.get("nearest") or {}
    oi3 = _num(rolling_oi.get("score_3m"))
    oi_dir = "BULLISH" if oi3 > 0.10 else "BEARISH" if oi3 < -0.10 else "MIXED"

    if active.get("armed_time"):
        try:
            armed_t = datetime.fromisoformat(str(active["armed_time"]))
            if slot - armed_t > timedelta(minutes=expiry_minutes):
                active["status"] = "EXPIRED"
                st["last_completed"] = active
                active = {}
        except Exception:
            active = {}

    prearm_stage = stage in {"BUILDUP", "PRESSURE", "IGNITION"}
    if not active and prearm_stage and direction in {"BULLISH", "BEARISH"}:
        active = {"status": "ARMED", "direction": direction, "armed_time": slot.isoformat(), "armed_stage": stage, "zone": nearest, "oi_3m_at_arm": oi3}

    if active:
        wanted = str(active.get("direction"))
        if stage == "ABSORPTION_WARNING" and str(expansion.get("direction")) == wanted:
            active["status"] = "WAITING_ABSORPTION"
        elif direction not in {wanted, "MIXED"} and stage in {"PRESSURE", "IGNITION", "EXPANSION"}:
            active["status"] = "CANCELLED"
            active["cancel_time"] = slot.isoformat()
            active["cancel_reason"] = "OPPOSITE_PRESSURE"
            st["last_completed"] = active
            active = {}
        elif stage == "IGNITION" and direction == wanted:
            active.setdefault("ignition_time", slot.isoformat())
            active["status"] = "IGNITION_SEEN"
        elif stage == "EXPANSION" and direction == wanted:
            active.setdefault("expansion_time", slot.isoformat())
            active["status"] = "EXPANSION_SEEN"

        if active and oi_dir == wanted:
            active.setdefault("oi_confirm_time", slot.isoformat())

    st["active"] = active
    st["last_slot"] = slot.isoformat()
    return st


def mark_five_minute_confirmation(state: Mapping[str, Any] | None, slot: datetime, direction: str | None) -> dict[str, Any]:
    st = dict(state or {})
    active = dict(st.get("active") or {})
    if active and direction and str(active.get("direction")) == ("BULLISH" if direction == "CE" else "BEARISH"):
        active["five_minute_confirm_time"] = slot.isoformat()
        active["five_minute_direction"] = direction
        active["status"] = "FIVE_MIN_CONFIRMED"
    st["active"] = active
    return st
