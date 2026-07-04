import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ADDRESS = "0xeebde7a0e019a63e6b476eb425505b7b3e6eba30"
BASE_URL = "https://data-api.polymarket.com/activity"
GAMMA_URL = "https://gamma-api.polymarket.com"
WALLET_DIR = "/root/ZiSi-v2/wallet"
CACHE_PATH = os.path.join(WALLET_DIR, "resolved_winners_cache.json")
RESULTS_PATH = "/root/ZiSi-v2/data/bonereaper_deep_analysis.json"

def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache):
    try:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        print(f"Error saving cache: {e}")

def format_trade(t):
    ts = int(t.get("timestamp") or t.get("blockTimestamp") or 0)
    dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else ""
    
    price = float(t.get("price") or 0.0)
    shares = float(t.get("size") or t.get("tokens") or t.get("shares") or 0.0)
    spent = float(t.get("usdcSize") or t.get("cash") or t.get("amount") or 0.0)
    
    if price == 0.0 and shares > 0 and spent > 0:
        price = spent / shares
    elif spent == 0.0 and price > 0 and shares > 0:
        spent = price * shares
        
    return {
        "TargetWallet": ADDRESS,
        "DateTime": dt_str,
        "Market": t.get("title") or t.get("market") or "",
        "Slug": t.get("slug") or t.get("conditionId") or "",
        "Action": (t.get("side") or t.get("type") or "").upper(),
        "BetOnOutcome": t.get("outcome") or "",
        "PricePerShare": round(price, 6),
        "TotalShares": round(shares, 6),
        "TotalUSDCSpent": round(spent, 6),
        "TxHash": t.get("transactionHash") or t.get("txHash") or ""
    }

def fetch_trades(max_trades=10000):
    print(f"[FETCH] Pulling up to {max_trades} trades for bonereaper...")
    trades = []
    seen = set()
    current_end = int(time.time())
    page = 0
    limit = 100
    
    while len(trades) < max_trades and page < 120:
        page += 1
        params = {
            "user": ADDRESS,
            "type": "TRADE",
            "limit": limit,
            "sortBy": "TIMESTAMP",
            "sortDirection": "DESC",
            "end": current_end
        }
        
        success = False
        data = None
        for attempt in range(1, 6):
            try:
                r = requests.get(BASE_URL, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    success = True
                    break
                elif r.status_code == 429:
                    time.sleep(2.0 ** attempt)
                else:
                    time.sleep(1.0)
            except Exception:
                time.sleep(1.0)
                
        if not success or not data:
            print(f"  Failed or empty response at page {page}. Stopping.")
            break
            
        new_items = []
        for item in data:
            tx = item.get("transactionHash")
            ts = item.get("timestamp")
            if tx and (tx, ts) not in seen:
                seen.add((tx, ts))
                new_items.append(format_trade(item))
                
        if not new_items:
            break
            
        trades.extend(new_items)
        last_ts = int(data[-1].get("timestamp"))
        current_end = last_ts - 1 if last_ts == current_end else last_ts
        time.sleep(0.05)
        
    print(f"  Completed! Total fetched bonereaper trades: {len(trades)}")
    return trades[:max_trades]

def resolve_slugs_in_batches(missing_slugs, cache):
    if not missing_slugs:
        return
    batch_size = 60
    batches = [missing_slugs[i:i+batch_size] for i in range(0, len(missing_slugs), batch_size)]
    print(f"[GAMMA] Resolving {len(missing_slugs)} missing slugs...")
    
    def process_batch(batch):
        url = f"{GAMMA_URL}/events"
        params = [("slug", s) for s in batch] + [("limit", str(len(batch)))]
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params=params, timeout=15)
            if r.status_code == 200:
                events = r.json()
                results = {}
                for event in events:
                    event_slug = event.get("slug")
                    if not event_slug: continue
                    markets = event.get("markets", [])
                    winner = None
                    for mkt in markets:
                        outcomes_str = mkt.get("outcomes", "[]")
                        prices_str = mkt.get("outcomePrices", "[]")
                        try:
                            outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
                            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
                        except Exception:
                            continue
                        for idx, p in enumerate(prices):
                            if str(p) in ("1", "1.0", "0.99", "0.999", "0.995"):
                                if idx < len(outcomes):
                                    winner = outcomes[idx]
                                    break
                        if winner: break
                    if winner:
                        results[event_slug] = winner
                return results
        except Exception:
            pass
        return {}

    resolved = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        for fut in as_completed(futures):
            res = fut.result()
            for s, w in res.items():
                if s not in cache:
                    cache[s] = w
                    resolved += 1
            time.sleep(0.05)
            
    print(f"  Gamma resolution done! Resolved {resolved} new winners.")
    save_cache(cache)

