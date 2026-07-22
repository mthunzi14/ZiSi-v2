import paramiko
import base64

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    # Python code to be executed on the VPS
    vps_code = """
import json
from pathlib import Path
from datetime import datetime, timezone

def clean_file(path_str):
    pos_path = Path(path_str)
    if not pos_path.exists():
        print(f"{path_str} does not exist!")
        return None
    try:
        data = json.loads(pos_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Failed to parse {path_str}: {e}")
        return None
        
    active = data.get('active', [])
    closed = data.get('closed', [])
    
    clean_active = [p for p in active if str(p.get('regime', 'UNKNOWN')).upper() != 'UNKNOWN']
    clean_closed = [p for p in closed if str(p.get('regime', 'UNKNOWN')).upper() != 'UNKNOWN']
    
    removed_active = len(active) - len(clean_active)
    removed_closed = len(closed) - len(clean_closed)
    print(f"Wiped {path_str}: removed {removed_active} active, {removed_closed} closed")
    
    realized_pnl = round(sum(float(p.get('realized_pnl', 0.0)) for p in clean_closed), 2)
    unrealized_pnl = round(sum(float(p.get('unrealized_pnl', 0.0)) for p in clean_active), 2)
    win_count = sum(1 for p in clean_closed if float(p.get('realized_pnl', 0.0)) > 0.009)
    loss_count = sum(1 for p in clean_closed if float(p.get('realized_pnl', 0.0)) < -0.009)
    breakeven_count = sum(1 for p in clean_closed if -0.009 <= float(p.get('realized_pnl', 0.0)) <= 0.009)
    
    summary = {
        'active_count': len(clean_active),
        'poly_active': len([p for p in clean_active if p.get('market') == 'POLYMARKET']),
        'closed_count': len(clean_closed),
        'unrealized_pnl': unrealized_pnl,
        'realized_pnl': realized_pnl,
        'win_count': win_count,
        'loss_count': loss_count,
        'breakeven_count': breakeven_count
    }
    
    data['summary'] = summary
    data['active'] = clean_active
    data['closed'] = clean_closed
    data['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    pos_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return realized_pnl

def clean_account(realized_pnl):
    acc_path = Path('/root/ZiSi-v2/data/account_state.json')
    if not acc_path.exists():
        return
    acc_data = json.loads(acc_path.read_text(encoding='utf-8'))
    starting_balance = float(acc_data.get('starting_balance', 100.0))
    new_balance = round(starting_balance + realized_pnl, 2)
    acc_data['balance'] = new_balance
    acc_data['pnl'] = round(new_balance - starting_balance, 2)
    acc_data['last_updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    acc_data['last_change_reason'] = 'Wiped UNKNOWN regime poison trades'
    acc_path.write_text(json.dumps(acc_data, indent=2), encoding='utf-8')
    print(f"Updated account_state.json: balance=${new_balance}, pnl=${acc_data['pnl']}")

realized = clean_file('/root/ZiSi-v2/data/positions_state.json')
if realized is not None:
    clean_account(realized)
clean_file('/root/ZiSi-v2/data/pos2.json')
clean_file('/root/ZiSi-v2/data/pos_snapshot.json')
"""

    b64_code = base64.b64encode(vps_code.encode('utf-8')).decode('utf-8')
    cmd = f"python3 -c \"import base64; exec(base64.b64decode('{b64_code}').decode('utf-8'))\""
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to VPS via SSH...")
        ssh.connect(hostname, username=username, password=password, timeout=30)
        print("Executing VPS database sanitization...")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        
        print("--- stdout ---")
        print(out)
        print("--- stderr ---")
        print(err)
        
        ssh.close()
    except Exception as e:
        print(f"SSH Error: {e}")

if __name__ == "__main__":
    main()
