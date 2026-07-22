import json
from datetime import datetime

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
closed = data.get("closed", [])

print("Index | Entry Time (UTC) | Asset | PnL | Title")
print("-" * 80)
for idx, p in enumerate(closed[:100]):
    entry_time = p.get("entry_time", "")
    asset = p.get("event_title", "").split("[")[2].split("]")[0] if "[" in p.get("event_title", "") else "UNKNOWN"
    pnl = p.get("realized_pnl", 0.0)
    title = p.get("event_title", "")
    print(f"{idx:5d} | {entry_time} | {asset:5s} | {pnl:+.2f} | {title[:40]}")
