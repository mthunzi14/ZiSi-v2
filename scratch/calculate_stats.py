import json
from pathlib import Path
import re

def main():
    path = Path("/root/ZiSi-v2/data/positions_state.json")
    if not path.exists():
        print(f"File {path} does not exist!")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    closed = data.get("closed", [])
    stats = {}
    
    for p in closed:
        title = p.get("event_title", "")
        # Try to parse asset from event_title [UPDOWN][BTC][5m]
        asset = "UNKNOWN"
        m = re.search(r"\[(BTC|ETH|SOL|XRP|DOGE|HYPE|BNB)\]", title)
        if m:
            asset = m.group(1)
            
        r = stats.setdefault(asset, {"wins": 0, "losses": 0, "flat": 0, "total": 0})
        pnl = float(p.get("realized_pnl", 0.0))
        r["total"] += 1
        if pnl > 0.009:
            r["wins"] += 1
        elif pnl < -0.009:
            r["losses"] += 1
        else:
            r["flat"] += 1
            
    print("--- ASSET WIN RATE STATS ---")
    for k, v in sorted(stats.items()):
        total_resolved = v["wins"] + v["losses"]
        wr = (v["wins"] / total_resolved) * 100 if total_resolved > 0 else 0
        print(f"{k} | Total: {v['total']} | WR: {wr:.2f}% | Wins: {v['wins']} | Losses: {v['losses']} | Breakeven: {v['flat']}")

if __name__ == "__main__":
    main()
