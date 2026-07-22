import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

stdin, stdout, stderr = ssh.exec_command('cat /root/ZiSi-v2/data/positions_state.json')
data = json.loads(stdout.read().decode('utf-8'))
closed = data.get("closed", [])
print(f"TOTAL CLOSED: {len(closed)}")
for i, pos in enumerate(closed):
    reason = str(pos.get("exit_reason", ""))
    pnl = float(pos.get("realized_pnl", pos.get("pnl", pos.get("profit", 0))) or 0)
    title = pos.get("event_title", "")
    direction = pos.get("direction", "")
    entry = pos.get("entry_price", 0)
    exit_p = pos.get("exit_price", 0)
    print(f"[{i+1:2d}] PnL: ${pnl:+.2f} | Dir: {direction:4s} | Entry: {entry:.3f} -> Exit: {exit_p:.3f} | Reason: {reason} | Title: {title}")

ssh.close()
