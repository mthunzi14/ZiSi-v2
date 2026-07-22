import paramiko
import json

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        sftp = ssh.open_sftp()
        
        # Check positions_state.json
        print("--- positions_state.json closed BNB ---")
        with sftp.open('/root/ZiSi-v2/data/positions_state.json', 'r') as f:
            data = json.load(f)
        closed = data.get("closed", [])
        active = data.get("active", [])
        
        bnb_closed = [p for p in closed if "BNB" in p.get("event_title", "")]
        for p in bnb_closed:
            print(f"Closed: {p.get('entry_time')} | PnL: ${p.get('realized_pnl')} | Size: ${p.get('size')} | Entry: {p.get('entry_price')} | Exit: {p.get('exit_price')}")
            
        print("\n--- positions_state.json active BNB ---")
        bnb_active = [p for p in active if "BNB" in p.get("event_title", "")]
        for p in bnb_active:
            print(f"Active: {p.get('entry_time')} | Size: ${p.get('size')} | Entry: {p.get('entry_price')}")
            
        # Check pos2.json
        print("\n--- pos2.json BNB ---")
        try:
            with sftp.open('/root/ZiSi-v2/data/pos2.json', 'r') as f2:
                data2 = json.load(f2)
            for k, p in data2.items():
                if "BNB" in p.get("event_title", "") or "BNB" in k:
                    print(f"pos2: {k} | {p.get('entry_time')} | Size: ${p.get('amount_spent')} | Entry: {p.get('entry_price')}")
        except Exception as e:
            print(f"No pos2.json or error: {e}")
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
