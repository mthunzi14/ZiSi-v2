import glob
import json
import os
import re
from collections import defaultdict

def parse_event_title(title):
    ma = re.search(r"\[(BTC|ETH|SOL|XRP|DOGE)\]", title or "")
    mt = re.search(r"\[(5m|15m|1h)\]", title or "")
    asset = ma.group(1) if ma else "UNKNOWN"
    tf = mt.group(1) if mt else "5m"
    return asset, tf

def main():
    pattern = "/root/ZiSi-v2/**/positions_state.json"
    files = glob.glob(pattern, recursive=True)
    
    all_trades = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            closed = data.get("closed", [])
            for t in closed:
                typ = t.get("type", t.get("entry_type", "UNKNOWN"))
                if typ in ("SIG", "SIGNAL"):
                    t["source_file"] = os.path.basename(os.path.dirname(os.path.dirname(f)))
                    all_trades.append(t)
        except Exception as e:
            pass
            
    print(f"Loaded {len(all_trades)} closed SIG/SIGNAL paper trades from all archived state files.")
    if not all_trades:
        return
        
    total_trades = len(all_trades)
    wins = sum(1 for t in all_trades if float(t.get("realized_pnl", 0.0)) > 0)
    losses = sum(1 for t in all_trades if float(t.get("realized_pnl", 0.0)) < 0)
    flats = sum(1 for t in all_trades if float(t.get("realized_pnl", 0.0)) == 0)
    win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0.0
    total_pnl = sum(float(t.get("realized_pnl", 0.0)) for t in all_trades)
    
    print(f"\n==========================================")
    print(f"  BOT'S OWN HISTORICAL SIG STRATEGY AUDIT")
    print(f"==========================================")
    print(f"Total Closed SIG Trades: {total_trades}")
    print(f"Wins: {wins} | Losses: {losses} | Flats: {flats}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Net PnL: ${total_pnl:,.2f} USDC")
    
    # 1. Asset Breakdown
    print("\n1. Asset Breakdown:")
    asset_groups = defaultdict(list)
    for t in all_trades:
        asset, tf = parse_event_title(t.get("event_title", ""))
        asset_groups[asset].append(t)
    for asset, group in sorted(asset_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(float(x.get("realized_pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if float(x.get("realized_pnl", 0.0)) > 0)
        a_losses = sum(1 for x in group if float(x.get("realized_pnl", 0.0)) < 0)
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        print(f"  {asset:7}: {len(group):3} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # 2. Timeframe Breakdown
    print("\n2. Timeframe Breakdown:")
    tf_groups = defaultdict(list)
    for t in all_trades:
        asset, tf = parse_event_title(t.get("event_title", ""))
        tf_groups[tf].append(t)
    for tf, group in sorted(tf_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(float(x.get("realized_pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if float(x.get("realized_pnl", 0.0)) > 0)
        a_losses = sum(1 for x in group if float(x.get("realized_pnl", 0.0)) < 0)
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        print(f"  {tf:7}: {len(group):3} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # 3. Price Band Performance
    print("\n3. Price Band Performance:")
    price_groups = defaultdict(list)
    for t in all_trades:
        price = float(t.get("entry_price", 0.50))
        if price < 0.30:
            price_groups["< 30c (Low)        "].append(t)
        elif 0.30 <= price < 0.50:
            price_groups["30c - 50c (Mid-Low)"].append(t)
        elif 0.50 <= price < 0.70:
            price_groups["50c - 70c (Mid-High)"].append(t)
        elif 0.70 <= price < 0.85:
            price_groups["70c - 85c (High)   "].append(t)
        else:
            price_groups[">= 85c (Certainty) "].append(t)
            
    for band, group in sorted(price_groups.items()):
        a_pnl = sum(float(x.get("realized_pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if float(x.get("realized_pnl", 0.0)) > 0)
        a_losses = sum(1 for x in group if float(x.get("realized_pnl", 0.0)) < 0)
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        print(f"  {band}: {len(group):3} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # 4. Exit reasons
    print("\n4. Exit Reasons:")
    exit_groups = defaultdict(list)
    for t in all_trades:
        reason = t.get("exit_reason", "UNKNOWN")
        exit_groups[reason].append(t)
    for reason, group in sorted(exit_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {reason:20}: {len(group):3} trades")

if __name__ == '__main__':
    main()
