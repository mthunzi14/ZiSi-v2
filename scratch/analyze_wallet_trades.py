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
        
        # Read the first few lines of wallet_0xeebde7a0_history.json
        f = sftp.file("/root/ZiSi-v2/wallet/wallet_0xeebde7a0_history.json", "r")
        content = f.read(5000).decode("utf-8")
        f.close()
        
        print("=== History JSON Sample ===")
        print(content[:2000])
        
        # Also check resolved_winners_cache.json size/keys
        try:
            f = sftp.file("/root/ZiSi-v2/wallet/resolved_winners_cache.json", "r")
            win_sample = f.read(1000).decode("utf-8")
            f.close()
            print("\n=== Winners Cache Sample ===")
            print(win_sample)
        except Exception as e:
            print("Winners Cache read error:", e)
            
        sftp.close()
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
