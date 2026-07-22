import json
from collections import defaultdict
from datetime import datetime

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

try:
    with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

closed = data.get("closed", [])
print(f"Analyzing {len(closed)} closed positions...")

# Filter trades closed on July 19 (today)
today_trades = []
for p in closed:
    exit_time_str = p.get("exit_time") or p.get("close_time") or ""
    if "2026-07-19" in exit_time_str:
        today_trades.append(p)

print(f"Found {len(today_trades)} trades closed today (July 19).")

win_slippages = []
loss_slippages = []

for p in today_trades:
    # Slippage value: check "slippage_cents" or "slp"
    # Wait, let's see how slippage is stored in each position
    slp = p.get("slp") or p.get("slippage_cents") or p.get("slippage")
    if slp is None:
        # Check tranches
        tranches = p.get("tranches", {})
        # If not, let's look at entry_price vs signal_price if available
        entry_p = p.get("entry_price")
        sig_p = p.get("signal_price")
        if entry_p is not None and sig_p is not None:
            slp = (entry_p - sig_p) * 100 # slippage in cents
            
    if slp is not None:
        try:
            slp_val = float(slp)
            pnl = p.get("realized_pnl", 0.0)
            if pnl > 0.01:
                win_slippages.append(slp_val)
            elif pnl < -0.01:
                loss_slippages.append(slp_val)
        except Exception:
            pass

print(f"Trades with parsed slippage: wins={len(win_slippages)}, losses={len(loss_slippages)}")
if win_slippages:
    print(f"Average entry slippage for WINS: {sum(win_slippages)/len(win_slippages):.2f}¢")
if loss_slippages:
    print(f"Average entry slippage for LOSSES: {sum(loss_slippages)/len(loss_slippages):.2f}¢")

# Let's inspect some of the specific large losses closed today to check their entry prices and slippages
print("\n--- Breakdown of Large Expiry Losses Today ---")
for p in today_trades:
    pnl = p.get("realized_pnl", 0.0)
    if pnl < -20.0 and "expired" in p.get("exit_reason", "").lower():
        title = p.get("event_title")
        entry_p = p.get("entry_price")
        exit_p = p.get("exit_price")
        entry_spot = p.get("entry_spot")
        exit_reason = p.get("exit_reason")
        print(f"Title: {title}")
        print(f"  PnL: {pnl:.2f} USD | Entry Price: {entry_p:.3f} | Exit Price: {exit_p:.3f}")
        print(f"  Entry Spot: {entry_spot} | Reason: {exit_reason}")
