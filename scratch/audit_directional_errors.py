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
    ssh.connect(hostname=hostname, username=username, password=password, timeout=15, look_for_keys=False, allow_agent=False)
    
    cmd = (
        "python3 -c '"
        "import json; "
        "data = json.loads(open(\"/root/ZiSi-v2/data/positions_state.json\").read()); "
        "closed = data.get(\"closed\", []); "
        "print(f\"CLOSED POSITIONS COUNT: {len(closed)}\"); "
        "for p in closed: "
        "    reason = str(p.get(\"exit_reason\", \"\")); "
        "    title = p.get(\"event_title\", \"\"); "
        "    if \"loss\" in reason.lower() or \"expired\" in reason.lower(): "
        "        print(f\"TITLE: {title} | REASON: {reason} | DIR: {p.get(\"direction\")} | ENTRY: {p.get(\"entry_price\")} -> EXIT: {p.get(\"exit_price\")}\"); "
        "'"
    )
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raw = stdout.read().decode('utf-8', errors='replace').strip()
    safe_print(raw)
    
finally:
    ssh.close()
