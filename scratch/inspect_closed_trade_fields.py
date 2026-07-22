import json
from pathlib import Path

POSITIONS_PATH = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json")

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

closed = data.get("closed", [])
print(f"Total closed trades: {len(closed)}")

# Inspect sample keys and fields of trades across different dates
sample_trades = [closed[0], closed[len(closed)//4], closed[len(closed)//2], closed[-1]]

for i, t in enumerate(sample_trades):
    print(f"\n--- Trade {i+1} ---")
    print("Entry Time:", t.get("entry_time"))
    print("Asset/TF:", t.get("event_title"), t.get("asset"), t.get("timeframe"))
    print("Entry Price:", t.get("entry_price"))
    print("Signal Price:", t.get("signal_price"))
    print("SLP field:", t.get("slp"))
    print("Keys in dict:", list(t.keys()))
