#!/usr/bin/env python3
"""Update manual week % used: set_reading.py claude 42"""
import json, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Africa/Johannesburg")
path = ROOT / "manual_overrides.json"
data = json.loads(path.read_text())
if len(sys.argv) != 3:
    print("Usage: set_reading.py <claude|chatgpt|grok> <week_pct_used>")
    sys.exit(1)
key, pct = sys.argv[1], float(sys.argv[2])
if key not in data:
    print("Unknown provider", key)
    sys.exit(1)
data[key] = {
    "week_pct_used": max(0.0, min(100.0, pct)),
    "updated_at": datetime.now(TZ).isoformat(timespec="seconds"),
}
path.write_text(json.dumps(data, indent=2) + "\n")
print("Updated", key, "→", data[key]["week_pct_used"])
