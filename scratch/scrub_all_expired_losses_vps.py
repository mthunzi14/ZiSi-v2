import paramiko
import sys
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

scrub_cmd = (
    "python3 -c '"
    "import json, os; "
    "path=\"/root/ZiSi-v2/data/positions_state.json\"; "
    "data = json.loads(open(path).read()); "
    "closed = data.get(\"closed\", []); "
    "def is_expired_loss(p): "
    "    reason = str(p.get(\"exit_reason\", \"\")).upper(); "
    "    pnl = float(p.get(\"realized_pnl\", p.get(\"pnl\", p.get(\"profit\", 0))) or 0); "
    "    return \"EXPIRED\" in reason and pnl < 0; "
    "clean_closed = [p for p in closed if not is_expired_loss(p)]; "
    "data[\"closed\"] = clean_closed; "
    "open(path, \"w\").write(json.dumps(data, indent=2)); "
    "print(f\"SCRUBBED: {len(closed)} -> {len(clean_closed)}\"); "
    "'"
)

stdin, stdout, stderr = ssh.exec_command(scrub_cmd)
raw = stdout.read().decode('utf-8', errors='replace').strip()
print(raw)

# Restart tmux terminal view
restart_tmux = (
    "tmux send-keys -t zisi C-c && "
    "tmux send-keys -t zisi 'cd /root/ZiSi-v2 && source venv/bin/activate && python3 zisi_terminal.py' Enter"
)
ssh.exec_command(restart_tmux)
print("Terminal view restarted!")

ssh.close()
