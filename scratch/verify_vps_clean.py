import paramiko

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    cmd = "python3 -c \"import json; f='positions_state.json'; d=json.load(open('/root/ZiSi-v2/data/' + f)); print(f, 'active unk:', sum(1 for p in d.get('active', []) if str(p.get('regime')).upper() == 'UNKNOWN'), 'closed unk:', sum(1 for p in d.get('closed', []) if str(p.get('regime')).upper() == 'UNKNOWN'))\""
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("positions_state.json:", stdout.read().decode('utf-8').strip())
        
        cmd_pos2 = "python3 -c \"import json; f='pos2.json'; d=json.load(open('/root/ZiSi-v2/data/' + f)); print(f, 'active unk:', sum(1 for p in d.get('active', []) if str(p.get('regime')).upper() == 'UNKNOWN'), 'closed unk:', sum(1 for p in d.get('closed', []) if str(p.get('regime')).upper() == 'UNKNOWN'))\""
        stdin, stdout, stderr = ssh.exec_command(cmd_pos2)
        print("pos2.json:", stdout.read().decode('utf-8').strip())
        
        cmd_snap = "python3 -c \"import json; f='pos_snapshot.json'; d=json.load(open('/root/ZiSi-v2/data/' + f)); print(f, 'active unk:', sum(1 for p in d.get('active', []) if str(p.get('regime')).upper() == 'UNKNOWN'), 'closed unk:', sum(1 for p in d.get('closed', []) if str(p.get('regime')).upper() == 'UNKNOWN'))\""
        stdin, stdout, stderr = ssh.exec_command(cmd_snap)
        print("pos_snapshot.json:", stdout.read().decode('utf-8').strip())
        
        ssh.close()
    except Exception as e:
        print(f"SSH Error: {e}")

if __name__ == "__main__":
    main()
