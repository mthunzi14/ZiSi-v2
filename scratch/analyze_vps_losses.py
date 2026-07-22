import json
from pathlib import Path

pos_file = Path("data/positions_state.json")
with open(pos_file, "r") as f:
    data = json.load(f)

closed = data.get("closed", [])
july22_trades = [p for p in closed if (p.get("entry_time") or p.get("timestamp") or "").startswith("2026-07-22")]

wins = [p for p in july22_trades if p.get("realized_pnl", 0.0) > 0.01]
losses = [p for p in july22_trades if p.get("realized_pnl", 0.0) < -0.01]
breakevens = [p for p in july22_trades if -0.01 <= p.get("realized_pnl", 0.0) <= 0.01]

print(f"July 22 Summary:")
print(f"  Total Trades: {len(july22_trades)}")
print(f"  Wins: {len(wins)}")
print(f"  Losses: {len(losses)}")
print(f"  Breakevens: {len(breakevens)}")
print(f"  Win Rate (excl. BE): {round((len(wins)/(len(wins)+len(losses)))*100, 2) if len(wins)+len(losses)>0 else 0}%")

print("\n--- ALL LOSSES ON JULY 22 ---")
for pos in losses:
    title = pos.get("event_title") or pos.get("event_id")
    pnl = pos.get("realized_pnl", 0.0)
    et = pos.get("entry_time") or pos.get("timestamp") or "N/A"
    direction = pos.get("direction")
    entry = pos.get("entry_price")
    exit_p = pos.get("exit_price")
    print(f"Time: {et} | Title: {title} | Dir: {direction} | Entry: {entry} | Exit: {exit_p} | PnL: ${pnl:.2f}")
