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
        
        # Read the first few lines of wallet_0xeebde7a0_run1_clean.json
        f = sftp.file("/root/ZiSi-v2/wallet/wallet_0xeebde7a0_run1_clean.json", "r")
        content = f.read(5000).decode("utf-8")
        f.close()
        
        print("=== Run1 Clean Sample ===")
        print(content[:2500])
        
        sftp.close()
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
