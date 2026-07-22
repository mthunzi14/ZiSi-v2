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
    
    cmd = "cat /root/ZiSi-v2/data/positions_state.json"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raw = stdout.read().decode('utf-8', errors='replace')
    data = json.loads(raw)
    closed = data.get("closed", [])
    
    safe_print(f"=== TOTAL CLOSED TRANCHES: {len(closed)} ===")
    
    wins = 0
    losses = 0
    be = 0
    total_pnl = 0.0
    
    by_asset = {}
    
    for i, p in enumerate(closed):
        t = p.get("event_title", "")
        pnl = float(p.get("pnl", p.get("realized_pnl", p.get("profit", 0))) or 0)
        reason = p.get("exit_reason", "N/A")
        ep = float(p.get("entry_price", 0) or 0)
        xp = float(p.get("exit_price", 0) or 0)
        sz = float(p.get("size", 0) or 0)
        
        asset = "UNKNOWN"
        for a in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]:
            if f"[{a}]" in t.upper() or a in t.upper():
                asset = a
                break
                
        if asset not in by_asset:
            by_asset[asset] = {"w": 0, "l": 0, "b": 0, "pnl": 0.0}
            
        if pnl > 0.009 or "target" in str(reason).lower() or xp > ep:
            wins += 1
            by_asset[asset]["w"] += 1
            tag = "WIN"
        elif pnl < -0.009 or "expired" in str(reason).lower() or "loss" in str(reason).lower() or xp < ep:
            losses += 1
            by_asset[asset]["l"] += 1
            tag = "LOSS"
        else:
            be += 1
            by_asset[asset]["b"] += 1
            tag = "BE"
            
        total_pnl += pnl
        by_asset[asset]["pnl"] += pnl
        
        safe_print(f"[{i+1:2d}] {asset:5s} | Tag: {tag:4s} | PnL: ${pnl:+.2f} | Sz: ${sz:.2f} | Entry: {ep:.3f} -> Exit: {xp:.3f} | Reason: {reason}")
        
    safe_print("\n=== PER ASSET BREAKDOWN ===")
    for a, d in sorted(by_asset.items()):
        a_tot = d["w"] + d["l"] + d["b"]
        a_wr = (d["w"] / a_tot * 100) if a_tot else 0
        safe_print(f"  {a:5s}: {d['w']}W / {d['l']}L / {d['b']}BE ({a_wr:.1f}% WR) | PnL: ${d['pnl']:+.2f}")
        
finally:
    ssh.close()
