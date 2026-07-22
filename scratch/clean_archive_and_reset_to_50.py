import json
import shutil
from datetime import datetime
from pathlib import Path

# Paths
DATA_DIR = Path("/root/ZiSi-v2/data")
if not DATA_DIR.exists():
    DATA_DIR = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data")

BACKUP_DIR = DATA_DIR.parent / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
archive_prefix = f"archive_session_best_3205usd_{timestamp}"

print(f"--- Archiving Current $3,205 session data to {BACKUP_DIR} ---")

# 1. Files to archive (copy to backups/)
files_to_archive = [
    "positions_state.json",
    "account_state.json",
    "antifragile_state.json",
    "balance_history.jsonl",
    "entry_logs.json",
    "gate_log.jsonl",
    "order_placements.jsonl",
    "fair_value_trades.jsonl",
    "slippage_log.jsonl",
    "pos2.json",
    "pos_snapshot.json"
]

for filename in files_to_archive:
    src = DATA_DIR / filename
    if src.exists():
        dest = BACKUP_DIR / f"{archive_prefix}_{filename}"
        shutil.copy2(src, dest)
        print(f"Archived: {filename} -> {dest.name}")

# 2. Reset account_state.json
new_account_state = {
    "balance": 50.0,
    "starting_balance": 50.0,
    "last_updated": datetime.utcnow().isoformat() + "Z",
    "trades_executed": 0,
    "phase": "phase_1",
    "paused": False,
    "status": "running",
    "pnl": 0.0,
    "total_pnl": 0.0,
    "last_change_reason": "clean-session-reset-50usd",
    "gas_balance": 5.0,
    "realized_pnl": 0.0
}
with open(DATA_DIR / "account_state.json", "w", encoding="utf-8") as f:
    json.dump(new_account_state, f, indent=2)

# 3. Reset positions_state.json
new_positions_state = {
    "open": [],
    "closed": [],
    "summary": {
        "total_closed_trades": 0,
        "win_count": 0,
        "loss_count": 0,
        "breakeven_count": 0,
        "realized_pnl": 0.0
    }
}
with open(DATA_DIR / "positions_state.json", "w", encoding="utf-8") as f:
    json.dump(new_positions_state, f, indent=2)

# 4. Reset antifragile_state.json
new_antifragile_state = {
    "aggression": 1.0,
    "tier": "NORMAL",
    "in_recovery": False,
    "consecutive_wins": 0,
    "consecutive_losses": 0,
    "peak_portfolio": 50.0,
    "current_portfolio": 50.0,
    "trade_history": [],
    "last_updated": 0.0
}
with open(DATA_DIR / "antifragile_state.json", "w", encoding="utf-8") as f:
    json.dump(new_antifragile_state, f, indent=2)

# 5. Reset auxiliary position state files
for aux in ["pos2.json", "pos_snapshot.json"]:
    with open(DATA_DIR / aux, "w", encoding="utf-8") as f:
        json.dump({"open": [], "closed": []}, f, indent=2)

# 6. Reset balance history
with open(DATA_DIR / "balance_history.jsonl", "w", encoding="utf-8") as f:
    f.write(json.dumps({"timestamp": datetime.utcnow().isoformat() + "Z", "balance": 50.0, "realized_pnl": 0.0}) + "\n")

# 7. Clear log / tracking state files cleanly
for log_file in ["entry_logs.json"]:
    with open(DATA_DIR / log_file, "w", encoding="utf-8") as f:
        json.dump({}, f)

for jsonl_file in ["gate_log.jsonl", "order_placements.jsonl", "fair_value_trades.jsonl", "slippage_log.jsonl"]:
    with open(DATA_DIR / jsonl_file, "w", encoding="utf-8") as f:
        f.write("")

print("\n--- RESET COMPLETE ---")
print("Account Balance: $50.00 USDC")
print("Kelly & Anti-Fragile Systems: Reset to Initial Baseline")
print("Position Databases & Logs: Initialized Clean")
