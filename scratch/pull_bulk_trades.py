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

def fetch_bulk_trades(address, target_count=1500):
    all_trades = []
    limit = 100
    offset = 0
    
    print(f"Fetching bulk trades for {address} (Target: {target_count})...")
    while len(all_trades) < target_count:
        url = f"https://data-api.polymarket.com/activity?user={address}&limit={limit}&offset={offset}"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f"  Error fetching at offset {offset}: status {r.status_code}")
                break
                
            activities = r.json()
            if not activities:
                print(f"  No more activities returned at offset {offset}.")
                break
                
            trades = [a for a in activities if a.get("type") == "TRADE"]
            all_trades.extend(trades)
            
            print(f"  Offset {offset:4} | Fetced {len(trades):3} trades | Total accrued: {len(all_trades)}")
            offset += limit
            time.sleep(0.5)  # rate limit safety
            
            # If the API returned fewer activities than the limit, we hit the end of history
            if len(activities) < limit:
                print("  Hit end of user history.")
                break
        except Exception as e:
            print(f"  Exception at offset {offset}: {e}")
            break
            
    return all_trades[:target_count]

def analyze_and_format(name, trades):
    lines = []
    lines.append(f"======================================================================")
    lines.append(f"  DEEP QUANTITATIVE EDGE DECONSTRUCTION: {name.upper()}")
    lines.append(f"======================================================================")
    lines.append(f"Analyzed {len(trades)} recent trades.")
    if not trades:
        return "\n".join(lines)
        
    asset_counts = defaultdict(int)
    timeframe_counts = defaultdict(int)
    side_counts = defaultdict(int)
    price_bands = defaultdict(int)
    days_of_week = defaultdict(int)
    hourly_distribution = defaultdict(int)
    
    # Track volumes and averages per asset
    asset_volume = defaultdict(float)
    asset_shares = defaultdict(float)
    
    for t in trades:
        title = t.get("title", "")
        slug = t.get("slug", "")
        price = float(t.get("price", 0.0))
        size = float(t.get("size", 0.0))
        usdc = float(t.get("usdcSize", 0.0))
        side = t.get("side", "BUY")
        ts = t.get("timestamp", 0)
        
        # Resolve Asset
        asset = "UNKNOWN"
        for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:
            if possible in title.upper() or possible in slug.upper():
                asset = possible
                break
        asset_counts[asset] += 1
        asset_volume[asset] += usdc
        asset_shares[asset] += size
        
        # Resolve Timeframe
        tf = "5m"
        if "15M" in title.upper() or "15M" in slug.upper():
            tf = "15m"
        elif "1H" in title.upper() or "1H" in slug.upper():
            tf = "1h"
        timeframe_counts[tf] += 1
        
        # Side
        side_counts[side] += 1
        
        # Price Bands
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
            
        # Temporal
        if ts > 0:
            dt = datetime.fromtimestamp(ts)
            day = dt.strftime("%A")
            days_of_week[day] += 1
            hour = dt.strftime("%H:00")
            hourly_distribution[hour] += 1
            
    total_spent = sum(asset_volume.values())
    lines.append(f"Total spent volume: ${total_spent:,.2f} USDC")
    
    lines.append("\n1. Asset Performance Breakdown:")
    for a, count in sorted(asset_counts.items(), key=lambda x: x[1], reverse=True):
        vol = asset_volume[a]
        pct = (count / len(trades)) * 100
        lines.append(f"  {a:7}: {count:4} trades ({pct:5.1f}%) | Volume: ${vol:10,.2f} USDC (avg ${vol/max(1, count):.2f}/trade)")
        
    lines.append("\n2. Timeframe Breakdown:")
    for tf, count in sorted(timeframe_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(trades)) * 100
        lines.append(f"  {tf:7}: {count:4} trades ({pct:5.1f}%)")
        
    lines.append("\n3. Action Breakdown:")
    for s, count in sorted(side_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(trades)) * 100
        lines.append(f"  {s:7}: {count:4} trades ({pct:5.1f}%)")
        
    lines.append("\n4. Entry Price Distribution:")
    for band in ["< $0.30 (Low Odds)", "$0.30 - $0.50 (Mid-Low)", "$0.50 - $0.70 (Mid-High)", "$0.70 - $0.85 (High Odds)", ">= $0.85 (Certainty/NCS)"]:
        count = price_bands[band]
        pct = (count / len(trades)) * 100
        lines.append(f"  {band:30}: {count:4} trades ({pct:5.1f}%)")
        
    lines.append("\n5. Day of Week Distribution:")
    for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        count = days_of_week[d]
        pct = (count / len(trades)) * 100
        lines.append(f"  {d:10}: {count:4} trades ({pct:5.1f}%)")

    lines.append("\n6. Top Hourly Windows (UTC):")
    sorted_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:8]
    for h, count in sorted_hours:
        pct = (count / len(trades)) * 100
        lines.append(f"  {h}: {count:4} trades ({pct:5.1f}%)")
        
    return "\n".join(lines)

def main():
    report_lines = []
    report_lines.append(f"======================================================================")
    report_lines.append(f"  ZiSi-v2 Bulk Inspiration Wallets Edge Analysis")
    report_lines.append(f"  Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report_lines.append(f"======================================================================")
    
    for name, addr in WALLETS.items():
        # Pull 1500 trades (or as many as available)
        trades = fetch_bulk_trades(addr, target_count=1500)
        analysis_text = analyze_and_format(name, trades)
        report_lines.append("\n" + analysis_text)
        
    report = "\n".join(report_lines)
    
    # Save report
    report_path = "/root/ZiSi-v2/data/bulk_wallet_analysis_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"\nBulk analysis complete! Report saved to {report_path}")
    
    # Print the report to stdout so it gets captured in logs
    print(report)

if __name__ == '__main__':
    main()
