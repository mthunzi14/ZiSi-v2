import paramiko
from pathlib import Path

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    files_to_sync = [
        "data/positions_state.json",
        "data/account_state.json",
        "data/antifragile_state.json"
    ]
    
    local_root = Path(__file__).resolve().parent.parent
    
    print(f"Connecting to {hostname} via SFTP...")
    transport = paramiko.Transport((hostname, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    for f_rel in files_to_sync:
        local_path = local_root / f_rel
        remote_path = f"/root/ZiSi-v2/{f_rel}"
        
        if not local_path.exists():
            print(f"Local file {local_path} does not exist!")
            continue
            
        print(f"Uploading {f_rel} -> {remote_path}...")
        sftp.put(str(local_path), remote_path)
        
    sftp.close()
    transport.close()
    print("Upload complete!")

if __name__ == "__main__":
    main()
