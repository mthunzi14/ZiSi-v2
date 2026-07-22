import paramiko
from pathlib import Path

def main():
    hostname = "204.168.222.48"
    username = "root"
    password = "Makabongwe2005!"
    
    files_to_sync = [
        "config.py",
        "zisi_terminal.py",
        "app/main.py",
        "core/engine/updown_engine.py",
        "core/engine/trader.py",
        "core/engine/polymarket_rtds_ingest.py",
        "scratch/inspect_recent_trades.py",
        "scratch/calculate_stats.py",
        "ZISI - Items.md",
        "ZISI - Journal.md",
        "test/test_edges.py",
        "core/engine/volatility_surface.py",
        "core/risk/portfolio_heat.py",
        "core/engine/whale_tracker.py"
    ]
    
    local_root = Path(__file__).resolve().parent.parent
    
    print(f"Connecting to {hostname} via SFTP...")
    transport = paramiko.Transport((hostname, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    for f_rel in files_to_sync:
        local_path = local_root / f_rel
        remote_path = f"/root/ZiSi-v2/{f_rel}"
        
        if not local_path.exists():
            print(f"Local file {local_path} does not exist!")
            continue
            
        print(f"Uploading {f_rel} -> {remote_path}...")
        sftp.put(str(local_path), remote_path)
        
    sftp.close()
    transport.close()
    print("Sync complete!")

if __name__ == "__main__":
    main()
