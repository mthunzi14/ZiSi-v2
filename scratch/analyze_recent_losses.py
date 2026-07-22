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

if not closed:
    print("No closed positions found.")
    exit(0)

# Sort by timestamp/close time if possible, otherwise keep original order (newest is last in JSON)
recent = closed[-15:]
print("\n--- LAST 15 CLOSED TRADES ---")
for pos in reversed(recent):
    title = pos.get("event_title", "UNKNOWN")
    direction = pos.get("direction", "N/A")
    spent = pos.get("amount_spent", 0.0)
    shares = pos.get("shares_acquired", 0.0)
    entry = pos.get("entry_price", 0.0)
    exit_p = pos.get("exit_price", 0.0)
    pnl = pos.get("realized_pnl", 0.0)
    slp = pos.get("slp", 0.0)
    regime = pos.get("regime", "UNKNOWN")
    timestamp = pos.get("timestamp", "N/A")
    status = pos.get("status", "N/A")
    print(f"Title: {title} | Dir: {direction} | Entry: {entry} | Exit: {exit_p} | PnL: ${pnl:.2f} | Slp: {slp}% | Regime: {regime} | Status: {status}")
