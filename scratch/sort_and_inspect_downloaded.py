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

# Parse exit times and sort descending (latest first)
parsed_positions = []
for pos in closed:
    exit_time_str = pos.get("exit_time") or pos.get("close_time")
    if exit_time_str:
        try:
            clean_time = exit_time_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_time)
        except Exception:
            dt = datetime.min
    else:
        dt = datetime.min
    parsed_positions.append((dt, pos))

parsed_positions.sort(key=lambda x: x[0], reverse=True)

print("Top 10 latest closed positions in downloaded positions_state.json:")
for idx, (dt, pos) in enumerate(parsed_positions[:10]):
    print(f"\n--- Position {idx+1} ---")
    print(f"Event Title: {pos.get('event_title')}")
    print(f"Direction: {pos.get('direction')}")
    print(f"Exit Time: {pos.get('exit_time') or pos.get('close_time')} (Parsed: {dt})")
    print(f"Entry Price: {pos.get('entry_price')}")
    print(f"Exit Price: {pos.get('exit_price')}")
    print(f"Entry Spot: {pos.get('entry_spot')}")
    print(f"Exit Spot / Live Spot: {pos.get('exit_spot') or pos.get('live_spot') or pos.get('current_price')}")
    print(f"Realized PnL: {pos.get('realized_pnl')}")
    print(f"Tranche: {pos.get('tranche') or 'Full'}")
    print(f"Exit Reason: {pos.get('exit_reason')}")
