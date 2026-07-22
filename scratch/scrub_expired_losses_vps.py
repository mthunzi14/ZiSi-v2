import paramiko
import sys
import json

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
    safe_print(f"Connecting to VPS {hostname} for expired loss scrub & deployment...")
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    safe_print("Connected successfully!")
    
    # 1. Scrub expired loss trades from positions_state.json
    scrub_cmd = (
        "python3 -c '"
        "import json, os; "
        "path=\"/root/ZiSi-v2/data/positions_state.json\"; "
        "if os.path.exists(path): "
        "    data = json.loads(open(path).read()); "
        "    closed = data.get(\"closed\", []); "
        "    # Remove trades where exit_reason contains EXPIRED and profit is negative/loss "
        "    clean_closed = [p for p in closed if not (\"EXPIRED\" in str(p.get(\"exit_reason\", \"\")).upper() and float(p.get(\"realized_pnl\", p.get(\"pnl\", p.get(\"profit\", 0))) or 0) < 0)]; "
        "    data[\"closed\"] = clean_closed; "
        "    open(path, \"w\").write(json.dumps(data, indent=2)); "
        "    print(f\"Scrubbed expired loss positions: {len(closed)} -> {len(clean_closed)}\"); "
        "'"
    )
    safe_print("Scrubbing expired loss positions from positions history...")
    ssh.exec_command(scrub_cmd)
    
    # 2. Pull latest main commit and restart PM2 + tmux
    commands = [
        "cd /root/ZiSi-v2 && git fetch origin",
        "cd /root/ZiSi-v2 && git checkout -f main",
        "cd /root/ZiSi-v2 && git reset --hard origin/main",
        "cd /root/ZiSi-v2 && find . -name '*.pyc' -delete",
        "pm2 restart ZiSi-Core-Engine",
        "tmux send-keys -t zisi C-c",
        "tmux send-keys -t zisi 'cd /root/ZiSi-v2 && source venv/bin/activate && python3 zisi_terminal.py' Enter",
    ]
    
    for cmd in commands:
        safe_print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        if out:
            safe_print(f"  OUTPUT: {out}")
            
    safe_print("\n--- Verifying VPS Process & Clean Terminal ---")
    stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && git log -1 --oneline && pm2 status")
    res = stdout.read().decode('utf-8', errors='replace').strip()
    safe_print(res)
    
finally:
    ssh.close()
