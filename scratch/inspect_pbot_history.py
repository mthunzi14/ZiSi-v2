import json

def main():
    f = "/root/ZiSi-v2/wallet/wallet_0x21d0a97a_history.json"
    try:
        with open(f, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        print(f"Total transactions: {len(data)}")
        if data:
            print("First transaction keys:", data[0].keys())
            print("First transaction sample:")
            print(json.dumps(data[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
