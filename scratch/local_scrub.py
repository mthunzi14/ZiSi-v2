import json
import os

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"
ACCOUNT_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\account_state.json"
ANTIFRAGILE_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\antifragile_state.json"

# 1. Scrub positions_state.json
try:
    with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
        pos_data = json.load(f)
except Exception as e:
    print(f"Error loading positions_state.json: {e}")
    exit(1)

closed = pos_data.get("closed", [])
print(f"Original closed positions count: {len(closed)}")

# Keep only the first 1311 closed positions
closed_scrubbed = closed[:1311]
pos_data["closed"] = closed_scrubbed
pos_data["active"] = [] # make sure active is empty
pos_data["last_updated"] = "2026-07-19T17:34:00+00:00"

with open(POSITIONS_PATH, "w", encoding="utf-8") as f:
    json.dump(pos_data, f, indent=2)
print(f"Scrubbed positions_state.json. New count: {len(closed_scrubbed)}")

# 2. Update account_state.json
try:
    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        acc_data = json.load(f)
except Exception as e:
    print(f"Error loading account_state.json: {e}")
    exit(1)

acc_data["balance"] = 3443.43
acc_data["pnl"] = 3393.43
acc_data["trades_executed"] = 1311
acc_data["last_updated"] = "2026-07-19T17:34:00Z"
acc_data["last_change_reason"] = "scrubbed-revert"

with open(ACCOUNT_PATH, "w", encoding="utf-8") as f:
    json.dump(acc_data, f, indent=2)
print("Updated account_state.json balance to 3443.43 and trades to 1311.")

# 3. Reset antifragile_state.json
try:
    with open(ANTIFRAGILE_PATH, "r", encoding="utf-8") as f:
        af_data = json.load(f)
except Exception as e:
    af_data = {}

af_data["aggression"] = 1.0
af_data["tier"] = "NORMAL"
af_data["in_recovery"] = False
af_data["consecutive_wins"] = 0
af_data["consecutive_losses"] = 0
af_data["peak_portfolio"] = 3443.43
af_data["current_portfolio"] = 3443.43
af_data["trade_history"] = []
af_data["last_updated"] = 0.0

with open(ANTIFRAGILE_PATH, "w", encoding="utf-8") as f:
    json.dump(af_data, f, indent=2)
print("Reset antifragile_state.json to Normal.")
