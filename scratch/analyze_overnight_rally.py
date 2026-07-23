import json
from pathlib import Path

pos_file = Path("data/positions_state.json")
acc_file = Path("data/account_state.json")

with open(pos_file, "r") as f:
    pos_data = json.load(f)

with open(acc_file, "r") as f:
    acc_data = json.load(f)

closed = pos_data.get("closed", [])

wins = [p for p in closed if p.get("realized_pnl", 0.0) > 0.01]
losses = [p for p in closed if p.get("realized_pnl", 0.0) < -0.01]
breakevens = [p for p in closed if -0.01 <= p.get("realized_pnl", 0.0) <= 0.01]

total = len(wins) + len(losses)
wr = (len(wins) / total * 100) if total > 0 else 0.0

current_balance = acc_data.get("balance", 0.0)
starting_balance = acc_data.get("starting_balance", 30.0)
net_pnl = current_balance - starting_balance
roi = (net_pnl / starting_balance * 100) if starting_balance > 0 else 0.0

print(f"================ OVERNIGHT RALLY SUMMARY ================")
print(f"Current Balance: ${current_balance:.2f} USDC")
print(f"Starting Balance: ${starting_balance:.2f} USDC")
print(f"Net PnL: ${net_pnl:+.2f} USDC (+{roi:.2f}%)")
print(f"Total Closed Trades: {len(closed)}")
print(f"Wins: {len(wins)} | Losses: {len(losses)} | Breakevens: {len(breakevens)}")
print(f"Win Rate (excl BE): {wr:.2f}%")
print(f"========================================================\n")

# Group by Asset
asset_stats = {}
for p in closed:
    title = p.get("event_title", "")
    asset = "OTHER"
    for a in ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "HYPE"]:
        if f"[{a}]" in title:
            asset = a
            break
    
    if asset not in asset_stats:
        asset_stats[asset] = {"wins": 0, "losses": 0, "pnl": 0.0}
    
    pnl = p.get("realized_pnl", 0.0)
    asset_stats[asset]["pnl"] += pnl
    if pnl > 0.01:
        asset_stats[asset]["wins"] += 1
    elif pnl < -0.01:
        asset_stats[asset]["losses"] += 1

print("--- PERFORMANCE BY ASSET ---")
for asset, stats in sorted(asset_stats.items(), key=lambda x: x[1]["pnl"], reverse=True):
    tot = stats["wins"] + stats["losses"]
    asset_wr = (stats["wins"] / tot * 100) if tot > 0 else 0.0
    print(f"Asset: {asset:<6} | Wins: {stats['wins']:<3} | Losses: {stats['losses']:<3} | Win Rate: {asset_wr:6.2f}% | PnL: ${stats['pnl']:+8.2f}")

print("\n--- LATEST 10 CLOSED TRADES (MOST RECENT FIRST) ---")
sorted_closed = sorted(closed, key=lambda x: x.get("entry_time") or x.get("timestamp") or "", reverse=True)
for p in sorted_closed[:10]:
    title = p.get("event_title")
    tranche = p.get("tranche")
    size = p.get("size")
    direction = p.get("direction")
    entry = p.get("entry_price")
    exit_p = p.get("exit_price")
    pnl = p.get("realized_pnl")
    time = p.get("entry_time") or p.get("timestamp") or "N/A"
    print(f"Time: {time} | {title} | {tranche} | ${size} | {direction} | Entry: {entry} | Exit: {exit_p} | PnL: ${pnl:+.2f}")
