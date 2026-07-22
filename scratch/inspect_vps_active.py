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
        
        with sftp.open('/root/ZiSi-v2/data/positions_state.json', 'r') as f:
            data = json.load(f)
            
        active = data.get("active", [])
        print(f"Total active positions: {len(active)}")
        for idx, p in enumerate(active):
            print(f"- {idx}: {p.get('order_id')} | {p.get('event_title')} | {p.get('direction')} | Size: {p.get('amount_spent')}")
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
