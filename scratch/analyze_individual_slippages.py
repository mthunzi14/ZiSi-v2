import json
from datetime import datetime

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

try:
    with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

closed = data.get("closed", [])

print("| Event Title | Dir | Entry Price | Signal Price | Slippage (cents) | Realized PnL |")
print("|---|---|---|---|---|---|")
for p in closed:
    exit_time_str = p.get("exit_time") or p.get("close_time") or ""
    if "2026-07-19" in exit_time_str:
        pnl = p.get("realized_pnl", 0.0)
        entry_p = p.get("entry_price")
        sig_p = p.get("signal_price")
        if entry_p is not None and sig_p is not None:
            slp = (entry_p - sig_p) * 100
            # If the trade is a loss, let's output it
            if pnl < -20.0:
                print(f"| {p.get('event_title')} | {p.get('direction')} | {entry_p:.3f} | {sig_p:.3f} | {slp:+.1f}¢ | {pnl:+.2f} USD |")
