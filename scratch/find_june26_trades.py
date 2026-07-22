import paramiko

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    vps_script = """import json
import os

path = "/root/ZiSi-v2/data/potential_trades.json"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        print(f.read())
else:
    print("Not found:", path)
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30, banner_timeout=30)
        sftp = ssh.open_sftp()
        vps_path = "/root/ZiSi-v2/scratch/find_june26_trades.py"
        with sftp.file(vps_path, "w") as f:
            f.write(vps_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("/root/ZiSi-v2/venv/bin/python3 /root/ZiSi-v2/scratch/find_june26_trades.py")
        print("=== VPS POTENTIAL TRADES ===")
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
    except Exception as e:
        print("Error:", e)
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
