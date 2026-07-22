import json
from pathlib import Path

pos_file = Path("data/positions_state.json")
with open(pos_file, "r") as f:
    data = json.load(f)

closed = data.get("closed", [])
print(f"Total closed trades: {len(closed)}")
for idx, p in enumerate(closed):
    title = p.get("event_title")
    tranche = p.get("tranche")
    size = p.get("size")
    direction = p.get("direction")
    entry = p.get("entry_price")
    exit_p = p.get("exit_price")
    pnl = p.get("realized_pnl")
    reason = p.get("exit_reason")
    time = p.get("entry_time") or p.get("timestamp") or "N/A"
    print(f"{idx+1}. Time: {time} | {title} | Tranche: {tranche} | Size: {size} | Dir: {direction} | Entry: {entry} | Exit: {exit_p} | PnL: ${pnl} | Reason: {reason}")
