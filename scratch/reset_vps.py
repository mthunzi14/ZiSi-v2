import paramiko
import json

def run_reset():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("Connecting to VPS via SSH...")
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        # 1. Stop PM2 and Tmux
        print("Stopping ZiSi-Core-Engine and killing zisi tmux session...")
        ssh.exec_command("pm2 stop ZiSi-Core-Engine")
        ssh.exec_command("tmux kill-session -t zisi")
        
        # Wait a brief moment
        import time
        time.sleep(2)
        
        # 2. Pull git changes
        print("Pulling latest git changes...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && git pull origin main")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 3. SFTP state reset block (conditional on --reset)
        import sys
        if "--reset" in sys.argv:
            print("Writing clean positions_state.json...")
            pos_data = {
                "last_updated": "2026-07-11T14:45:00.000000+00:00",
                "source": "polymarket",
                "summary": {
                    "active_count": 0,
                    "poly_active": 0,
                    "closed_count": 0,
                    "unrealized_pnl": 0.0,
                    "realized_pnl": 0.0,
                    "win_count": 0,
                    "loss_count": 0
                },
                "active": [],
                "closed": []
            }
            sftp = ssh.open_sftp()
            with sftp.file('/root/ZiSi-v2/data/positions_state.json', 'w') as f:
                json.dump(pos_data, f, indent=2)
                
            print("Writing clean account_state.json...")
            acc_data = {
                "balance": 50.0,
                "starting_balance": 50.0,
                "last_updated": "2026-07-11T14:45:00Z",
                "trades_executed": 0,
                "phase": "phase_1",
                "paused": False,
                "status": "running",
                "pnl": 0.0,
                "total_pnl": 0.0,
                "last_change_reason": "reset"
            }
            with sftp.file('/root/ZiSi-v2/data/account_state.json', 'w') as f:
                json.dump(acc_data, f, indent=2)
                
            print("Writing clean antifragile_state.json...")
            af_data = {
                "aggression": 1.0,
                "tier": "NORMAL",
                "in_recovery": False,
                "consecutive_wins": 0,
                "consecutive_losses": 0,
                "peak_portfolio": 0.0,
                "current_portfolio": 0.0,
                "trade_history": [],
                "last_updated": 0.0
            }
            with sftp.file('/root/ZiSi-v2/data/antifragile_state.json', 'w') as f:
                json.dump(af_data, f, indent=2)
                
            print("Writing clean gate_matrix.json...")
            gm_data = {
                "WEEKEND": False,
                "assets": {
                    "BTC": {"rsi": 50.0, "cvd": 0.0, "obi": 0.0, "nic": 0.0, "score": 0.0, "status": "IDLE"},
                    "ETH": {"rsi": 50.0, "cvd": 0.0, "obi": 0.0, "nic": 0.0, "score": 0.0, "status": "IDLE"},
                    "SOL": {"rsi": 50.0, "cvd": 0.0, "obi": 0.0, "nic": 0.0, "score": 0.0, "status": "IDLE"},
                    "XRP": {"rsi": 50.0, "cvd": 0.0, "obi": 0.0, "nic": 0.0, "score": 0.0, "status": "IDLE"},
                    "DOGE": {"rsi": 50.0, "cvd": 0.0, "obi": 0.0, "nic": 0.0, "score": 0.0, "status": "IDLE"}
                }
            }
            with sftp.file('/root/ZiSi-v2/data/gate_matrix.json', 'w') as f:
                json.dump(gm_data, f, indent=2)
            sftp.close()
        else:
            print("Preserving live account balance, position history, and gate state...")
        
        # 7. Start bot and tmux dashboard
        print("Starting ZiSi-Core-Engine and launching dashboard in tmux...")
        ssh.exec_command("pm2 start ZiSi-Core-Engine")
        ssh.exec_command("tmux new -d -s zisi 'cd /root/ZiSi-v2 && venv/bin/python3 zisi_terminal.py'")
        
        print("Reset completed successfully!")
        ssh.close()
    except Exception as e:
        print(f"Error executing reset: {e}")

if __name__ == "__main__":
    run_reset()
