import json

def main():
    f = "/root/ZiSi-v2/data/positions_state.json"
    try:
        with open(f, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        closed = data.get("closed", [])
        if closed:
            print("Keys:", closed[0].keys())
            print(json.dumps(closed[0], indent=2))
        else:
            print("Closed list is empty.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
