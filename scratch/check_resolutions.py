import json
import requests

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

try:
    with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

closed = data.get("closed", [])

# Filter positions around 14:50:04 UTC on July 19
target_positions = []
for pos in closed:
    exit_time_str = pos.get("exit_time") or pos.get("close_time") or ""
    if "14:50:04" in exit_time_str:
        target_positions.append(pos)

print(f"Found {len(target_positions)} target positions closed at 14:50:04 UTC:")

for p in target_positions:
    market_id = p.get("market_id")
    event_title = p.get("event_title")
    direction = p.get("direction")
    pnl = p.get("realized_pnl")
    print(f"\nTitle: {event_title}")
    print(f"Direction: {direction} | PnL: {pnl}")
    print(f"Market ID: {market_id}")
    
    if market_id:
        # Fetch CLOB market details
        url = f"https://clob.polymarket.com/markets/{market_id}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                m_data = r.json()
                print(f"Polymarket CLOB resolution: {m_data.get('description')} | Resolved: {m_data.get('resolved')} | Outcome: {m_data.get('outcome')}")
            else:
                print(f"Failed to fetch CLOB details: Status {r.status_code}")
        except Exception as e:
            print(f"Error fetching CLOB details: {e}")
