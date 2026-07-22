import json

def main():
    f = "/root/ZiSi-v2/core/calibration_trades/trades_2026-06-26.jsonl"
    try:
        with open(f, "r", encoding="utf-8") as file_obj:
            first_line = file_obj.readline()
        if first_line:
            data = json.loads(first_line.strip())
            print("Keys in calibration trade sample:")
            print(list(data.keys()))
            print("\nSample values:")
            print(json.dumps(data, indent=2))
        else:
            print("File is empty.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
