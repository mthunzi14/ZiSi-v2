import json
import sys
from collections import defaultdict
from datetime import datetime

def main():
    try:
        # Load Winners Cache
        with open("/root/ZiSi-v2/wallet/resolved_winners_cache.json", "r", encoding="utf-8") as f:
            winners = json.load(f)
        
        # Load Run 2 Clean (representing his high-performance prime period)
        with open("/root/ZiSi-v2/wallet/wallet_0xeebde7a0_run2_clean.json", "r", encoding="utf-8") as f:
            run2 = json.load(f)
            
        print("=== BONEREAPER (0xeebde7a0) DEEP QUANTITATIVE AUDIT ===")
        deconstruct_wallet(run2, winners)
        
    except Exception as e:
        print("Error:", e)

def deconstruct_wallet(txs, winners):
    # Group transactions by market slug
    markets = defaultdict(list)
    for tx in txs:
        slug = tx.get("Slug")
        if slug:
            markets[slug].append(tx)
            
    total_markets = len(markets)
    resolved_trades = []
    
    for slug, trades in markets.items():
        # Find asset from slug
        asset = "UNKNOWN"
        for possible in ["btc", "eth", "sol", "xrp", "doge"]:
            if possible in slug.lower():
                asset = possible.upper()
                break
                
        # Resolve timeframe
        tf = "5m"
        if "15m" in slug.lower():
            tf = "15m"
        elif "1h" in slug.lower():
            tf = "1h"
            
        # Resolve outcome
        winning_outcome = winners.get(slug)
        if not winning_outcome:
            continue
            
        # We bet on BetOnOutcome (e.g. "Up" or "Down")
        bet = trades[0].get("BetOnOutcome")
        if not bet:
            continue
            
        won = bet.lower() == winning_outcome.lower()
        
        # Calculate cost and return
        spent = sum(t.get("TotalUSDCSpent", 0.0) for t in trades if t.get("Action") == "BUY")
        shares = sum(t.get("TotalShares", 0.0) for t in trades if t.get("Action") == "BUY")
        avg_entry_price = spent / shares if shares > 0 else 0.0
        
        # Day of week
        dt_str = trades[0].get("DateTime")
        day_of_week = "Unknown"
        is_weekend = False
        if dt_str:
            try:
                # ISO format parse
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                day_of_week = dt.strftime("%A")
                is_weekend = dt.weekday() >= 5  # 5=Saturday, 6=Sunday
            except:
                pass
                
        trade_pnl = (shares - spent) if won else -spent
        
        resolved_trades.append({
            "slug": slug,
            "asset": asset,
            "tf": tf,
            "entry_price": avg_entry_price,
            "won": won,
            "pnl": trade_pnl,
            "day": day_of_week,
            "is_weekend": is_weekend,
            "shares": shares,
            "spent": spent
        })

    total = len(resolved_trades)
    wins = sum(1 for t in resolved_trades if t["won"])
    losses = total - wins
    overall_pnl = sum(t["pnl"] for t in resolved_trades)
    
    print(f"\nOverall Performance:")
    print(f"  Total Trades Analyzed: {total}")
    print(f"  Wins: {wins} | Losses: {losses}")
    print(f"  Win Rate: {(wins / max(1, total)) * 100:.2f}%")
    print(f"  Total PnL: ${overall_pnl:.2f}")

    # 1. Asset Breakdown
    print("\n1. Asset Performance Breakdown:")
    asset_groups = defaultdict(list)
    for t in resolved_trades:
        asset_groups[t["asset"]].append(t)
    for asset in sorted(asset_groups.keys()):
        grp = asset_groups[asset]
        a_tot = len(grp)
        a_wins = sum(1 for t in grp if t["won"])
        a_pnl = sum(t["pnl"] for t in grp)
        print(f"  {asset:5}: {a_tot:2} trades | {a_wins:2} W - {a_tot - a_wins:2} L | Win Rate: {(a_wins/max(1, a_tot))*100:5.2f}% | PnL: ${a_pnl:8.2f}")

    # 2. Timeframe Breakdown
    print("\n2. Timeframe Performance Breakdown:")
    tf_groups = defaultdict(list)
    for t in resolved_trades:
        tf_groups[t["tf"]].append(t)
    for tf in sorted(tf_groups.keys()):
        grp = tf_groups[tf]
        t_tot = len(grp)
        t_wins = sum(1 for t in grp if t["won"])
        t_pnl = sum(t["pnl"] for t in grp)
        print(f"  {tf:5}: {t_tot:2} trades | {t_wins:2} W - {t_tot - t_wins:2} L | Win Rate: {(t_wins/max(1, t_tot))*100:5.2f}% | PnL: ${t_pnl:8.2f}")

    # 3. Entry Price Band Analysis
    print("\n3. Entry Price Band Performance:")
    bands = [
        ("< $0.30", lambda p: p < 0.30),
        ("$0.30 - $0.50", lambda p: 0.30 <= p < 0.50),
        ("$0.50 - $0.70", lambda p: 0.50 <= p < 0.70),
        ("$0.70 - $0.85", lambda p: 0.70 <= p < 0.85),
        (">= $0.85 (High Risk/NCS)", lambda p: p >= 0.85)
    ]
    for label, fn in bands:
        grp = [t for t in resolved_trades if fn(t["entry_price"])]
        b_tot = len(grp)
        b_wins = sum(1 for t in grp if t["won"])
        b_pnl = sum(t["pnl"] for t in grp)
        print(f"  {label:25}: {b_tot:2} trades | {b_wins:2} W - {b_tot - b_wins:2} L | Win Rate: {(b_wins/max(1, b_tot))*100:5.2f}% | PnL: ${b_pnl:8.2f}")

    # 4. Temporal Analysis (Weekday vs Weekend)
    print("\n4. Day of Week & Session Performance:")
    day_groups = defaultdict(list)
    for t in resolved_trades:
        day_groups[t["day"]].append(t)
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        grp = day_groups[day]
        d_tot = len(grp)
        d_wins = sum(1 for t in grp if t["won"])
        d_pnl = sum(t["pnl"] for t in grp)
        print(f"  {day:9}: {d_tot:2} trades | {d_wins:2} W - {d_tot - d_wins:2} L | Win Rate: {(d_wins/max(1, d_tot))*100:5.2f}% | PnL: ${d_pnl:8.2f}")

    weekend_grp = [t for t in resolved_trades if t["is_weekend"]]
    weekday_grp = [t for t in resolved_trades if not t["is_weekend"]]
    
    print(f"\n  Weekdays : {len(weekday_grp):2} trades | {sum(1 for t in weekday_grp if t['won']):2} W | Win Rate: {(sum(1 for t in weekday_grp if t['won'])/max(1, len(weekday_grp)))*100:.2f}% | PnL: ${sum(t['pnl'] for t in weekday_grp):.2f}")
    print(f"  Weekends : {len(weekend_grp):2} trades | {sum(1 for t in weekend_grp if t['won']):2} W | Win Rate: {(sum(1 for t in weekend_grp if t['won'])/max(1, len(weekend_grp)))*100:.2f}% | PnL: ${sum(t['pnl'] for t in weekend_grp):.2f}")

if __name__ == '__main__':
    main()
