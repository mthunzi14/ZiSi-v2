import requests

market_ids = [
    "62636902377091213817535006927823479735278139003143603012841347248023794335502", # SOL
    "95145654447998599116848474837754152404236567812025663926670580530442627389992"  # BTC
]

for m_id in market_ids:
    print(f"\nFetching Gamma info for: {m_id}")
    url = f"https://gamma-api.polymarket.com/markets?id={m_id}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                m = data[0]
                print(f"Title: {m.get('question')}")
                print(f"Outcome: {m.get('outcomeType')} | Resolved: {m.get('resolved')} | Resolution Source: {m.get('resolutionSource')}")
                print(f"Clarifying rules: {m.get('rules')}")
                print(f"End date / Expiry: {m.get('endDate')}")
            else:
                # Try direct get
                url_direct = f"https://gamma-api.polymarket.com/markets/{m_id}"
                r2 = requests.get(url_direct, timeout=10)
                if r2.status_code == 200:
                    m = r2.json()
                    print(f"Direct Title: {m.get('question')}")
                    print(f"Resolved: {m.get('resolved')} | Outcome: {m.get('outcome')}")
                else:
                    print(f"Gamma returned empty or error: {data}")
        else:
            print(f"Gamma HTTP Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Error fetching Gamma info: {e}")
