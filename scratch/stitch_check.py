import json

CURRENT_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"
BACKUP_PATH = r"c:\Users\mthun\.gemini\antigravity\brain\14e04d67-5e69-491a-9086-7b2c06bc7b3d\backups\positions_state.json"

with open(CURRENT_PATH, "r") as f:
    curr_data = json.load(f)
with open(BACKUP_PATH, "r") as f:
    back_data = json.load(f)

curr_closed = curr_data.get("closed", [])
back_closed = back_data.get("closed", [])

print("Current length:", len(curr_closed))
print("Backup length:", len(back_closed))

# Let's find unique trade IDs or titles+timestamps to see what's in backup but not in current
curr_keys = { (p['entry_time'], p.get('event_title', '')) for p in curr_closed }
back_keys = { (p['entry_time'], p.get('event_title', '')) for p in back_closed }

only_in_back = [p for p in back_closed if (p['entry_time'], p.get('event_title', '')) not in curr_keys]
print("Number of trades only in backup:", len(only_in_back))
if only_in_back:
    print("Sample only in backup (oldest):")
    for p in only_in_back[:5]:
        print(p['entry_time'], p.get('event_title', ''))
