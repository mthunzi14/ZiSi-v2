import paramiko
import sys
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

cmd = (
    "python3 -c '"
    "import json, os; "
    "path=\"/root/ZiSi-v2/data/positions_state.json\"; "
    "data = json.loads(open(path).read()); "
    "closed = data.get(\"closed\", []); "
    "for p in closed: "
    "    reason = str(p.get(\"exit_reason\", \"\")).upper(); "
    "    pnl = p.get(\"realized_pnl\", p.get(\"pnl\", p.get(\"profit\", 0))); "
    "    if \"EXPIRED\" in reason or \"LOSS\" in reason: "
    "        print(f\"ID: {p.get(\"id\")} | Reason: {reason} | PnL: {pnl} (type={type(pnl)})\"); "
    "'"
)

stdin, stdout, stderr = ssh.exec_command(cmd)
raw = stdout.read().decode('utf-8', errors='replace').strip()
print(raw)

ssh.close()
