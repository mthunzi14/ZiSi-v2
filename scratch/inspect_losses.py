import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

cmd = (
    "python3 -c '"
    "import json; "
    "data = json.loads(open(\"/root/ZiSi-v2/data/positions_state.json\").read()); "
    "closed = data.get(\"closed\", []); "
    "print(f\"Total closed: {len(closed)}\"); "
    "reasons = set(str(p.get(\"exit_reason\", \"\")) for p in closed); "
    "print(f\"Unique exit reasons: {reasons}\"); "
    "losses = [p for p in closed if float(p.get(\"realized_pnl\", p.get(\"pnl\", p.get(\"profit\", 0))) or 0) < 0]; "
    "print(f\"Total loss positions: {len(losses)}\"); "
    "for l in losses[:15]: "
    "    print(f\"  Loss: {l.get(\"asset\",\"?\")} PnL={l.get(\"realized_pnl\", l.get(\"pnl\"))} Reason={l.get(\"exit_reason\")} Time={l.get(\"closed_at\", l.get(\"entry_time\"))}\"); "
    "'"
)

stdin, stdout, stderr = ssh.exec_command(cmd)
raw = stdout.read().decode('utf-8', errors='replace').strip()
print(raw)

ssh.close()
