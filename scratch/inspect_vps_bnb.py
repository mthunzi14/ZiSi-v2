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
            
        closed = data.get("closed", [])
        # Find the parent of the BNB match
        parent_id = "zisi_61ada4f755b3"
        parent_pos = [p for p in closed if p.get("order_id") == parent_id]
        
        if not parent_pos:
            # Maybe it's in the active positions?
            active = data.get("active", [])
            parent_pos = [p for p in active if p.get("order_id") == parent_id]
            
        print(f"Parent pos count: {len(parent_pos)}")
        if parent_pos:
            print(json.dumps(parent_pos[0], indent=2))
        else:
            # Let's search the file content as a string
            f.seek(0)
            text = f.read().decode('utf-8')
            print("Is parent ID present in text?", parent_id in text)
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
