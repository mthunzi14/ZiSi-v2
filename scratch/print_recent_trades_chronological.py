import json
from pathlib import Path
from datetime import datetime

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

# Sort by timestamp (isoformat strings or timestamps)
def get_time(pos):
    ts = pos.get("timestamp") or pos.get("open_time") or ""
    try:
        # Check if float timestamp
        return float(ts)
    except ValueError:
        try:
            # Parse ISO string
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

closed_sorted = sorted(closed, key=get_time)

# Let's print the latest 20 trades
recent = closed_sorted[-20:]
print("\n--- LATEST 20 CHRONOLOGICAL CLOSED TRADES ---")
for pos in reversed(recent):
    title = pos.get("event_title", "UNKNOWN")
    direction = pos.get("direction", "N/A")
    spent = pos.get("amount_spent", 0.0)
    entry = pos.get("entry_price", 0.0)
    exit_p = pos.get("exit_price", 0.0)
    pnl = pos.get("realized_pnl", 0.0)
    regime = pos.get("regime", "UNKNOWN")
    ts = pos.get("timestamp") or "N/A"
    print(f"Time: {ts} | Title: {title} | Dir: {direction} | Entry: {entry} | Exit: {exit_p} | PnL: ${pnl:.2f} | Regime: {regime}")
