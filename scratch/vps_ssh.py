import paramiko
import sys

# Reconfigure stdout for UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def run_ssh_command(cmd):
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname} via SSH...")
        ssh.connect(hostname, username=username, password=password, timeout=30, banner_timeout=30)
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Read outputs
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
    if len(sys.argv) < 2:
        print("Usage: python vps_ssh.py \"<command>\"")
        sys.exit(1)
    command = " ".join(sys.argv[1:])
    run_ssh_command(command)
