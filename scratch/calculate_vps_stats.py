import json
from collections import defaultdict

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

try:
    with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

closed = data.get("closed", [])
print(f"Total closed positions: {len(closed)}")

# We need to map each tranche record to its asset
# Let's count wins, losses, breakevens per asset
stats = defaultdict(lambda: {"wins": 0, "losses": 0, "be": 0})

for pos in closed:
    title = pos.get("event_title", "")
    pnl = pos.get("realized_pnl", 0.0)
    exit_reason = pos.get("exit_reason", "")
    
    # Extract asset from event_title e.g. [UPDOWN][BTC][5m][ZISI]
    asset = "UNKNOWN"
    for a in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE"]:
        if f"[{a}]" in title:
            asset = a
            break
            
    if pnl > 0.009:
        stats[asset]["wins"] += 1
    elif pnl < -0.009:
        stats[asset]["losses"] += 1
    else:
        stats[asset]["be"] += 1

total_all = 0
wins_all = 0
losses_all = 0
be_all = 0

print("\n| Asset | Trades | Wins | Losses | BE | Win Rate |")
print("|---|---|---|---|---|---|")
for asset in ["DOGE", "SOL", "XRP", "ETH", "BTC", "BNB", "HYPE"]:
    s = stats[asset]
    total = s["wins"] + s["losses"] + s["be"]
    wr = (s["wins"] / (s["wins"] + s["losses"])) * 100 if (s["wins"] + s["losses"]) > 0 else 0
    print(f"| {asset} | {total} | {s['wins']} | {s['losses']} | {s['be']} | {wr:.1f}% |")
    total_all += total
    wins_all += s["wins"]
    losses_all += s["losses"]
    be_all += s["be"]

wr_all = (wins_all / (wins_all + losses_all)) * 100 if (wins_all + losses_all) > 0 else 0
print(f"| **OVERALL** | **{total_all}** | **{wins_all}** | **{losses_all}** | **{be_all}** | **{wr_all:.1f}%** |")
