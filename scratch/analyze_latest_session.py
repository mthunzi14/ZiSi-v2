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
        
        # Filter for trades closed after 2026-07-18T21:40:00+00:00 (which is 23:40 SAST)
        cutoff = datetime(2026, 7, 18, 21, 40, 0, tzinfo=timezone.utc)
        
        session_trades = []
        for p in closed:
            exit_time_str = p.get("exit_time", "")
            if exit_time_str:
                # Remove Z or parse timezone offset
                if exit_time_str.endswith("Z"):
                    exit_time_str = exit_time_str[:-1] + "+00:00"
                try:
                    exit_time = datetime.fromisoformat(exit_time_str)
                    if exit_time >= cutoff:
                        session_trades.append(p)
                except ValueError:
                    pass
                    
        print(f"Total trades in this session (since 23:40 SAST restart): {len(session_trades)}")
        wins = 0
        losses = 0
        total_pnl = 0.0
        
        # Group by parent order id to treat tranche A and B as one logical trade
        logical_trades = {}
        for p in session_trades:
            pid = p.get("parent_order_id", p.get("order_id"))
            if pid not in logical_trades:
                logical_trades[pid] = []
            logical_trades[pid].append(p)
            
        print("\nDetail of logical trades:")
        for pid, tranches in logical_trades.items():
            asset = tranches[0].get("asset") or "?"
            if not asset or asset == "?":
                # Extract asset from event_title or order_id
                title = tranches[0].get("event_title", "")
                if "BTC" in title: asset = "BTC"
                elif "ETH" in title: asset = "ETH"
                elif "SOL" in title: asset = "SOL"
                elif "XRP" in title: asset = "XRP"
                elif "DOGE" in title: asset = "DOGE"
                elif "BNB" in title: asset = "BNB"
                elif "HYPE" in title: asset = "HYPE"
            
            pnl = sum(t.get("realized_pnl", 0.0) for t in tranches)
            total_pnl += pnl
            cost = sum(t.get("size", 0.0) for t in tranches)
            
            # Entry / Exit prices
            entry_prices = [t.get("entry_price") for t in tranches]
            exit_prices = [t.get("exit_price") for t in tranches]
            directions = [t.get("direction") for t in tranches]
            
            is_win = pnl > 0.009
            if is_win:
                wins += 1
            elif pnl < -0.009:
                losses += 1
                
            outcome_str = "WIN" if is_win else "LOSS" if pnl < -0.009 else "BE"
            print(f"- {asset} {directions[0]} | Cost: ${cost:.2f} | Entry: {entry_prices} | Exit: {exit_prices} | PnL: ${pnl:+.2f} ({outcome_str})")
            
        print("\nSummary:")
        print(f"Wins: {wins} | Losses: {losses} | Win Rate: {wins/(wins+losses)*100 if (wins+losses) else 0:.1f}%")
        print(f"Total Session PnL: ${total_pnl:+.2f}")
        
        # Get account balance
        with sftp.open('/root/ZiSi-v2/data/account_state.json', 'r') as f_acct:
            acct_data = json.load(f_acct)
            print(f"Current VPS Balance: ${acct_data.get('balance', 0.0):.2f}")
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
