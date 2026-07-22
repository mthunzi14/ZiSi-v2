import paramiko
import sys

hostname = "204.168.222.48"
username = "root"
password = "Makabongwe2005!"

def safe_print(msg: str):
    try:
        sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
        sys.stdout.buffer.flush()
    except Exception:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    safe_print("Connecting to VPS to run recent trade analysis...")
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    
    # Run fetch, reset, and execute script
    stdin, stdout, stderr = ssh.exec_command(
        "cd /root/ZiSi-v2 && git fetch origin && git reset --hard origin/main && python3 scratch/inspect_vps_positions.py"
    )
    res = stdout.read().decode('utf-8', errors='replace').strip()
    safe_print(res)
    
finally:
    ssh.close()
