import paramiko
import sys

def main():
    key_path = r"c:\Users\mthun\Downloads\vps_key.key"
    ip = "204.168.222.48"
    username = "root"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Loading private key...")
    try:
        # Try loading as RSA key
        key = paramiko.RSAKey.from_private_key_file(key_path)
    except Exception as e:
        print(f"Failed to load as RSA: {e}")
        try:
            # Try loading as Ed25519 or other key types
            key = paramiko.PrivateKey.from_private_key_file(key_path)
        except Exception as e2:
            print(f"Failed to load key: {e2}")
            return
            
    print("Connecting to VPS...")
    try:
        ssh.connect(ip, username=username, pkey=key, timeout=10)
        print("Successfully connected!")
        
        stdin, stdout, stderr = ssh.exec_command("hostname")
        print("Hostname:", stdout.read().decode().strip())
        
        ssh.close()
    except Exception as e:
        print(f"SSH connection failed: {e}")

if __name__ == "__main__":
    main()
