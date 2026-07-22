import glob
import os
import json

def main():
    pattern = "/root/ZiSi-v2/core/calibration_trades/*.jsonl"
    files = glob.glob(pattern)
    
    infra_pattern = "/root/ZiSi-v2/infrastructure/calibration_trades/*.jsonl"
    files.extend(glob.glob(infra_pattern))
    
    print(f"Found {len(files)} calibration daily logs.")
    tot_lines = 0
    for f in files:
        count = 0
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                for line in file_obj:
                    if line.strip():
                        count += 1
            print(f"File: {f} | Lines/Trades: {count}")
            tot_lines += count
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    print(f"Total calibration trades found: {tot_lines}")

if __name__ == '__main__':
    main()
