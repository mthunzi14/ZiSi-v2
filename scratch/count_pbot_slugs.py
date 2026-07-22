import json

def main():
    f = "/root/ZiSi-v2/wallet/wallet_0x21d0a97a_history.json"
    try:
        with open(f, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        slugs = set(t.get("Slug") for t in data if t.get("Slug"))
        print(f"PBot-6 Main unique slugs: {len(slugs)} | Total txs: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
