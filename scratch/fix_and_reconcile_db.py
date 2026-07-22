import json

CURRENT_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"
BACKUP_PATH = r"c:\Users\mthun\.gemini/antigravity/brain/14e04d67-5e69-491a-9086-7b2c06bc7b3d/backups/positions_state.json"

with open(CURRENT_PATH, "r", encoding="utf-8") as f:
    curr_data = json.load(f)
with open(BACKUP_PATH, "r", encoding="utf-8") as f:
    back_data = json.load(f)

curr_closed = curr_data.get("closed", [])
back_closed = back_data.get("closed", [])

curr_keys = { (p['entry_time'], p.get('event_title', '')) for p in curr_closed }
missing_old_trades = [p for p in back_closed if (p['entry_time'], p.get('event_title', '')) not in curr_keys]

# Combine current closed + missing oldest trades
full_closed = curr_closed + missing_old_trades

# Filter out bad drawdown trades from Sunday afternoon (entry_time between 15:40 UTC and 17:00 UTC)
# Let's inspect trades in that window
drawdown_trades = [p for p in full_closed if "2026-07-19T15:40" <= p.get("entry_time", "") <= "2026-07-19T17:00"]
clean_closed = [p for p in full_closed if not ("2026-07-19T15:40" <= p.get("entry_time", "") <= "2026-07-19T17:00")]

print(f"Total full trades before filter: {len(full_closed)}")
print(f"Drawdown trades filtered out: {len(drawdown_trades)}")
drawdown_pnl = sum(p.get("realized_pnl", 0.0) for p in drawdown_trades)
print(f"Drawdown total PnL impact: ${drawdown_pnl:+.2f}")

# Recalculate summary metrics
wins = sum(1 for p in clean_closed if p.get('realized_pnl', 0.0) > 0.01)
losses = sum(1 for p in clean_closed if p.get('realized_pnl', 0.0) < -0.01)
breakeven = len(clean_closed) - wins - losses
tot_realized_pnl = sum(p.get('realized_pnl', 0.0) for p in clean_closed)
new_balance = round(50.0 + tot_realized_pnl, 2)
win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0.0

print("-" * 50)
print(f"Cleaned Total Trades: {len(clean_closed)}")
print(f"Cleaned Wins: {wins}, Losses: {losses}, Push: {breakeven}")
print(f"Cleaned Win Rate: {win_rate:.1f}%")
print(f"Cleaned Realized PnL: ${tot_realized_pnl:.2f}")
print(f"Cleaned Account Balance: ${new_balance:.2f}")
print("-" * 50)
