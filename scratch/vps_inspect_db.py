import json
import os

db_path = "/root/ZiSi-v2/data/positions_state.json"
if os.path.exists(db_path):
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    closed = data.get("closed", [])
    active = data.get("active", [])
    print(f"CLOSED_LEN: {len(closed)}")
    print(f"ACTIVE_LEN: {len(active)}")
    if closed:
        print(f"NEWEST: {closed[0]['entry_time']} - {closed[0].get('event_title', '')}")
        print(f"OLDEST: {closed[-1]['entry_time']} - {closed[-1].get('event_title', '')}")
        pnl = sum(p.get('realized_pnl', 0.0) for p in closed)
        print(f"SUM_PNL: ${pnl:.2f}")
        print(f"CALCULATED_BALANCE: ${50.0 + pnl:.2f}")
