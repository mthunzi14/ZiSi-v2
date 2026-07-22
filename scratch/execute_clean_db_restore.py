import json
import os

CURRENT_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"
BACKUP_PATH = r"c:\Users\mthun\.gemini\antigravity\brain\14e04d67-5e69-491a-9086-7b2c06bc7b3d\backups\positions_state.json"
ACCOUNT_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\account_state.json"
ANTIFRAGILE_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\antifragile_state.json"

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
clean_closed = [p for p in full_closed if not ("2026-07-19T15:40" <= p.get("entry_time", "") <= "2026-07-19T17:00")]

# Recalculate summary metrics
wins = sum(1 for p in clean_closed if p.get('realized_pnl', 0.0) > 0.01)
losses = sum(1 for p in clean_closed if p.get('realized_pnl', 0.0) < -0.01)
breakeven = len(clean_closed) - wins - losses
tot_realized_pnl = round(sum(p.get('realized_pnl', 0.0) for p in clean_closed), 2)
new_balance = round(50.0 + tot_realized_pnl, 2)

# Update positions_state.json
curr_data["closed"] = clean_closed
curr_data["active"] = []
curr_data["summary"] = {
    "active_count": 0,
    "poly_active": 0,
    "closed_count": len(clean_closed),
    "unrealized_pnl": 0.0,
    "realized_pnl": tot_realized_pnl,
    "win_count": wins,
    "loss_count": losses,
    "breakeven_count": breakeven
}
curr_data["last_updated"] = "2026-07-19T19:00:00+00:00"

with open(CURRENT_PATH, "w", encoding="utf-8") as f:
    json.dump(curr_data, f, indent=2)

print(f"Updated positions_state.json: {len(clean_closed)} trades, ${tot_realized_pnl:.2f} PnL")

# Update account_state.json
try:
    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        acc_data = json.load(f)
except Exception:
    acc_data = {}

acc_data["balance"] = new_balance
acc_data["starting_balance"] = 50.0
acc_data["pnl"] = tot_realized_pnl
acc_data["trades_executed"] = len(clean_closed)
acc_data["last_updated"] = "2026-07-19T19:00:00Z"
acc_data["last_change_reason"] = "clean-reconciled-restore"

with open(ACCOUNT_PATH, "w", encoding="utf-8") as f:
    json.dump(acc_data, f, indent=2)

print(f"Updated account_state.json: ${new_balance:.2f} balance")

# Update antifragile_state.json
try:
    with open(ANTIFRAGILE_PATH, "r", encoding="utf-8") as f:
        af_data = json.load(f)
except Exception:
    af_data = {}

af_data["aggression"] = 1.0
af_data["tier"] = "NORMAL"
af_data["in_recovery"] = False
af_data["consecutive_wins"] = 0
af_data["consecutive_losses"] = 0
af_data["peak_portfolio"] = new_balance
af_data["current_portfolio"] = new_balance
af_data["trade_history"] = []
af_data["last_updated"] = 0.0

with open(ANTIFRAGILE_PATH, "w", encoding="utf-8") as f:
    json.dump(af_data, f, indent=2)

print(f"Updated antifragile_state.json to NORMAL with ${new_balance:.2f} balance")
