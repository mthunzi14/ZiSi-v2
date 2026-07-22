import json
from pathlib import Path
from datetime import datetime, timezone

def main():
    pos_path = Path("data/positions_state.json")
    acc_path = Path("data/account_state.json")
    
    if not pos_path.exists():
        print("positions_state.json does not exist!")
        return

    # Load positions state
    data = json.loads(pos_path.read_text(encoding="utf-8"))
    
    active = data.get("active", [])
    closed = data.get("closed", [])
    
    # Filter active and closed
    clean_active = [p for p in active if str(p.get("regime", "UNKNOWN")).upper() != "UNKNOWN"]
    clean_closed = [p for p in closed if str(p.get("regime", "UNKNOWN")).upper() != "UNKNOWN"]
    
    removed_active_count = len(active) - len(clean_active)
    removed_closed_count = len(closed) - len(clean_closed)
    
    print(f"Removed active positions: {removed_active_count}")
    print(f"Removed closed positions: {removed_closed_count}")
    
    # Recalculate summary stats
    realized_pnl = round(sum(float(p.get("realized_pnl", 0.0)) for p in clean_closed), 2)
    unrealized_pnl = round(sum(float(p.get("unrealized_pnl", 0.0)) for p in clean_active), 2)
    win_count = sum(1 for p in clean_closed if float(p.get("realized_pnl", 0.0)) > 0.009)
    loss_count = sum(1 for p in clean_closed if float(p.get("realized_pnl", 0.0)) < -0.009)
    breakeven_count = sum(1 for p in clean_closed if -0.009 <= float(p.get("realized_pnl", 0.0)) <= 0.009)
    
    summary = {
        "active_count": len(clean_active),
        "poly_active": len([p for p in clean_active if p.get("market") == "POLYMARKET"]),
        "closed_count": len(clean_closed),
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": realized_pnl,
        "win_count": win_count,
        "loss_count": loss_count,
        "breakeven_count": breakeven_count
    }
    
    new_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "source": data.get("source", "polymarket"),
        "summary": summary,
        "active": clean_active,
        "closed": clean_closed
    }
    
    # Save positions state back
    pos_path.write_text(json.dumps(new_data, indent=2), encoding="utf-8")
    print("Successfully updated positions_state.json")
    
    # Reconcile account state
    if acc_path.exists():
        acc_data = json.loads(acc_path.read_text(encoding="utf-8"))
        starting_balance = float(acc_data.get("starting_balance", 100.0))
        new_balance = round(starting_balance + realized_pnl, 2)
        
        acc_data["balance"] = new_balance
        acc_data["pnl"] = round(new_balance - starting_balance, 2)
        acc_data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        acc_data["last_change_reason"] = "Wiped UNKNOWN regime poison trades"
        
        acc_path.write_text(json.dumps(acc_data, indent=2), encoding="utf-8")
        print(f"Successfully updated account_state.json. New balance: ${new_balance}, PnL: ${acc_data['pnl']}")

if __name__ == "__main__":
    main()
