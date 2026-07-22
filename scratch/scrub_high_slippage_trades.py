import json
from pathlib import Path

POSITIONS_PATH = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json")
ACCOUNT_PATH = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data\account_state.json")

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    pos_data = json.load(f)

with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
    acc_data = json.load(f)

closed = pos_data.get("closed", [])
orig_count = len(closed)

MAX_SLIPPAGE_CENTS = 8.0

kept_trades = []
removed_trades = []

for trade in closed:
    raw_slp = trade.get("slp")
    if raw_slp is None:
        raw_slp = trade.get("slippage", 0.0)
    slp_cents = abs(float(raw_slp or 0.0))
    
    if slp_cents > MAX_SLIPPAGE_CENTS:
        removed_trades.append((trade, slp_cents))
    else:
        kept_trades.append(trade)

print(f"Original closed trades count: {orig_count}")
print(f"Removed trades count (> {MAX_SLIPPAGE_CENTS}¢): {len(removed_trades)}")
print(f"Kept trades count (<= {MAX_SLIPPAGE_CENTS}¢): {len(kept_trades)}")

if removed_trades:
    print("\n--- Removed Trades Details ---")
    for t, slp in removed_trades:
        print(f"ID: {t.get('order_id')} | Asset/TF: {t.get('asset')} {t.get('timeframe')} | SLP: {slp:.1f}¢ | PnL: ${float(t.get('realized_pnl', 0.0)):+.2f} | Reason: {t.get('exit_reason')}")

# Recalculate summary metrics
new_wins = sum(1 for t in kept_trades if float(t.get("realized_pnl", 0.0)) > 0.01)
new_losses = sum(1 for t in kept_trades if float(t.get("realized_pnl", 0.0)) < -0.01)
new_breakevens = sum(1 for t in kept_trades if -0.01 <= float(t.get("realized_pnl", 0.0)) <= 0.01)
new_realized = sum(float(t.get("realized_pnl", 0.0)) for t in kept_trades)

start_bal = float(acc_data.get("starting_balance", 50.00))
new_balance = round(start_bal + new_realized, 2)

decided = new_wins + new_losses
new_win_rate = (new_wins / decided * 100) if decided > 0 else 0.0

print("\n--- Recalculated Summary ---")
print(f"Wins: {new_wins} | Losses: {new_losses} | Pushes: {new_breakevens}")
print(f"New Win Rate: {new_win_rate:.2f}%")
print(f"New Realized PnL: ${new_realized:+.2f}")
print(f"New Account Balance: ${new_balance:,.2f}")
