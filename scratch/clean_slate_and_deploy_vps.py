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
    safe_print(f"Connecting to VPS {hostname} for Clean Slate & FAIR_VALUE_MODE Deployment...")
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    safe_print("Connected successfully!")
    
    # 1. Clean slate positions_state.json
    clean_pos_cmd = (
        "python3 -c '"
        "import json, os; "
        "path=\"/root/ZiSi-v2/data/positions_state.json\"; "
        "data={\"active\": [], \"closed\": []}; "
        "open(path, \"w\").write(json.dumps(data, indent=2))'"
    )
    safe_print("Resetting positions_state.json to clean slate...")
    ssh.exec_command(clean_pos_cmd)
    
    # 2. Reset balance to 50.00 USDC in account_state.json
    clean_acc_cmd = (
        "python3 -c '"
        "import json, time, os; "
        "path=\"/root/ZiSi-v2/data/account_state.json\"; "
        "data={\"balance\": 50.00, \"starting_balance\": 50.00, \"equity\": 50.00, \"peak_balance\": 50.00, \"history\": [{\"timestamp\": time.time(), \"balance\": 50.00, \"equity\": 50.00}]}; "
        "open(path, \"w\").write(json.dumps(data, indent=2))'"
    )
    safe_print("Resetting account balance to 50.00 USDC clean slate...")
    ssh.exec_command(clean_acc_cmd)

    # 3. Reset rolling slippage and anti-fragile states
    clean_misc_cmd = (
        "python3 -c '"
        "import json, os; "
        "for fname in [\"slippage_log.json\", \"antifragile_state.json\"]: "
        "    p = f\"/root/ZiSi-v2/data/{fname}\"; "
        "    if os.path.exists(p): os.remove(p)'"
    )
    safe_print("Cleaning slippage and anti-fragile states...")
    ssh.exec_command(clean_misc_cmd)
    
    # 4. Pre-populate oi_history.json with all 8 assets
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
    
    # 5. Pull latest main commit and restart PM2 + tmux
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
            
    safe_print("\n--- Verifying VPS Process & Clean Balance ---")
    stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && git log -1 --oneline && pm2 status")
    res = stdout.read().decode('utf-8', errors='replace').strip()
    safe_print(res)
    
finally:
    ssh.close()
