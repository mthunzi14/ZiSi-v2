import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import zisi_terminal

print("Testing active market resolver...")
now = time.time()
ts_current = int(now // 300) * 300
print(f"Current Unix timestamp boundary: {ts_current} (ISO: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ts_current))} UTC)")

assets = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for asset in assets:
    coin_lower = asset.lower()
    for ts in [ts_current, ts_current + 300]:
        slug = f"{coin_lower}-updown-5m-{ts}"
        url = f"https://gamma-api.polymarket.com/events?slug={slug}"
        print(f"Fetching: {url}")
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as r:
                import json
                data = json.loads(r.read())
                if data and isinstance(data, list) and len(data) > 0:
                    markets = data[0].get("markets", [])
                    print(f"  [SUCCESS] Found event! Markets count: {len(markets)}")
                    for m in markets:
                        print(f"    Market ID: {m.get('id')} -> {m.get('question')}")
                else:
                    print(f"  [EMPTY] Empty event list returned.")
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
