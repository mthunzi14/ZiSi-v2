import json
from pathlib import Path

pos_file = Path("data/positions_state.json")
if not pos_file.exists():
    print("No positions_state.json file found locally.")
    exit(0)

try:
    with open(pos_file, "r") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(0)

closed = data.get("closed", [])
print(f"Total Closed Positions: {len(closed)}")

# Let's print the actual last 30 entries as appended to closed
recent = closed[-30:]
print("\n--- ACTUAL LAST 30 CLOSED TRADES IN DATABASE ---")
for idx, pos in enumerate(reversed(recent)):
    title = pos.get("event_title", "UNKNOWN")
    direction = pos.get("direction", "N/A")
    spent = pos.get("amount_spent", 0.0)
    entry = pos.get("entry_price", 0.0)
    exit_p = pos.get("exit_price", 0.0)
    pnl = pos.get("realized_pnl", 0.0)
    regime = pos.get("regime", "UNKNOWN")
    ts = pos.get("timestamp") or pos.get("open_time") or "N/A"
    print(f"[Index -{idx}] Time: {ts} | Title: {title} | Dir: {direction} | Entry: {entry} | Exit: {exit_p} | PnL: ${pnl:.2f} | Regime: {regime}")
