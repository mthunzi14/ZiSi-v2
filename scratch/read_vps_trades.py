import paramiko
import json

def get_vps_trades():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        # Read trades_2026-07-13.jsonl from the VPS
        sftp = ssh.open_sftp()
        filepath = "/root/ZiSi-v2/core/calibration_trades/trades_2026-07-13.jsonl"
        
        trades = []
        try:
            with sftp.file(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        trades.append(json.loads(line))
        except FileNotFoundError:
            print("File not found on VPS.")
            
        sftp.close()
        ssh.close()
        
        # Print trades in formatted way
        print(f"Parsed {len(trades)} trades from today:")
        for idx, t in enumerate(trades):
            print(f"{idx+1}. Asset={t.get('asset')} TF={t.get('timeframe')} Strategy={t.get('strategy')} Dir={t.get('direction')} EntryPrice={t.get('entry_price')} ExitPrice={t.get('exit_price')} PnL={t.get('pnl')} Result={t.get('result')} ExitReason={t.get('exit_reason')} Time={t.get('ts')}")
            
    except Exception as e:
        print(f"SSH Error: {e}")

if __name__ == "__main__":
    get_vps_trades()
