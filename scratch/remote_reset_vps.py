import paramiko
import time

def remote_reset():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"

    print("Connecting to VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=30)

    print("1. Fetching and syncing git on VPS to origin/stable-june22...")
    stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && git fetch origin && git reset --hard origin/stable-june22")
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

    print("2. Running clean slate reset on VPS...")
    stdin, stdout, stderr = ssh.exec_command("cd /root/ZiSi-v2 && venv/bin/python3 scratch/clean_archive_and_reset_to_50.py")
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

    print("3. Restarting PM2 engine and tmux zisi session...")
    ssh.exec_command("pm2 restart all")
    ssh.exec_command("tmux kill-session -t zisi")
    time.sleep(2)
    ssh.exec_command("tmux new -d -s zisi 'cd /root/ZiSi-v2 && venv/bin/python3 zisi_terminal.py'")

    print("--- REMOTE VPS RESET COMPLETE ---")
    ssh.close()

if __name__ == "__main__":
    remote_reset()
