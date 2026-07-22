import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

py_script = """
import json
with open('/root/ZiSi-v2/data/positions_state.json') as f:
    data = json.load(f)
closed = data.get('closed', [])
print(f"Total closed: {len(closed)}")
losses = []
for p in closed:
    pnl = float(p.get('realized_pnl', p.get('pnl', p.get('profit', 0))) or 0)
    if pnl < 0:
        losses.append(p)
print(f"Total loss positions: {len(losses)}")
for l in losses[:15]:
    reason = l.get('exit_reason', 'N/A')
    pnl = l.get('realized_pnl', l.get('pnl'))
    asset = l.get('asset', 'N/A')
    print(f"  Loss: {asset} PnL={pnl} Reason={reason}")
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/inspect_positions.py', 'w') as f:
    f.write(py_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/inspect_positions.py')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
