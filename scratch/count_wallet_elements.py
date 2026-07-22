import glob
import json

def main():
    files = glob.glob("/root/ZiSi-v2/wallet/*.json")
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            if isinstance(data, list):
                print(f"File: {f} | Type: list | Elements: {len(data)}")
            elif isinstance(data, dict):
                print(f"File: {f} | Type: dict | Keys: {len(data)}")
                for k, v in data.items():
                    if isinstance(v, list):
                        print(f"  Key '{k}': list | Elements: {len(v)}")
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == '__main__':
    main()
