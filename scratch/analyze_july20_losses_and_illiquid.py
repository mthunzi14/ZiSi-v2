import json
import os
import glob

print("=== COMPREHENSIVE POSITIONS & LOSS SCRUBBER ===")

files_to_check = glob.glob("backups/*.json") + glob.glob("data/*.json") + glob.glob("*.json")

all_trades = []

for filepath in set(files_to_check):
    if not os.path.exists(filepath):
        continue
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            closed = data.get("closed", data.get("closed_positions", []))
            active = data.get("active", data.get("active_positions", data.get("open_positions", [])))
            if isinstance(closed, list):
                for item in closed:
                    if isinstance(item, dict):
                        item["_source"] = os.path.basename(filepath)
                        all_trades.append(item)
            if isinstance(active, list):
                for item in active:
                    if isinstance(item, dict):
                        item["_source"] = os.path.basename(filepath)
                        all_trades.append(item)
    except Exception as e:
        pass

print(f"Total trade records aggregated across all files: {len(all_trades)}")

losses = []
for p in all_trades:
    pnl = p.get("pnl", p.get("realized_pnl", p.get("profit", 0.0)))
    outcome = str(p.get("outcome", p.get("status", ""))).upper()
    ts = str(p.get("timestamp_closed", p.get("timestamp", p.get("time", p.get("entry_time", "")))))
    
    # Identify loss
    if pnl < 0 or outcome == "LOSS":
        losses.append({
            "source": p["_source"],
            "symbol": p.get("symbol", p.get("asset", "")),
            "pnl": round(pnl, 2),
            "amount": round(p.get("amount", p.get("size", p.get("cost", p.get("price", 0.0)))), 2),
            "entry_price": p.get("entry_price", p.get("price", 0.0)),
            "strike_price": p.get("strike_price", 0.0),
            "exit_price": p.get("exit_price", 0.0),
            "side": p.get("side", p.get("direction", "")),
            "timestamp": ts,
            "reason": p.get("exit_reason", p.get("reason", p.get("status", ""))),
            "market_slug": p.get("market_slug", "")
        })

print(f"Total losses aggregated: {len(losses)}")

# Deduplicate losses by timestamp and symbol
seen = set()
unique_losses = []
for l in losses:
    key = (l["timestamp"], l["symbol"], l["pnl"])
    if key not in seen:
        seen.add(key)
        unique_losses.append(l)

losses_sorted = sorted(unique_losses, key=lambda x: str(x["timestamp"]))

print("\n--- RECENT LOSSES IN THE ARCHIVE / DATA ---")
for l in losses_sorted[-40:]:
    print(f"[{l['timestamp']}] {l['symbol']} {l['side']} | PnL: ${l['pnl']} | Entry: {l['entry_price']} | Exit: {l['exit_price']} | Cost/Size: ${l['amount']} | File: {l['source']}")

print("\n--- LARGEST LOSSES (> $2.00) ---")
large_losses = [l for l in unique_losses if l['pnl'] < -2.00]
print(f"Total losses worse than -$2.00: {len(large_losses)}")
for l in sorted(large_losses, key=lambda x: x['pnl'])[:25]:
    print(f"[{l['timestamp']}] {l['symbol']} {l['side']} | PnL: ${l['pnl']} | Entry: {l['entry_price']} | Exit: {l['exit_price']} | Reason: {l['reason']}")
