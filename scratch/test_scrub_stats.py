import json
from datetime import datetime

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
closed = data.get("closed", [])

for label, cutoff_str in [("16:49 SAST (14:49 UTC)", "2026-07-19T14:49:00+00:00"), ("17:49 SAST (15:49 UTC)", "2026-07-19T15:49:00+00:00")]:
    cutoff = datetime.fromisoformat(cutoff_str)
    to_keep = []
    to_scrub = []
    pnl = 0.0
    for pos in closed:
        exit_time_str = pos.get("exit_time") or pos.get("close_time") or ""
        if exit_time_str:
            try:
                dt = datetime.fromisoformat(exit_time_str.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.min
        else:
            dt = datetime.min
        if dt >= cutoff:
            to_scrub.append(pos)
            pnl += pos.get("realized_pnl", 0.0)
        else:
            to_keep.append(pos)
    print(f"Cutoff {label}: keep={len(to_keep)}, scrub={len(to_scrub)}, net_pnl_to_revert={pnl:.2f} USD")
