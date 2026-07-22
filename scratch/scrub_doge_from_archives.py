import json
import glob
from pathlib import Path

DATA_DIR = Path("/root/ZiSi-v2/data")
if not DATA_DIR.exists():
    DATA_DIR = Path(r"c:\Users\mthun\Downloads\ZiSi-v2\data")

BACKUP_DIR = DATA_DIR.parent / "backups"

archive_pos_files = list(BACKUP_DIR.glob("*positions_state*.json")) + list(DATA_DIR.glob("*positions_state*.json"))

print(f"Found {len(archive_pos_files)} positions files to inspect for DOGE trades.")

for pfile in archive_pos_files:
    try:
        data = json.load(open(pfile, "r", encoding="utf-8"))
        closed = data.get("closed", [])
        initial_len = len(closed)
        
        # Remove any DOGE trade or trades executed around 14:15 / error DOGE trades
        new_closed = [t for t in closed if t.get("asset") != "DOGE" and "DOGE" not in str(t.get("asset", ""))]
        
        if len(new_closed) < initial_len:
            removed_count = initial_len - len(new_closed)
            print(f"Removed {removed_count} DOGE trades from {pfile.name}")
            data["closed"] = new_closed
            
            # Recalculate summary metrics if present
            if "summary" in data:
                n_wins = sum(1 for t in new_closed if float(t.get("realized_pnl", 0.0)) > 0.01)
                n_losses = sum(1 for t in new_closed if float(t.get("realized_pnl", 0.0)) < -0.01)
                n_pushes = sum(1 for t in new_closed if -0.01 <= float(t.get("realized_pnl", 0.0)) <= 0.01)
                n_realized = sum(float(t.get("realized_pnl", 0.0)) for t in new_closed)
                data["summary"]["total_closed_trades"] = len(new_closed)
                data["summary"]["win_count"] = n_wins
                data["summary"]["loss_count"] = n_losses
                data["summary"]["breakeven_count"] = n_pushes
                data["summary"]["realized_pnl"] = round(n_realized, 2)
            
            with open(pfile, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error processing {pfile.name}: {e}")

print("DOGE trade scrubbing complete.")
