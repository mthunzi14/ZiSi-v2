import json

path = "/root/ZiSi-v2/data/positions_state.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

target_ids = [
    "zisi_0e3f88d2a13e", # BNB unknown
    "zisi_ce9635c1c214", # DOGE unknown (with correct ID)
    "zisi_6488d5716bbf", # XRP loss
    "zisi_e72b8cb4de96", # SOL loss
    "zisi_d7c52c238ef4", # ETH loss
    "zisi_d73a81dbe565"  # BTC loss
]

print("--- PNL TO REVERT ---")
total_revert_pnl = 0.0
wins_to_remove = 0
losses_to_remove = 0
breakevens_to_remove = 0

for p in data.get("closed", []):
    oid = p.get("order_id", "")
    p_oid = p.get("parent_order_id", "")
    
    if any(tid in oid or tid in p_oid for tid in target_ids):
        pnl = float(p.get("realized_pnl", 0.0))
        print(f"Match: ID={oid} | PnL={pnl} | Regime={p.get('regime')} | Title={p.get('event_title')}")
        total_revert_pnl += pnl
        if pnl > 0.01:
            wins_to_remove += 1
        elif pnl < -0.01:
            losses_to_remove += 1
        else:
            breakevens_to_remove += 1

print(f"Total PnL to Revert: {total_revert_pnl}")
print(f"Wins to remove: {wins_to_remove}")
print(f"Losses to remove: {losses_to_remove}")
print(f"Breakevens to remove: {breakevens_to_remove}")
