#!/usr/bin/env python3
"""Compute day/week remaining % for Claude, ChatGPT, Grok with weekday-heavy weights."""
from __future__ import annotations

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text())
OVERRIDES = json.loads((ROOT / "manual_overrides.json").read_text())
OUT = ROOT / "public" / "data" / "usage.json"
TZ = ZoneInfo(CONFIG.get("timezone", "Africa/Johannesburg"))


def week_bounds(today: date) -> tuple[date, date]:
    # Monday = 0
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def day_weight(d: date, wd: float, we: float) -> float:
    return we if d.weekday() >= 5 else wd


def budgets_for_week(week_start: date, W: float, wd: float, we: float) -> dict[date, float]:
    S = 5 * wd + 2 * we
    out = {}
    for i in range(7):
        d = week_start + timedelta(days=i)
        out[d] = W * day_weight(d, wd, we) / S
    return out


def main() -> None:
    now = datetime.now(TZ)
    today = now.date()
    week_start, week_end = week_bounds(today)
    wd = float(CONFIG["weekday_weight"])
    we = float(CONFIG["weekend_weight"])
    days_left = (week_end - today).days + 1

    providers_out = {}
    for key, meta in CONFIG["providers"].items():
        W = float(meta["weekly_units"])
        budgets = budgets_for_week(week_start, W, wd, we)
        ov = OVERRIDES.get(key) or {}
        pct_used = ov.get("week_pct_used")
        has_reading = pct_used is not None

        if has_reading:
            pct_used = max(0.0, min(100.0, float(pct_used)))
            U = W * (pct_used / 100.0)
            week_remaining_pct = max(0.0, 100.0 - pct_used)
            remaining_units = max(0.0, W - U)
        else:
            pct_used = None
            U = None
            week_remaining_pct = None
            remaining_units = None

        # Ideal spend through end of yesterday (pacing)
        ideal_through_yesterday = sum(
            budgets[week_start + timedelta(days=i)]
            for i in range(today.weekday())
        )
        ideal_through_today = ideal_through_yesterday + budgets[today]
        today_budget = budgets[today]

        # Remaining calendar budgets from today through Sunday
        remaining_calendar = sum(
            budgets[today + timedelta(days=i)] for i in range(days_left)
        )

        if has_reading:
            # Bank: unused from earlier days rolls into available_today
            # Approximate past usage as min(U, ideal_through_yesterday) split is unknown;
            # use: units left should cover remaining_calendar at even pace within weights.
            # Day remaining = how much of TODAY's slice is left if we burn remaining_units
            # proportionally to today's share of remaining_calendar.
            if remaining_calendar > 0:
                today_fair = remaining_units * (today_budget / remaining_calendar)
            else:
                today_fair = 0.0
            # If behind schedule (used more than ideal_through_yesterday), today_fair shrinks.
            ahead_units = ideal_through_yesterday - min(U, ideal_through_yesterday)
            # Simpler pacing meter: compare U to ideal_through_today
            pace_delta = ideal_through_today - U  # positive = ahead (under budget)
            day_remaining_pct = max(0.0, min(100.0, 100.0 * (today_fair / today_budget))) if today_budget else 0.0
            # If already used entire week, day is 0
            if remaining_units <= 0:
                day_remaining_pct = 0.0
            status = (
                "voor" if pace_delta > today_budget * 0.05
                else ("agter" if pace_delta < -today_budget * 0.05 else "reg")
            )
        else:
            today_fair = today_budget
            day_remaining_pct = None
            pace_delta = None
            status = "wag_vir_lesing"

        providers_out[key] = {
            "label": meta["label"],
            "note": meta.get("note"),
            "source": "manual" if has_reading else "geen",
            "week_pct_used": pct_used,
            "week_remaining_pct": round(week_remaining_pct, 1) if week_remaining_pct is not None else None,
            "day_remaining_pct": round(day_remaining_pct, 1) if day_remaining_pct is not None else None,
            "today_budget_units": round(today_budget, 2),
            "today_fair_units": round(today_fair, 2) if has_reading else round(today_budget, 2),
            "remaining_units": round(remaining_units, 2) if remaining_units is not None else None,
            "pace_status": status,
            "reading_updated_at": ov.get("updated_at"),
            "day_type": "naweek" if today.weekday() >= 5 else "weekdag",
        }

    # Weight legend for UI
    sample = budgets_for_week(week_start, 100.0, wd, we)

    payload = {
        "updated_at": now.isoformat(timespec="seconds"),
        "timezone": str(TZ),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "today": today.isoformat(),
        "days_left_in_week": days_left,
        "weights": {"weekday": wd, "weekend": we},
        "daily_budget_pct_of_week": {
            "weekdag": round(100 * wd / (5 * wd + 2 * we), 1),
            "naweek": round(100 * we / (5 * wd + 2 * we), 1),
        },
        "providers": providers_out,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
