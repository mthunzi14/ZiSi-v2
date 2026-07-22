import json

def main():
    files = [
        "/root/ZiSi-v2/wallet/wallet_0xeebde7a0_run1_clean.json",
        "/root/ZiSi-v2/wallet/wallet_0xeebde7a0_run2_clean.json"
    ]
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            slugs = set(t.get("Slug") for t in data if t.get("Slug"))
            print(f"File: {f} | Unique Slugs: {len(slugs)} | Total txs: {len(data)}")
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == '__main__':
    main()
