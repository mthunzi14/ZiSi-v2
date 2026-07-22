import requests
import json
import time
from collections import defaultdict
from datetime import datetime

WALLETS = {
    "PBot-6 Main": "0x21d0a97aac03917e752857a551bbe5103a00e8d7",
    "PBot Sweeper": "0x13f0bcec1e2e60ec9acc3bee4d2da2fe9694a50f",
    "Bonereaper": "0xeebde7a0e019a63e6b476eb425505b7b3e6eba30"
}

def fetch_recent_trades(address, limit=500):
    url = f"https://data-api.polymarket.com/activity?user={address}&limit={limit}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            activities = r.json()
            trades = [a for a in activities if a.get("type") == "TRADE"]
            return trades
        else:
            print(f"Failed to fetch for {address}, status code: {r.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching for {address}: {e}")
        return []

def analyze_trades(name, trades):
    print(f"\n==========================================")
    print(f"  QUANTITATIVE ANALYSIS: {name}")
    print(f"==========================================")
    print(f"Fetched {len(trades)} recent trade records.")
    if not trades:
        return
        
    asset_counts = defaultdict(int)
    timeframe_counts = defaultdict(int)
    side_counts = defaultdict(int)
    price_bands = defaultdict(int)
    days_of_week = defaultdict(int)
    hourly_distribution = defaultdict(int)
    
    total_spent = 0.0
    total_shares = 0.0
    
    for t in trades:
        title = t.get("title", "")
        slug = t.get("slug", "")
        price = float(t.get("price", 0.0))
        size = float(t.get("size", 0.0))
        usdc = float(t.get("usdcSize", 0.0))
        side = t.get("side", "BUY")
        ts = t.get("timestamp", 0)
        
        total_spent += usdc
        total_shares += size
        
        # 1. Resolve Asset
        asset = "UNKNOWN"
        for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:
            if possible in title.upper() or possible in slug.upper():
                asset = possible
                break
        asset_counts[asset] += 1
        
        # 2. Resolve Timeframe
        tf = "5m"
        if "15M" in title.upper() or "15M" in slug.upper():
            tf = "15m"
        elif "1H" in title.upper() or "1H" in slug.upper():
            tf = "1h"
        timeframe_counts[tf] += 1
        
        # 3. Side
        side_counts[side] += 1
        
        # 4. Price Bands
        if price < 0.30:
            price_bands["< $0.30 (Low Odds)"] += 1
        elif 0.30 <= price < 0.50:
            price_bands["$0.30 - $0.50 (Mid-Low)"] += 1
        elif 0.50 <= price < 0.70:
            price_bands["$0.50 - $0.70 (Mid-High)"] += 1
        elif 0.70 <= price < 0.85:
            price_bands["$0.70 - $0.85 (High Odds)"] += 1
        else:
            price_bands[">= $0.85 (Certainty/NCS)"] += 1
            
        # 5. Temporal
        if ts > 0:
            dt = datetime.fromtimestamp(ts)
            day = dt.strftime("%A")
            days_of_week[day] += 1
            hour = dt.strftime("%H:00")
            hourly_distribution[hour] += 1
            
    print(f"Total volume (USDC Size): ${total_spent:,.2f}")
    print(f"Total shares bought/sold: {total_shares:,.2f}")
    
    print("\n1. Asset Breakdown:")
    for a, count in sorted(asset_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {a:7}: {count:3} trades ({(count/len(trades))*100:.1f}%)")
        
    print("\n2. Timeframe Breakdown:")
    for tf, count in sorted(timeframe_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tf:7}: {count:3} trades ({(count/len(trades))*100:.1f}%)")
        
    print("\n3. Side Breakdown:")
    for s, count in sorted(side_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {s:7}: {count:3} trades ({(count/len(trades))*100:.1f}%)")
        
    print("\n4. Entry Price Distribution:")
    for band in ["< $0.30 (Low Odds)", "$0.30 - $0.50 (Mid-Low)", "$0.50 - $0.70 (Mid-High)", "$0.70 - $0.85 (High Odds)", ">= $0.85 (Certainty/NCS)"]:
        count = price_bands[band]
        print(f"  {band:30}: {count:3} trades ({(count/len(trades))*100:.1f}%)")
        
    print("\n5. Day of Week Distribution:")
    for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        count = days_of_week[d]
        print(f"  {d:10}: {count:3} trades ({(count/len(trades))*100:.1f}%)")

    print("\n6. Top Hourly Windows (UTC):")
    sorted_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
    for h, count in sorted_hours:
        print(f"  {h}: {count:3} trades ({(count/len(trades))*100:.1f}%)")

def main():
    for name, addr in WALLETS.items():
        trades = fetch_recent_trades(addr, limit=500)
        analyze_trades(name, trades)
        time.sleep(1)

if __name__ == '__main__':
    main()
