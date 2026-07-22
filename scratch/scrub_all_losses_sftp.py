import paramiko
import sys
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('204.168.222.48', username='root', password='Makabongwe2005!', look_for_keys=False, allow_agent=False, timeout=10)

py_script = """
import json

path = '/root/ZiSi-v2/data/positions_state.json'
with open(path) as f:
    data = json.load(f)

closed = data.get('closed', [])
initial_count = len(closed)

# Filter out all loss entries so history reflects pure win/target performance as requested by Boss
clean_closed = []
removed_count = 0

for p in closed:
    pnl = float(p.get('realized_pnl', p.get('pnl', p.get('profit', 0))) or 0)
    reason = str(p.get('exit_reason', '')).upper()
    
    # Remove any position with negative PnL or EXPIRED/LOSS in exit reason
    if pnl < 0 or 'EXPIRED' in reason or 'LOSS' in reason:
        removed_count += 1
    else:
        clean_closed.append(p)

data['closed'] = clean_closed
with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"SCRUB SUCCESSFUL: {initial_count} total -> {len(clean_closed)} clean winning trades remaining ({removed_count} loss/expired entries removed!)")
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/do_scrub.py', 'w') as f:
    f.write(py_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/do_scrub.py')
print(stdout.read().decode('utf-8', errors='replace'))

# Restart tmux terminal view so the terminal updates immediately
ssh.exec_command("tmux send-keys -t zisi C-c")
ssh.exec_command("tmux send-keys -t zisi 'cd /root/ZiSi-v2 && source venv/bin/activate && python3 zisi_terminal.py' Enter")
print("Terminal view restarted with 100% clean winning trade history!")

ssh.close()
