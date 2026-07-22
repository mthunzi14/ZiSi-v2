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
    "data = json.loads(open(path).read()) if os.path.exists(path) else {}; "
    "closed = data.get(\"closed\", []); "
    "print(f\"TOTAL CLOSED: {len(closed)}\"); "
    "expired = [p for p in closed if \"expired\" in str(p.get(\"exit_reason\", \"\")).lower() or \"expired\" in str(p.get(\"status\", \"\")).lower()]; "
    "print(f\"EXPIRED LOSSES: {len(expired)}\"); "
    "for p in expired: "
    "    print(f\"  EXPIRED: {p.get(\"event_title\")} | ExitReason: {p.get(\"exit_reason\")} | PnL: {p.get(\"realized_pnl\", p.get(\"pnl\"))}\"); "
    "'"
)

stdin, stdout, stderr = ssh.exec_command(cmd)
raw = stdout.read().decode('utf-8', errors='replace').strip()
print(raw)

ssh.close()
