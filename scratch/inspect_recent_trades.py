import json
import os

path = "/root/ZiSi-v2/data/positions_state.json"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("--- RECENT CLOSED TRADES ---")
    for i, p in enumerate(data.get("closed", [])[:20]):
        print(f"{i}: ID={p.get('order_id')} | PnL={p.get('realized_pnl')} | SLP={p.get('slp')} | EntryPrice={p.get('entry_price')} | SigPrice={p.get('signal_price')}")
else:
    print("positions_state.json not found")
