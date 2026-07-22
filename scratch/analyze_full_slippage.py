import json
from pathlib import Path
from collections import defaultdict

POSITIONS_PATH = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json")

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

closed = data.get("closed", [])
print(f"Total closed trades loaded: {len(closed)}")

buckets = {
    "0 to 5¢": {"min": 0.0, "max": 5.0, "trades": [], "wins": 0, "losses": 0, "pushes": 0, "pnl": 0.0},
    "5 to 10¢": {"min": 5.0, "max": 10.0, "trades": [], "wins": 0, "losses": 0, "pushes": 0, "pnl": 0.0},
    "10 to 15¢": {"min": 10.0, "max": 15.0, "trades": [], "wins": 0, "losses": 0, "pushes": 0, "pnl": 0.0},
    "15 to 20¢": {"min": 15.0, "max": 20.0, "trades": [], "wins": 0, "losses": 0, "pushes": 0, "pnl": 0.0},
    "20 to 25¢": {"min": 20.0, "max": 25.0, "trades": [], "wins": 0, "losses": 0, "pushes": 0, "pnl": 0.0},
    "> 25¢": {"min": 25.0, "max": 999.0, "trades": [], "wins": 0, "losses": 0, "pushes": 0, "pnl": 0.0},
}

for pos in closed:
    # Get slippage in cents. If slp field is missing or 0, fallback to 0.0
    raw_slp = pos.get("slp")
    if raw_slp is None:
        raw_slp = pos.get("slippage", 0.0)
    
    slp_cents = abs(float(raw_slp or 0.0))
    pnl = float(pos.get("realized_pnl", 0.0))
    
    is_win = pnl > 0.01
    is_loss = pnl < -0.01
    is_push = not is_win and not is_loss

    # Categorize into bucket
    matched_bkey = "> 25¢"
    for bkey, bdata in buckets.items():
        if bkey == "> 25¢":
            continue
        if bdata["min"] <= slp_cents < bdata["max"]:
            matched_bkey = bkey
            break

    b = buckets[matched_bkey]
    b["trades"].append(pos)
    if is_win:
        b["wins"] += 1
    elif is_loss:
        b["losses"] += 1
    else:
        b["pushes"] += 1
    b["pnl"] += pnl

print("=" * 80)
print(f"{'SLIPPAGE BUCKET':<15} | {'TRADES':<8} | {'WINS':<6} | {'LOSSES':<6} | {'PUSH':<5} | {'WIN RATE':<9} | {'TOTAL PNL ($)':<14} | {'AVG PNL ($)':<12}")
print("-" * 80)

total_trades_count = 0
total_pnl_all = 0.0

for bkey, bdata in buckets.items():
    count = len(bdata["trades"])
    total_trades_count += count
    total_pnl_all += bdata["pnl"]
    wins = bdata["wins"]
    losses = bdata["losses"]
    decided = wins + losses
    win_rate = (wins / decided * 100) if decided > 0 else 0.0
    avg_pnl = (bdata["pnl"] / count) if count > 0 else 0.0
    
    print(f"{bkey:<15} | {count:<8} | {wins:<6} | {losses:<6} | {bdata['pushes']:<5} | {win_rate:6.1f}%   | ${bdata['pnl']:+12.2f} | ${avg_pnl:+10.2f}")

print("=" * 80)
print(f"{'TOTAL':<15} | {total_trades_count:<8} | {'-':<6} | {'-':<6} | {'-':<5} | {'-':<9} | ${total_pnl_all:+12.2f} |")
