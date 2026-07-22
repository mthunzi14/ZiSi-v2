import json

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
closed = data.get("closed", [])

assets = ['BTC','ETH','SOL','XRP','DOGE','BNB','HYPE']
stats = {a: {'w': 0, 'l': 0, 'be': 0} for a in assets}

for p in closed:
    title = p.get('event_title', '')
    if not title:
        continue
    # Extract asset name
    # Format is usually [UPDOWN][ASSET][5m][ZISI] or similar
    asset = None
    for a in assets:
        if f"[{a}]" in title:
            asset = a
            break
    if asset:
        pnl = p.get('realized_pnl', 0.0)
        if pnl > 0.01:
            stats[asset]['w'] += 1
        elif pnl < -0.01:
            stats[asset]['l'] += 1
        else:
            stats[asset]['be'] += 1

print("| Asset | Trades | Win Rate | Status |")
print("|---|---|---|---|")
total_w = 0
total_l = 0
total_be = 0
for a in assets:
    w = stats[a]['w']
    l = stats[a]['l']
    be = stats[a]['be']
    tot = w + l + be
    total_w += w
    total_l += l
    total_be += be
    wr = (w / (w + l)) * 100 if (w + l) > 0 else 0.0
    print(f"| {a} | {tot} | {wr:.1f}% | w={w}, l={l}, be={be} |")
    
tot_all = total_w + total_l + total_be
wr_all = (total_w / (total_w + total_l)) * 100 if (total_w + total_l) > 0 else 0.0
print(f"| OVERALL | {tot_all} | {wr_all:.1f}% | w={total_w}, l={total_l}, be={total_be} |")
