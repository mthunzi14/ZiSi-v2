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
    safe_print(f"Connecting to VPS {hostname} for position scrub & deployment...")
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    safe_print("Connected successfully!")
    
    # 1. Scrub dormant active positions in positions_state.json
    scrub_cmd = (
        "python3 -c '"
        "import json, time; "
        "path=\"/root/ZiSi-v2/data/positions_state.json\"; "
        "data=json.loads(open(path).read()) if __import__(\"os\").path.exists(path) else {}; "
        "data[\"active\"] = []; "
        "open(path, \"w\").write(json.dumps(data, indent=2))'"
    )
    safe_print("Scrubbing active positions...")
    ssh.exec_command(scrub_cmd)
    
    # 2. Pre-populate oi_history.json with all 8 assets
    oi_cmd = (
        "python3 -c '"
        "import json, time; "
        "path=\"/root/ZiSi-v2/data/oi_history.json\"; "
        "now=time.time(); "
        "assets=[\"BTC\",\"ETH\",\"SOL\",\"XRP\",\"DOGE\",\"BNB\",\"HYPE\",\"LINK\"]; "
        "payload = {a: [[now-300, 1000000.0], [now-150, 1005000.0], [now, 1010000.0]] for a in assets}; "
        "open(path, \"w\").write(json.dumps(payload, indent=2))'"
    )
    safe_print("Pre-populating OI history for all 8 assets...")
    ssh.exec_command(oi_cmd)
    
    # 3. Pull latest main and restart PM2 + tmux
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
            
    safe_print("\n--- Verifying VPS Process & Clean Positions Status ---")
    stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && git log -1 --oneline && pm2 status")
    res = stdout.read().decode('utf-8', errors='replace').strip()
    safe_print(res)
    
finally:
    ssh.close()
