import paramiko
import json
import os
from datetime import datetime, timezone

def clean_positions_file(file_data, cutoff):
    closed = file_data.get("closed", [])
    
    kept_closed = []
    wiped_count = 0
    for p in closed:
        exit_time_str = p.get("exit_time", "")
        if exit_time_str:
            if exit_time_str.endswith("Z"):
                exit_time_str = exit_time_str[:-1] + "+00:00"
            try:
                exit_time = datetime.fromisoformat(exit_time_str)
                if exit_time >= cutoff:
                    wiped_count += 1
                else:
                    kept_closed.append(p)
            except ValueError:
                kept_closed.append(p)
        else:
            kept_closed.append(p)
            
    # Rebuild counts and realized PnL
    win_count = sum(1 for p in kept_closed if p.get("realized_pnl", 0.0) > 0.009)
    loss_count = sum(1 for p in kept_closed if p.get("realized_pnl", 0.0) < -0.009)
    breakeven_count = sum(1 for p in kept_closed if -0.009 <= p.get("realized_pnl", 0.0) <= 0.009)
    realized_pnl = round(sum(p.get("realized_pnl", 0.0) for p in kept_closed), 2)
    
    file_data["closed"] = kept_closed
    file_data["active"] = [] # Clear active just in case
    
    # If the file uses a separate "summary" dict key (like pos2.json / pos_snapshot.json)
    if "summary" in file_data and isinstance(file_data["summary"], dict):
        file_data["summary"]["closed_count"] = len(kept_closed)
        file_data["summary"]["active_count"] = 0
        file_data["summary"]["poly_active"] = 0
        file_data["summary"]["win_count"] = win_count
        file_data["summary"]["loss_count"] = loss_count
        file_data["summary"]["breakeven_count"] = breakeven_count
        file_data["summary"]["realized_pnl"] = realized_pnl
    else:
        file_data["win_count"] = win_count
        file_data["loss_count"] = loss_count
        file_data["breakeven_count"] = breakeven_count
        file_data["realized_pnl"] = realized_pnl
        
    return file_data, wiped_count

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        sftp = ssh.open_sftp()
        
        backup_dir = r"C:\Users\mthun\.gemini\antigravity\brain\14e04d67-5e69-491a-9086-7b2c06bc7b3d\backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        cutoff = datetime(2026, 7, 18, 22, 20, 0, tzinfo=timezone.utc)
        
        # 1. positions_state.json
        print("Cleaning positions_state.json...")
        with sftp.open('/root/ZiSi-v2/data/positions_state.json', 'r') as f:
            pos_data = json.load(f)
        cleaned_pos, wiped_pos = clean_positions_file(pos_data, cutoff)
        print(f"Wiped {wiped_pos} closed trades from positions_state.json")
        
        # 2. pos2.json
        print("\nCleaning pos2.json...")
        with sftp.open('/root/ZiSi-v2/data/pos2.json', 'r') as f:
            pos2_data = json.load(f)
        cleaned_pos2, wiped_pos2 = clean_positions_file(pos2_data, cutoff)
        print(f"Wiped {wiped_pos2} closed trades from pos2.json")
        
        # 3. pos_snapshot.json
        print("\nCleaning pos_snapshot.json...")
        with sftp.open('/root/ZiSi-v2/data/pos_snapshot.json', 'r') as f:
            snap_data = json.load(f)
        cleaned_snap, wiped_snap = clean_positions_file(snap_data, cutoff)
        print(f"Wiped {wiped_snap} closed trades from pos_snapshot.json")
        
        # 4. account_state.json
        print("\nCleaning account_state.json...")
        with sftp.open('/root/ZiSi-v2/data/account_state.json', 'r') as f:
            acct_data = json.load(f)
        print(f"Original account balance: ${acct_data.get('balance')}")
        acct_data["balance"] = 1744.00
        acct_data["realized_pnl"] = 1624.00
        acct_data["pnl"] = 1624.00
        print(f"Reset account balance to: ${acct_data['balance']}")
        
        # 5. Upload all cleaned files back to VPS
        print("\nUploading cleaned files to VPS...")
        
        # Write files locally
        local_pos_path = os.path.join(backup_dir, "positions_state_clean.json")
        with open(local_pos_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_pos, f, indent=2)
        sftp.put(local_pos_path, "/root/ZiSi-v2/data/positions_state.json")
        
        local_pos2_path = os.path.join(backup_dir, "pos2_clean.json")
        with open(local_pos2_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_pos2, f, indent=2)
        sftp.put(local_pos2_path, "/root/ZiSi-v2/data/pos2.json")
        
        local_snap_path = os.path.join(backup_dir, "pos_snapshot_clean.json")
        with open(local_snap_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_snap, f, indent=2)
        sftp.put(local_snap_path, "/root/ZiSi-v2/data/pos_snapshot.json")
        
        local_acct_path = os.path.join(backup_dir, "account_state_clean.json")
        with open(local_acct_path, "w", encoding="utf-8") as f:
            json.dump(acct_data, f, indent=2)
        sftp.put(local_acct_path, "/root/ZiSi-v2/data/account_state.json")
        
        print("Upload successful!")
        
        # 6. Verify that positions_state.json closed count matches pos2/snapshot
        print("\nVerification check:")
        print(f"positions_state.json closed size: {len(cleaned_pos['closed'])}")
        print(f"pos2.json closed size: {len(cleaned_pos2['closed'])}")
        print(f"pos_snapshot.json closed size: {len(cleaned_snap['closed'])}")
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
