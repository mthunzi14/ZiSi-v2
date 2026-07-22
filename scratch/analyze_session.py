import json
import re

json_path = r"c:\Users\mthun\Downloads\ZiSi-v2\backups\archive_session_best_3205usd_20260719_201044_positions_state.json"
account_path = r"c:\Users\mthun\Downloads\ZiSi-v2\backups\archive_session_best_3205usd_20260719_201044_account_state.json"

with open(json_path, 'r') as f:
    data = json.load(f)

with open(account_path, 'r') as f:
    account_data = json.load(f)

closed = data.get("closed", [])
summary = data.get("summary", {})

asset_stats = {}
regime_stats = {}
tranche_stats = {}
direction_stats = {}

wins = 0
losses = 0
breakevens = 0
total_pnl = 0.0

for p in closed:
    pnl = p.get("realized_pnl", 0.0)
    title = p.get("event_title", "")
    regime = p.get("regime", "UNKNOWN")
    tranche = p.get("tranche", "UNKNOWN")
    direction = p.get("direction", "UNKNOWN")
    
    brackets = re.findall(r"\[([A-Z0-9]+)\]", title)
    asset = "UNKNOWN"
    for b in brackets:
        if b in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE"]:
            asset = b
            break
    
    total_pnl += pnl
    
    # Asset
    if asset not in asset_stats:
        asset_stats[asset] = {"wins": 0, "losses": 0, "be": 0, "pnl": 0.0, "count": 0}
    asset_stats[asset]["count"] += 1
    asset_stats[asset]["pnl"] += pnl

    # Regime
    if regime not in regime_stats:
        regime_stats[regime] = {"wins": 0, "losses": 0, "be": 0, "pnl": 0.0, "count": 0}
    regime_stats[regime]["count"] += 1
    regime_stats[regime]["pnl"] += pnl

    # Tranche
    if tranche not in tranche_stats:
        tranche_stats[tranche] = {"wins": 0, "losses": 0, "be": 0, "pnl": 0.0, "count": 0}
    tranche_stats[tranche]["count"] += 1
    tranche_stats[tranche]["pnl"] += pnl

    # Direction
    if direction not in direction_stats:
        direction_stats[direction] = {"wins": 0, "losses": 0, "be": 0, "pnl": 0.0, "count": 0}
    direction_stats[direction]["count"] += 1
    direction_stats[direction]["pnl"] += pnl
    
    if pnl > 0.001:
        wins += 1
        asset_stats[asset]["wins"] += 1
        regime_stats[regime]["wins"] += 1
        tranche_stats[tranche]["wins"] += 1
        direction_stats[direction]["wins"] += 1
    elif pnl < -0.001:
        losses += 1
        asset_stats[asset]["losses"] += 1
        regime_stats[regime]["losses"] += 1
        tranche_stats[tranche]["losses"] += 1
        direction_stats[direction]["losses"] += 1
    else:
        breakevens += 1
        asset_stats[asset]["be"] += 1
        regime_stats[regime]["be"] += 1
        tranche_stats[tranche]["be"] += 1
        direction_stats[direction]["be"] += 1

print("==========================================================================")
print("              ZISI-V2 ARCHIVED BEST SESSION (3.2K USD) DEEP AUDIT         ")
print("==========================================================================")
print(f"Account Balance (Archived): ${account_data.get('balance', 0.0):,.2f}")
print(f"Starting Balance:          ${account_data.get('starting_balance', 0.0):,.2f}")
print(f"Summary Realized PnL:      ${summary.get('realized_pnl', 0.0):,.2f}")
print(f"Calculated Sum of PnL:     ${total_pnl:,.2f}")
print(f"Total Tranche Positions:   {len(closed)}")
print(f"Wins:                      {wins}")
print(f"Losses:                    {losses}")
print(f"Breakevens:                {breakevens}")
wr_excl = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
wr_incl = (wins / len(closed) * 100) if len(closed) > 0 else 0
print(f"Overall Win Rate (excl BE): {wr_excl:.2f}%")
print(f"Overall Win Rate (incl BE): {wr_incl:.2f}%")

print("\n--------------------------------------------------------------------------")
print("                          ASSET BREAKDOWN                                 ")
print("--------------------------------------------------------------------------")
print(f"{'Asset':<8} | {'Trades':<8} | {'Wins':<6} | {'Losses':<6} | {'BE':<4} | {'WR (excl BE)':<12} | {'PnL ($)':<12}")
print("-" * 74)
for k in sorted(asset_stats.keys()):
    v = asset_stats[k]
    w, l, b = v["wins"], v["losses"], v["be"]
    wr = (w / (w + l) * 100) if (w + l) > 0 else 0
    print(f"{k:<8} | {v['count']:<8} | {w:<6} | {l:<6} | {b:<4} | {wr:11.2f}% | ${v['pnl']:11.2f}")

print("\n--------------------------------------------------------------------------")
print("                         REGIME BREAKDOWN                                 ")
print("--------------------------------------------------------------------------")
print(f"{'Regime':<18} | {'Trades':<8} | {'Wins':<6} | {'Losses':<6} | {'BE':<4} | {'WR (excl BE)':<12} | {'PnL ($)':<12}")
print("-" * 80)
for k in sorted(regime_stats.keys()):
    v = regime_stats[k]
    w, l, b = v["wins"], v["losses"], v["be"]
    wr = (w / (w + l) * 100) if (w + l) > 0 else 0
    print(f"{k:<18} | {v['count']:<8} | {w:<6} | {l:<6} | {b:<4} | {wr:11.2f}% | ${v['pnl']:11.2f}")

print("\n--------------------------------------------------------------------------")
print("                         TRANCHE BREAKDOWN                                ")
print("--------------------------------------------------------------------------")
for k in sorted(tranche_stats.keys()):
    v = tranche_stats[k]
    w, l, b = v["wins"], v["losses"], v["be"]
    wr = (w / (w + l) * 100) if (w + l) > 0 else 0
    print(f"Tranche {k:<2} | Trades: {v['count']:<5} | W: {w:<5} | L: {l:<4} | BE: {b:<3} | WR: {wr:.2f}% | PnL: ${v['pnl']:,.2f}")

print("==========================================================================")
