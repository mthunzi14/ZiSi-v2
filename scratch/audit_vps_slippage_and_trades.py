import paramiko
import sys
import json

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

    cmd = "cat /root/ZiSi-v2/data/positions_state.json"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raw = stdout.read().decode('utf-8')
    data = json.loads(raw)
    closed = data.get("closed", [])
    active = data.get("active", [])
    print(f"ACTIVE: {len(active)} | CLOSED: {len(closed)}")
    
    for i, p in enumerate(closed):
        print(f"[{i+1}] {p}")
        
    ssh.close()
except Exception as e:
    print(f"ERROR: {e}")
