import paramiko
import json
import os

def pull_vps_files():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to VPS via SFTP...")
        ssh.connect(hostname, username=username, password=password, timeout=30)
        sftp = ssh.open_sftp()
        
        # Paths on VPS
        vps_positions_path = "/root/ZiSi-v2/data/positions_state.json"
        vps_account_path = "/root/ZiSi-v2/data/account_state.json"
        
        # Local paths
        local_dir = r"c:\Users\mthun\Downloads\ZiSi-v2\data"
        local_positions_path = os.path.join(local_dir, "positions_state.json")
        local_account_path = os.path.join(local_dir, "account_state.json")
        
        print(f"Downloading positions_state.json to {local_positions_path}...")
        sftp.get(vps_positions_path, local_positions_path)
        
        print(f"Downloading account_state.json to {local_account_path}...")
        sftp.get(vps_account_path, local_account_path)
        
        sftp.close()
        ssh.close()
        print("SFTP Sync Completed Successfully.")
        
        # Read the downloaded positions_state.json
        with open(local_positions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        closed = data.get("closed", [])
        print(f"Total closed positions: {len(closed)}")
        
        # Sort by exit time to get the absolute latest
        parsed_positions = []
        for pos in closed:
            exit_time_str = pos.get("exit_time") or pos.get("close_time") or ""
            parsed_positions.append((exit_time_str, pos))
            
        # Print the last 10 closed positions
        print("\nLast 10 closed positions in positions_state.json:")
        for idx, (exit_time, pos) in enumerate(parsed_positions[-10:]):
            print(f"\n--- Position {idx+1} ---")
            print(f"Event Title: {pos.get('event_title')}")
            print(f"Direction: {pos.get('direction')}")
            print(f"Exit Time: {exit_time}")
            print(f"Entry Price: {pos.get('entry_price')}")
            print(f"Exit Price: {pos.get('exit_price')}")
            print(f"Entry Spot: {pos.get('entry_spot')}")
            print(f"Exit Spot / Live Spot: {pos.get('exit_spot') or pos.get('live_spot') or pos.get('current_price')}")
            print(f"Realized PnL: {pos.get('realized_pnl')}")
            print(f"Tranche: {pos.get('tranche') or 'Full'}")
            print(f"Exit Reason: {pos.get('exit_reason')}")
            
    except Exception as e:
        print(f"SSH Error: {e}")

if __name__ == "__main__":
    pull_vps_files()
