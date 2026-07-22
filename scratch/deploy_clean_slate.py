import paramiko
import sys
import json
import time

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
    safe_print(f"Connecting to VPS {hostname} for Clean Slate Reset & Deployment...")
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    safe_print("Connected successfully!")

    # 1. Stop PM2 Core Engine
    safe_print("Stopping ZiSi-Core-Engine on PM2...")
    ssh.exec_command("pm2 stop ZiSi-Core-Engine")

    # 2. Archive current test session
    ts_str = time.strftime("%Y%m%d_%H%M%S")
    archive_cmd = f"mkdir -p /root/ZiSi-v2/backups && cp /root/ZiSi-v2/data/positions_state.json /root/ZiSi-v2/backups/archive_session_test_{ts_str}.json"
    safe_print(f"Archiving test session: {archive_cmd}")
    ssh.exec_command(archive_cmd)

    # 3. Pull latest code from main
    git_cmds = [
        "cd /root/ZiSi-v2 && git fetch origin",
        "cd /root/ZiSi-v2 && git checkout -f main",
        "cd /root/ZiSi-v2 && git reset --hard origin/main",
        "cd /root/ZiSi-v2 && find . -name '*.pyc' -delete",
    ]
    for cmd in git_cmds:
        safe_print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        if out:
            safe_print(f"  OUTPUT: {out}")

    # 4. Inject Chainlink Data Streams credentials to VPS .env if missing
    env_append = """
# ===== CHAINLINK DATA STREAMS =====
CHAINLINK_DS_CLIENT_ID=128265c1-2583-4982-9e15-42100a4317b3
CHAINLINK_DS_CLIENT_SECRET=qNUyra94KkSO6NBoOq6e0zwGNd2Nz7SDyrl9FVkjiLEm655te1a0Eiy8Am5tHoLJKG6C328ErA85o8Ew6IZ0yrVZtegIQm64g0u5EWglQPR694CB8hxhHS5hev71Few1
CHAINLINK_DS_CANDLESTICK_API_KEY=c564fc42-dda0-4173-89f5-67716542829c
CHAINLINK_DS_REST_URL=https://api.chain.link
CHAINLINK_DS_WS_URL=wss://ws.stream.chain.link
"""
    check_env_cmd = "grep -q 'CHAINLINK_DS_CLIENT_ID' /root/ZiSi-v2/.env || echo 'MISSING'"
    stdin, stdout, stderr = ssh.exec_command(check_env_cmd)
    if "MISSING" in stdout.read().decode():
        safe_print("Appending Chainlink DS credentials to VPS .env...")
        sftp = ssh.open_sftp()
        with sftp.file('/root/ZiSi-v2/.env', 'a') as f:
            f.write(env_append)
        sftp.close()

    # 5. Clean Slate Reset of database files to $50.00 USDC
    clean_positions = {
        "positions": {},
        "closed": [],
        "summary": {
            "active_count": 0,
            "poly_active": 0,
            "closed_count": 0,
            "unrealized_pnl": 0.0,
            "realized_pnl": 0.0,
            "win_count": 0,
            "loss_count": 0,
            "breakeven_count": 0
        }
    }
    
    clean_account = {
        "balance": 50.00,
        "starting_balance": 50.00,
        "peak_balance": 50.00,
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    clean_antifragile = {
        "aggressiveness": 1.0,
        "tier": "NORMAL",
        "consecutive_losses": 0,
        "history": []
    }

    safe_print("Writing Clean Slate database files ($50.00 USDC starting balance)...")
    sftp = ssh.open_sftp()
    with sftp.file('/root/ZiSi-v2/data/positions_state.json', 'w') as f:
        f.write(json.dumps(clean_positions, indent=2))
    with sftp.file('/root/ZiSi-v2/data/account_state.json', 'w') as f:
        f.write(json.dumps(clean_account, indent=2))
    with sftp.file('/root/ZiSi-v2/data/antifragile_state.json', 'w') as f:
        f.write(json.dumps(clean_antifragile, indent=2))
    sftp.close()

    # 6. Restart PM2 Core Engine
    safe_print("Restarting ZiSi-Core-Engine via PM2...")
    stdin, stdout, stderr = ssh.exec_command("pm2 restart ZiSi-Core-Engine")
    safe_print("PM2 Output:\n" + stdout.read().decode('utf-8', errors='replace').strip())

    # 7. Restart Tmux Terminal Dashboard
    safe_print("Restarting tmux session zisi...")
    ssh.exec_command("tmux new-session -d -s zisi 2>/dev/null || true")
    ssh.exec_command("tmux send-keys -t zisi C-c")
    ssh.exec_command("tmux send-keys -t zisi 'cd /root/ZiSi-v2 && source venv/bin/activate && python3 zisi_terminal.py' Enter")

    # 8. Verify status
    time.sleep(3)
    safe_print("\n--- Clean Slate VPS Status Verification ---")
    stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && git log -1 --oneline && pm2 status && cat data/account_state.json")
    safe_print(stdout.read().decode('utf-8', errors='replace').strip())

finally:
    ssh.close()
