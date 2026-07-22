import paramiko
import re

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        # We will search the console log for events between 00:20 and 09:00 on July 19th
        # The logs use local time or UTC? The logs use local timezone or UTC?
        # Let's check the log timestamps from the console log:
        # In our previous tail, we saw:
        # 01:04:47 [DEBUG] zisi.rtds.ws: [RTDS-WS] ...
        # And:
        # 22:20:08 [DEBUG] zisi.main: ...
        # Ah! The console logs use local time of the VPS, which is in SAST!
        # Wait, if local time of the VPS is SAST, let's check by running `date` on the VPS.
        stdin, stdout, stderr = ssh.exec_command("date")
        date_out = stdout.read().decode('utf-8').strip()
        print(f"VPS current date/time: {date_out}")
        
        # Let's search the console log for "[Execution]" lines between 00:20 and 09:00 today.
        cmd = "grep -i '\[Execution\]' /root/ZiSi-v2/zisi_bot_console.log | tail -n 40"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exec_lines = stdout.read().decode('utf-8').strip().split('\n')
        
        print("\n--- Recent Execution Logs ---")
        for line in exec_lines:
            print(line)
            
        # Let's search for "Regime" updates for BNB, HYPE, SOL, XRP, DOGE, ETH in the last few hours
        print("\n--- Recent Regime Logs ---")
        cmd_regime = "grep -i '\[Regime\]' /root/ZiSi-v2/zisi_bot_console.log | tail -n 25"
        stdin, stdout, stderr = ssh.exec_command(cmd_regime)
        regime_lines = stdout.read().decode('utf-8').strip().split('\n')
        for line in regime_lines:
            print(line)
            
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