def analyze_trades(trades, cache):
    grouped = {}
    for t in trades:
        slug = t.get("Slug")
        if slug:
            grouped.setdefault(slug, []).append(t)
            
    total_markets = len(grouped)
    resolved_markets = 0
    wins = 0
    losses = 0
    spent = 0.0
    payout = 0.0
    
    tf_stats = {}
    asset_stats = {}
    session_stats = {
        "Asian (00-08 UTC)": {"count": 0, "wins": 0, "losses": 0, "spent": 0.0, "payout": 0.0},
        "European (08-16 UTC)": {"count": 0, "wins": 0, "losses": 0, "spent": 0.0, "payout": 0.0},
        "US (16-24 UTC)": {"count": 0, "wins": 0, "losses": 0, "spent": 0.0, "payout": 0.0}
    }
    
    for slug, group in grouped.items():
        group.sort(key=lambda x: x.get("DateTime", ""))
        title = group[0].get("Market", "") or ""
        title_lower = title.lower()
        slug_lower = slug.lower()
        
        # Timeframe
        if "-15m-" in slug_lower or "15m" in slug_lower or "15-minute" in title_lower or "15 minute" in title_lower:
            tf = "15m"
        elif "-5m-" in slug_lower or "5m" in slug_lower or "5-minute" in title_lower or "5 minute" in title_lower:
            tf = "5m"
        elif "-1h-" in slug_lower or "1h" in slug_lower or "1-hour" in title_lower or "1 hour" in title_lower or "hourly" in title_lower or ("up-or-down-" in slug_lower and slug_lower.endswith("-et")):
            tf = "1h"
        elif "-4h-" in slug_lower or "4h" in slug_lower or "4-hour" in title_lower or "4 hour" in title_lower:
            tf = "4h"
        else:
            tf = "other"
            
        tf_stats.setdefault(tf, {"count": 0, "wins": 0, "losses": 0, "spent": 0.0, "payout": 0.0})
        
        # Asset
        asset = "OTHER"
        for sym in ["BTC", "ETH", "SOL", "XRP", "DOGE", "LINK", "BNB"]:
            if sym.lower() in slug_lower or sym.lower() in title_lower or (sym == "BTC" and "bitcoin" in title_lower) or (sym == "ETH" and "ethereum" in title_lower):
                asset = sym
                break
                
        asset_stats.setdefault(asset, {"count": 0, "wins": 0, "losses": 0, "spent": 0.0, "payout": 0.0})
        
        try:
            dt = datetime.fromisoformat(group[0].get("DateTime").replace("Z", "+00:00"))
            hour = dt.astimezone(timezone.utc).hour
        except Exception:
            hour = 12
            
        if 0 <= hour < 8:
            sess = "Asian (00-08 UTC)"
        elif 8 <= hour < 16:
            sess = "European (08-16 UTC)"
        else:
            sess = "US (16-24 UTC)"
            
        winner = cache.get(slug)
        market_spent = 0.0
        market_payout = 0.0
        
        for t in group:
            act = t.get("Action")
            amt = t.get("TotalUSDCSpent") or 0.0
            shs = t.get("TotalShares") or 0.0
            out = t.get("BetOnOutcome") or ""
            
            if act == "BUY":
                market_spent += amt
                if winner and out.strip().lower() == winner.strip().lower():
                    market_payout += shs
            elif act == "SELL":
                market_payout += amt
                
        spent += market_spent
        payout += market_payout
        
        if winner:
            resolved_markets += 1
            is_win = market_payout > market_spent
            
            tf_stats[tf]["spent"] += market_spent
            tf_stats[tf]["payout"] += market_payout
            
            asset_stats[asset]["spent"] += market_spent
            asset_stats[asset]["payout"] += market_payout
            
            session_stats[sess]["spent"] += market_spent
            session_stats[sess]["payout"] += market_payout
            
            if is_win:
                wins += 1
                tf_stats[tf]["wins"] += 1
                asset_stats[asset]["wins"] += 1
                session_stats[sess]["wins"] += 1
            else:
                losses += 1
                tf_stats[tf]["losses"] += 1
                asset_stats[asset]["losses"] += 1
                session_stats[sess]["losses"] += 1
                
            tf_stats[tf]["count"] += 1
            asset_stats[asset]["count"] += 1
            session_stats[sess]["count"] += 1
            
    wr = (wins / resolved_markets * 100) if resolved_markets > 0 else 0.0
    pnl = payout - spent
    
    # Save JSON results to inspect programmatically
    results = {
        "resolved_markets": resolved_markets,
        "wins": wins,
        "losses": losses,
        "win_rate": wr,
        "spent": spent,
        "payout": payout,
        "pnl": pnl,
        "tf_stats": tf_stats,
        "asset_stats": asset_stats,
        "session_stats": session_stats
    }
    
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"Deep Analysis json generated at {RESULTS_PATH}")

def main():
    cache = load_cache()
    print(f"Loaded {len(cache)} resolutions from cache.")
    
    trades = fetch_trades(10000)
    
    missing_slugs = set()
    for t in trades:
        slug = t.get("Slug")
        if slug and slug not in cache:
            missing_slugs.add(slug)
            
    if missing_slugs:
        resolve_slugs_in_batches(list(missing_slugs), cache)
        
    analyze_trades(trades, cache)

if __name__ == "__main__":
    main()
