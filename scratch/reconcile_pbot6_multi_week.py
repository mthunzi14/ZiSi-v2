import json
from collections import defaultdict
from datetime import datetime

def parse_timeframe(slug, market):
    slug_upper = slug.upper() if slug else ""
    market_upper = market.upper() if market else ""
    if "15M" in slug_upper or "15M" in market_upper:
        return "15m"
    if "1H" in slug_upper or "1H" in market_upper:
        return "1h"
    return "5m"

def parse_asset(slug, market):
    slug_upper = slug.upper() if slug else ""
    market_upper = market.upper() if market else ""
    for token in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:
        if token in slug_upper or token in market_upper:
            return token
    return "UNKNOWN"

def main():
    history_path = "/root/ZiSi-v2/wallet/wallet_0x21d0a97a_multi_week.json"
    cache_path = "/root/ZiSi-v2/wallet/resolved_winners_cache.json"
    
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            txs = json.load(f)
        with open(cache_path, "r", encoding="utf-8") as f:
            winners = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    print(f"Loaded {len(txs)} transactions and {len(winners)} resolved winners.")
    
    market_trades = defaultdict(list)
    for t in txs:
        slug = t.get("Slug")
        if not slug:
            continue
        market_trades[slug].append(t)
        
    resolved_trades = []
    unresolved_count = 0
    
    for slug, actions in market_trades.items():
        buys = [a for a in actions if a.get("Action") == "BUY"]
        if not buys:
            continue
            
        first_buy = buys[0]
        market_name = first_buy.get("Market", "")
        asset = parse_asset(slug, market_name)
        tf = parse_timeframe(slug, market_name)
        
        total_spent = sum(float(b.get("TotalUSDCSpent", 0.0)) for b in buys)
        total_shares = sum(float(b.get("TotalShares", 0.0)) for b in buys)
        avg_price = total_spent / total_shares if total_shares > 0 else 0.0
        
        direction = first_buy.get("BetOnOutcome", "Up")
        winning_outcome = winners.get(slug)
        if not winning_outcome:
            unresolved_count += 1
            continue
            
        won = False
        dir_lower = direction.lower()
        win_lower = winning_outcome.lower()
        
        if dir_lower == win_lower:
            won = True
        elif dir_lower == "up" and win_lower in ("yes", "up"):
            won = True
        elif dir_lower == "down" and win_lower in ("no", "down"):
            won = True
            
        pnl = 0.0
        if won:
            pnl = total_shares - total_spent
        else:
            pnl = -total_spent
            
        dt_str = first_buy.get("DateTime", "")
        dt = None
        if dt_str:
            try:
                dt = datetime.fromisoformat(dt_str)
            except:
                pass
                
        resolved_trades.append({
            "slug": slug,
            "market": market_name,
            "asset": asset,
            "tf": tf,
            "direction": direction,
            "total_spent": total_spent,
            "total_shares": total_shares,
            "avg_price": avg_price,
            "won": won,
            "pnl": pnl,
            "dt": dt
        })
        
    print(f"Reconstructed {len(resolved_trades)} resolved trades. Unresolved: {unresolved_count}")
    
    total_pnl = sum(r["pnl"] for r in resolved_trades)
    wins = sum(1 for r in resolved_trades if r["won"])
    total_r = len(resolved_trades)
    win_rate = (wins / total_r) * 100 if total_r > 0 else 0.0
    
    print(f"\n==========================================")
    print(f"  P-BOT 6 MULTI-WEEK GATES & PERFORMANCE RECONCILIATION")
    print(f"==========================================")
    print(f"Total Reconstructed Trades: {total_r}")
    print(f"Wins: {wins} | Losses: {total_r - wins}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Net PnL: ${total_pnl:,.2f} USDC")
    
    # 1. Asset Breakdown
    print("\n1. Asset Breakdown:")
    asset_groups = defaultdict(list)
    for r in resolved_trades:
        asset_groups[r["asset"]].append(r)
    for asset, group in sorted(asset_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        print(f"  {asset:7}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # 2. Timeframe Breakdown
    print("\n2. Timeframe Breakdown:")
    tf_groups = defaultdict(list)
    for r in resolved_trades:
        tf_groups[r["tf"]].append(r)
    for tf, group in sorted(tf_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        print(f"  {tf:7}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # 3. Price Band Performance
    print("\n3. Price Band Performance:")
    price_groups = defaultdict(list)
    for r in resolved_trades:
        price = r["avg_price"]
        if price < 0.30:
            price_groups["< 30c (Low)        "].append(r)
        elif 0.30 <= price < 0.50:
            price_groups["30c - 50c (Mid-Low)"].append(r)
        elif 0.50 <= price < 0.70:
            price_groups["50c - 70c (Mid-High)"].append(r)
        elif 0.70 <= price < 0.85:
            price_groups["70c - 85c (High)   "].append(r)
        else:
            price_groups[">= 85c (Certainty) "].append(r)
            
    for band, group in sorted(price_groups.items()):
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        print(f"  {band}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # 4. Temporal analysis (Day of Week)
    print("\n4. Day of Week Performance:")
    day_groups = defaultdict(list)
    for r in resolved_trades:
        if r["dt"]:
            day = r["dt"].strftime("%A")
            day_groups[day].append(r)
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        group = day_groups[day]
        if not group:
            continue
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        print(f"  {day:10}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:8.2f}")
        
    # Save a report to a markdown file
    report_lines = [
        f"# 📊 PBot-6 Main Historical Gates & PnL Reconciliation (Multi-Week)",
        f"**Source File:** `wallet_0x21d0a97a_multi_week.json`",
        f"**Resolved Winner Cache:** `resolved_winners_cache.json`",
        f"**Date Range:** Reconstructed from multi-week transaction logs.",
        f"",
        f"## Reconciled Summary Metrics",
        f"- **Total Resolved Trades:** {total_r}",
        f"- **Wins / Losses:** {wins}W / {total_r - wins}L",
        f"- **Win Rate:** **{win_rate:.2f}%**",
        f"- **Total Realized P&L:** **${total_pnl:,.2f} USDC**",
        f"",
        f"## Performance by Asset",
        f"| Asset | Trades | Wins | Losses | Win Rate | Net PnL |",
        f"|---|---|---|---|---|---|",
    ]
    for asset, group in sorted(asset_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        report_lines.append(f"| **{asset}** | {len(group)} | {a_wins} | {len(group) - a_wins} | {a_wr:.2f}% | ${a_pnl:.2f} |")
        
    report_lines.append(f"")
    report_lines.append(f"## Performance by Timeframe")
    report_lines.append(f"| Timeframe | Trades | Wins | Losses | Win Rate | Net PnL |")
    report_lines.append(f"|---|---|---|---|---|---|")
    for tf, group in sorted(tf_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        report_lines.append(f"| **{tf}** | {len(group)} | {a_wins} | {len(group) - a_wins} | {a_wr:.2f}% | ${a_pnl:.2f} |")
        
    report_lines.append(f"")
    report_lines.append(f"## Performance by Entry Price Band")
    report_lines.append(f"| Price Band | Trades | Wins | Losses | Win Rate | Net PnL |")
    report_lines.append(f"|---|---|---|---|---|---|")
    for band, group in sorted(price_groups.items()):
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        report_lines.append(f"| **{band.strip()}** | {len(group)} | {a_wins} | {len(group) - a_wins} | {a_wr:.2f}% | ${a_pnl:.2f} |")
        
    report_lines.append(f"")
    report_lines.append(f"## Performance by Day of Week")
    report_lines.append(f"| Day | Trades | Wins | Losses | Win Rate | Net PnL |")
    report_lines.append(f"|---|---|---|---|---|---|")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        group = day_groups[day]
        if not group:
            continue
        a_pnl = sum(x["pnl"] for x in group)
        a_wins = sum(1 for x in group if x["won"])
        a_wr = (a_wins / len(group)) * 100
        report_lines.append(f"| **{day}** | {len(group)} | {a_wins} | {len(group) - a_wins} | {a_wr:.2f}% | ${a_pnl:.2f} |")
        
    with open("/root/ZiSi-v2/wallet/wallet_0x21d0a97a_multi_week_reconciliation.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("\nSaved report to /root/ZiSi-v2/wallet/wallet_0x21d0a97a_multi_week_reconciliation.md")

if __name__ == '__main__':
    main()
