import paramiko
import json

def run_analysis():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to VPS via SSH...")
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        # Python script to execute on the VPS
        py_code = """
import json, os
files = [
    '/root/ZiSi-v2/core/calibration_trades/trades_2026-06-14.jsonl',
    '/root/ZiSi-v2/core/calibration_trades/trades_2026-06-15.jsonl',
    '/root/ZiSi-v2/core/calibration_trades/trades_2026-06-16.jsonl',
    '/root/ZiSi-v2/core/calibration_trades/trades_2026-06-22.jsonl',
    '/root/ZiSi-v2/core/calibration_trades/trades_2026-06-23.jsonl'
]
all_trades = []
for f in files:
    if os.path.exists(f):
        with open(f) as fh:
            for line in fh:
                try: 
                    all_trades.append(json.loads(line))
                except: 
                    pass
sig_trades = [t for t in all_trades if t.get('strategy') == 'SIG']
print('Total SIG trades:', len(sig_trades))
wins = [t for t in sig_trades if t.get('result') == 'WIN']
losses = [t for t in sig_trades if t.get('result') == 'LOSS']
print(f'Win Rate: {len(wins)}W - {len(losses)}L ({len(wins)/len(sig_trades)*100:.2f}%)' if sig_trades else 'No trades')
prices = [t.get('entry_price') for t in sig_trades if t.get('entry_price') is not None]
if prices: 
    print(f'Prices: Min={min(prices):.4f}, Max={max(prices):.4f}, Avg={sum(prices)/len(prices):.4f}')
bands = [
    ('<0.30', lambda p: p < 0.30),
    ('0.30-0.40', lambda p: 0.30 <= p < 0.40),
    ('0.40-0.50', lambda p: 0.40 <= p < 0.50),
    ('0.50-0.60', lambda p: 0.50 <= p < 0.60),
    ('0.60-0.70', lambda p: 0.60 <= p < 0.70),
    ('>=0.70', lambda p: p >= 0.70)
]
for label, check in bands:
    bt = [t for t in sig_trades if check(t.get('entry_price', 0))]
    if bt:
        bw = sum(1 for t in bt if t.get('result') == 'WIN')
        bl = sum(1 for t in bt if t.get('result') == 'LOSS')
        print(f'{label}: {len(bt)} trades | {bw}W - {bl}L ({bw/len(bt)*100:.2f}%)')
"""
        # Write script to VPS via SFTP
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/analyze_vps_sig.py', 'w') as f:
            f.write(py_code)
        sftp.close()
        
        # Execute script on VPS
        stdin, stdout, stderr = ssh.exec_command("/root/ZiSi-v2/venv/bin/python3 /tmp/analyze_vps_sig.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        ssh.close()
    except Exception as e:
        print(f"Error running analysis: {e}")

if __name__ == "__main__":
    run_analysis()
