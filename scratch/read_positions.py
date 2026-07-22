import paramiko
import json

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30, banner_timeout=30)
        sftp = ssh.open_sftp()
        f = sftp.file("/root/ZiSi-v2/data/positions_state.json", "r")
        content = f.read().decode("utf-8")
        f.close()
        sftp.close()
        
        data = json.loads(content)
        closed = data.get("closed", [])
        print(f"Total closed positions: {len(closed)}")
        
        for i, pos in enumerate(closed):
            print(f"Position {i+1}:")
            print(f"  Title: {pos.get('event_title')}")
            print(f"  Strategy: {pos.get('strategy_type')}")
            print(f"  Direction: {pos.get('direction')}")
            print(f"  PnL: {pos.get('unrealized_pnl')} | {pos.get('pnl')}")
            print(f"  Reason: {pos.get('exit_reason')}")
            print(f"  Open Time: {pos.get('entry_time_sast')} | Close Time: {pos.get('exit_time_sast')}")
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
