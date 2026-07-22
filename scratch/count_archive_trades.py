import glob
import json
import os

def main():
    tot = 0
    pattern = "/root/ZiSi-v2/**/positions_state.json"
    files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(files)} files matching pattern.")
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            closed = data.get("closed", [])
            count = len(closed)
            print(f"File: {f} | Closed Trades: {count}")
            tot += count
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    print(f"Total closed trades found in state files: {tot}")

if __name__ == '__main__':
    main()
