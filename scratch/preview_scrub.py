import json
from datetime import datetime

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

try:
    with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

closed = data.get("closed", [])
print(f"Total closed positions: {len(closed)}")

cutoff = datetime.fromisoformat("2026-07-19T14:49:00+00:00")
to_keep = []
to_scrub = []

total_loss_to_recover = 0.0

for pos in closed:
    exit_time_str = pos.get("exit_time") or pos.get("close_time") or ""
    if exit_time_str:
        try:
            clean_time = exit_time_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_time)
        except Exception:
            dt = datetime.min
    else:
        dt = datetime.min
        
    if dt >= cutoff:
        to_scrub.append((dt, pos))
        total_loss_to_recover += pos.get("realized_pnl", 0.0)
    else:
        to_keep.append(pos)

print(f"\nPositions to keep: {len(to_keep)}")
print(f"Positions to scrub: {len(to_scrub)}")
print(f"Total PnL of scrubbed positions: {total_loss_to_recover:.2f} USD")

print("\nDetail of positions to scrub:")
for dt, p in to_scrub:
    print(f"  - Title: {p.get('event_title')} | Tranche: {p.get('tranche')} | Realized PnL: {p.get('realized_pnl')} | Exit Time: {p.get('exit_time')}")
