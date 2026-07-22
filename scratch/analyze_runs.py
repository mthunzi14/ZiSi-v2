import json
import sys
from collections import defaultdict

def main():
    try:
        # Read winners cache
        with open("/root/ZiSi-v2/wallet/resolved_winners_cache.json", "r", encoding="utf-8") as f:
            winners = json.load(f)
        
        # Read Run 1 Clean
        with open("/root/ZiSi-v2/wallet/wallet_0xeebde7a0_run1_clean.json", "r", encoding="utf-8") as f:
            run1 = json.load(f)
        
        # Read Run 2 Clean
        with open("/root/ZiSi-v2/wallet/wallet_0xeebde7a0_run2_clean.json", "r", encoding="utf-8") as f:
            run2 = json.load(f)
        
        print("=== Run 1 Clean Statistics ===")
        analyze_run(run1, winners)
        
        print("\n=== Run 2 Clean Statistics ===")
        analyze_run(run2, winners)
        
    except Exception as e:
        print("Error:", e)

def analyze_run(txs, winners):
    # Group transactions by market slug
    markets = defaultdict(list)
    for tx in txs:
        slug = tx.get("Slug")
        if slug:
            markets[slug].append(tx)
            
    total_markets = len(markets)
    wins = 0
    losses = 0
    pnl = 0.0
    
    asset_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "pnl": 0.0, "total": 0})
    
    for slug, trades in markets.items():
        # Find asset from slug
        asset = "UNKNOWN"
        for possible in ["btc", "eth", "sol", "xrp", "doge"]:
            if possible in slug.lower():
                asset = possible.upper()
                break
                
        # Resolve outcome
        winning_outcome = winners.get(slug)
        if not winning_outcome:
            continue
            
        # We need to find the final position state
        # In a buy transaction, we bet on BetOnOutcome (e.g. "Up" or "Down")
        bet = trades[0].get("BetOnOutcome")
        if not bet:
            continue
            
        won = bet.lower() == winning_outcome.lower()
        
        # Calculate cost and return
        spent = sum(t.get("TotalUSDCSpent", 0.0) for t in trades if t.get("Action") == "BUY")
        shares = sum(t.get("TotalShares", 0.0) for t in trades if t.get("Action") == "BUY")
        
        if won:
            wins += 1
            asset_stats[asset]["wins"] += 1
            trade_pnl = shares - spent
        else:
            losses += 1
            asset_stats[asset]["losses"] += 1
            trade_pnl = -spent
            
        pnl += trade_pnl
        asset_stats[asset]["pnl"] += trade_pnl
        asset_stats[asset]["total"] += 1
        
    print(f"Total resolved markets: {wins + losses}")
    print(f"Wins: {wins} | Losses: {losses}")
    print(f"Win Rate: {(wins / max(1, wins + losses)) * 100:.2f}%")
    print(f"Total PnL: ${pnl:.2f}")
    
    print("\nAsset Breakdown:")
    # sort by asset name
    for asset in sorted(asset_stats.keys()):
        stats = asset_stats[asset]
        wr = (stats["wins"] / max(1, stats["total"])) * 100
        print(f"  {asset}: {stats['total']} trades | {stats['wins']} W - {stats['losses']} L | Win Rate: {wr:.2f}% | PnL: ${stats['pnl']:.2f}")

if __name__ == '__main__':
    main()
