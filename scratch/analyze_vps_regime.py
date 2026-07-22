import paramiko
import sys

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        
        # Search the console log for "Regime" status updates for SOL, HYPE, BNB, XRP on July 19
        cmd = "grep -i '\[Regime\]' /root/ZiSi-v2/zisi_bot_console.log | grep '03:\|04:\|05:' | tail -n 50"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Read raw bytes and decode using utf-8 with replacement to avoid crash
        out_bytes = stdout.read()
        out_str = out_bytes.decode('utf-8', errors='replace')
        
        print("--- Regime Logs ---")
        # Print using sys.stdout.buffer to avoid Windows console encoding errors, or just replace → with ->
        clean_str = out_str.replace("→", "->").replace("\u2192", "->")
        print(clean_str)
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
