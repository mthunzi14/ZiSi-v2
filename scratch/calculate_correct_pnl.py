import json
import os

path = "/root/ZiSi-v2/data/positions_state.json"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    closed = d.get("closed", [])
    s = sum(float(p.get("realized_pnl", 0.0)) for p in closed)
    print(f"SUM of remaining closed trades: {s}")
    print(f"Top-level summary realized_pnl: {d.get('summary', {}).get('realized_pnl')}")
    print(f"Top-level summary closed_count: {d.get('summary', {}).get('closed_count')}")
    print(f"Length of closed list: {len(closed)}")
else:
    print("File not found")
