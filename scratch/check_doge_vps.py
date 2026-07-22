import json
from pathlib import Path

p_path = Path("/root/ZiSi-v2/data/positions_state.json")
if not p_path.exists():
    p_path = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json")

data = json.load(open(p_path, "r", encoding="utf-8"))
open_pos = data.get("open", [])
closed_pos = data.get("closed", [])

print(f"Open Positions Count: {len(open_pos)}")
for p in open_pos:
    print("  OPEN:", p.get("order_id"), p.get("asset"), p.get("timeframe"), p.get("direction"), p.get("size"))

print(f"Closed Positions Count: {len(closed_pos)}")
doge_closed = [t for t in closed_pos if t.get("asset") == "DOGE" or "DOGE" in str(t)]
print(f"DOGE Closed Positions Count: {len(doge_closed)}")
for t in doge_closed:
    print("  DOGE CLOSED:", t.get("order_id"), t.get("closed_at"), t.get("realized_pnl"))
