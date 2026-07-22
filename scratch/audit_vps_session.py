import paramiko
import json
import sys
import re

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
    
    stdin, stdout, stderr = ssh.exec_command("cat /root/ZiSi-v2/data/positions_state.json")
    data_str = stdout.read().decode('utf-8')
    data = json.loads(data_str)
    
    closed = data.get("closed", [])
    summary = data.get("summary", {})
    
    safe_print("==========================================================================")
    safe_print("             VPS LIVE SESSION FORENSIC AUDIT (314 TRADES)                 ")
    safe_print("==========================================================================")
    safe_print(f"VPS Closed Trade Count: {len(closed)}")
    safe_print(f"VPS Summary: {summary}")
    
    wins = [p for p in closed if p.get('realized_pnl', 0) > 0.01]
    losses = [p for p in closed if p.get('realized_pnl', 0) < -0.01]
    breakevens = [p for p in closed if -0.01 <= p.get('realized_pnl', 0) <= 0.01]
    
    wr_excl = (len(wins) / (len(wins) + len(losses)) * 100) if (len(wins) + len(losses)) > 0 else 0
    total_pnl = sum(p.get('realized_pnl', 0) for p in closed)
    
    safe_print(f"Total Wins: {len(wins)} | Total Losses: {len(losses)} | BE: {len(breakevens)}")
    safe_print(f"Win Rate (excl BE): {wr_excl:.2f}%")
    safe_print(f"Total Realized PnL: ${total_pnl:.2f}")
    
    expired_losses = [p for p in losses if 'expired' in str(p.get('exit_reason', '')).lower()]
    stop_losses = [p for p in losses if 'expired' not in str(p.get('exit_reason', '')).lower()]
    
    safe_print(f"\nLoss Breakdown:")
    safe_print(f"  - Market Expired Losses: {len(expired_losses)}")
    safe_print(f"  - Trailing/Stop Losses: {len(stop_losses)}")
    
    avg_win_slp = sum(p.get('slp', 0.0) for p in wins) / len(wins) if wins else 0
    avg_exp_slp = sum(p.get('slp', 0.0) for p in expired_losses) / len(expired_losses) if expired_losses else 0
    
    safe_print(f"\nSlippage Correlation:")
    safe_print(f"  - Avg Slippage on Winning Trades: {avg_win_slp*100:.2f}¢")
    safe_print(f"  - Avg Slippage on Expired Losses: {avg_exp_slp*100:.2f}¢")
    
    high_slp_losses = [p for p in expired_losses if p.get('slp', 0) > 0.12]
    low_slp_losses = [p for p in expired_losses if p.get('slp', 0) <= 0.12]
    safe_print(f"  - Expired Losses with Slippage > 12¢: {len(high_slp_losses)} ({len(high_slp_losses)/len(expired_losses)*100:.1f}%)")
    safe_print(f"  - Expired Losses with Slippage <= 12¢: {len(low_slp_losses)} ({len(low_slp_losses)/len(expired_losses)*100:.1f}%)")
    
    # Asset breakdown
    asset_stats = {}
    for p in closed:
        title = p.get('event_title', '')
        pnl = p.get('realized_pnl', 0.0)
        brackets = re.findall(r"\[([A-Z0-9]+)\]", title)
        asset = "UNKNOWN"
        for b in brackets:
            if b in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE"]:
                asset = b
                break
        if asset not in asset_stats:
            asset_stats[asset] = {"w": 0, "l": 0, "be": 0, "pnl": 0.0}
        if pnl > 0.01: asset_stats[asset]["w"] += 1
        elif pnl < -0.01: asset_stats[asset]["l"] += 1
        else: asset_stats[asset]["be"] += 1
        asset_stats[asset]["pnl"] += pnl
        
    safe_print("\n--- ASSET BREAKDOWN (CURRENT SESSION) ---")
    for k in sorted(asset_stats.keys()):
        v = asset_stats[k]
        w, l, b = v["w"], v["l"], v["be"]
        wr = (w / (w + l) * 100) if (w + l) > 0 else 0
        safe_print(f"{k:<6s}: {w+l+b:3d} trades | {w:3d} W / {l:3d} L / {b:2d} BE | WR: {wr:5.1f}% | PnL: ${v['pnl']:7.2f}")

    safe_print("\n--- TOP 15 LARGEST LOSSES ON VPS ---")
    top_losses = sorted(closed, key=lambda x: x.get('realized_pnl', 0))[:15]
    for p in top_losses:
        title = p.get('event_title', '')
        pnl = p.get('realized_pnl', 0.0)
        entry = p.get('entry_price', 0.0)
        slp = p.get('slp', 0.0)
        sig_p = p.get('signal_price', 0.0)
        reason = p.get('exit_reason', '')
        t_str = p.get('exit_time', p.get('entry_time', ''))[:19]
        safe_print(f"{t_str} | {title[:28]:<28} | PnL: ${pnl:6.2f} | Entry: {entry:.3f} (Sig: {sig_p:.3f}, Slp: {slp*100:4.1f}¢) | {reason}")

finally:
    ssh.close()
