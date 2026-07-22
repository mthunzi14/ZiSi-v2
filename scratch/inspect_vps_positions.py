import json
from pathlib import Path
from datetime import datetime

pos_file = Path("data/positions_state.json")
with open(pos_file, "r") as f:
    data = json.load(f)

closed = data.get("closed", [])
print(f"Total closed trades: {len(closed)}")

# Group and print by entry_time prefix
dates = {}
for p in closed:
    et = p.get("entry_time") or p.get("timestamp") or ""
    day = et[:10] if et else "N/A"
    dates[day] = dates.get(day, 0) + 1

print("\n--- Trades count by day ---")
for k in sorted(dates.keys()):
    print(f"  {k}: {dates[k]} trades")

# Print details of the 10 most recent trades based on parseable dates
def parse_date(p):
    et = p.get("entry_time") or p.get("timestamp") or ""
    try:
        if "T" in et:
            return datetime.fromisoformat(et.replace("Z", "+00:00"))
    except:
        pass
    return datetime.min

recent_trades = sorted(closed, key=parse_date, reverse=True)[:15]
print("\n--- 15 LATEST TRADES BY DATE ---")
for p in recent_trades:
    title = p.get("event_title") or p.get("event_id")
    pnl = p.get("realized_pnl", 0.0)
    et = p.get("entry_time") or p.get("timestamp") or "N/A"
    print(f"Time: {et} | Title: {title} | PnL: ${pnl:.2f}")
