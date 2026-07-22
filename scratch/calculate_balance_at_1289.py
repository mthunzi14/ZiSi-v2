import json
from datetime import datetime

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
closed = data.get("closed", [])

def get_exit_time(pos):
    exit_time_str = pos.get("exit_time") or pos.get("close_time") or ""
    if exit_time_str:
        try:
            return datetime.fromisoformat(exit_time_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.min
    return datetime.min

closed.sort(key=get_exit_time)

pnl_sum_1289 = sum(trade.get("realized_pnl", 0.0) for trade in closed[1226:1289])
pnl_sum_1311 = sum(trade.get("realized_pnl", 0.0) for trade in closed[1226:1311])

print(f"Balance at trade 1289 (1744.0 + PnL sum): {1744.0 + pnl_sum_1289:.2f} USD")
print(f"Balance at trade 1311 (1744.0 + PnL sum): {1744.0 + pnl_sum_1311:.2f} USD")
