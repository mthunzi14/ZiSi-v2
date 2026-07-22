import paramiko
import sys

hostname = "204.168.222.48"
username = "root"
password = "Makabongwe2005!"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def safe_print(msg: str):
    try:
        sys.stdout.buffer.write((msg + "\n").encode('utf-8'))
        sys.stdout.buffer.flush()
    except Exception:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

try:
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    
    commands = [
        "tmux new-session -d -s zisi 2>/dev/null || true",
        "tmux send-keys -t zisi C-c",
        "tmux send-keys -t zisi 'cd /root/ZiSi-v2 && source venv/bin/activate && python3 zisi_terminal.py' Enter",
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        if out:
            safe_print(f"  OUTPUT: {out}")
            
    stdin, stdout, stderr = ssh.exec_command("tmux list-sessions")
    safe_print("Tmux Sessions:\n" + stdout.read().decode('utf-8', errors='replace').strip())
    
finally:
    ssh.close()
