import paramiko
import sys
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

cmd = (
    "python3 -c '"
    "import json, os; "
    "data = json.loads(open(\"/root/ZiSi-v2/data/positions_state.json\").read()); "
    "closed = data.get(\"closed\", []); "
    "expired = [p for p in closed if \"EXPIRED\" in str(p.get(\"exit_reason\", \"\")).upper() and float(p.get(\"realized_pnl\", p.get(\"pnl\", 0)) or 0) < 0]; "
    "print(f\"CLOSED: {len(closed)} | EXPIRED LOSSES REMAINING: {len(expired)}\"); "
    "'"
)

stdin, stdout, stderr = ssh.exec_command(cmd)
raw = stdout.read().decode('utf-8', errors='replace').strip()
print(raw)

ssh.close()
