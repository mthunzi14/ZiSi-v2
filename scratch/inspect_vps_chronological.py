import paramiko
import json
from datetime import datetime, timezone

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        sftp = ssh.open_sftp()
        with sftp.open('/root/ZiSi-v2/data/positions_state.json', 'r') as f:
            data = json.load(f)
            
        closed = data.get("closed", [])
        
        # Sort closed trades in chronological order by entry_time or exit_time
        # Since they are stored newest-first, we can just reverse the list
        closed_sorted = list(reversed(closed))
        
        # Filter for trades closed after 2026-07-18T21:40:00+00:00 (which is 23:40 SAST)
        cutoff = datetime(2026, 7, 18, 21, 40, 0, tzinfo=timezone.utc)
        
        filtered = []
        for p in closed_sorted:
            exit_time_str = p.get("exit_time", "")
            if exit_time_str:
                if exit_time_str.endswith("Z"):
                    exit_time_str = exit_time_str[:-1] + "+00:00"
                try:
                    exit_time = datetime.fromisoformat(exit_time_str)
                    if exit_time >= cutoff:
                        filtered.append((exit_time, p))
                except ValueError:
                    pass
                    
        print(f"Total tranche trades in this session (chronological order): {len(filtered)}")
        for idx, (exit_time, p) in enumerate(filtered):
            # Convert exit_time to SAST (UTC+2) for printing
            exit_sast = exit_time.astimezone(timezone(datetime.now().astimezone().utcoffset()))
            sast_str = exit_sast.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{idx:02d} | {sast_str} SAST | {p.get('asset')} | {p.get('tranche')} | {p.get('direction')} | Size: ${p.get('size')} | Entry: {p.get('entry_price')} | Exit: {p.get('exit_price')} | PnL: ${p.get('realized_pnl'):+.2f} | Reason: {p.get('exit_reason')}")
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
