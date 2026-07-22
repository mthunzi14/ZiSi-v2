import json
import os

target_ids = ["zisi_0e3f88d2a13e", "zisi_ce9365c1c214"]
data_dir = "/root/ZiSi-v2/data"
files = ["positions_state.json", "pos2.json", "pos_snapshot.json"]

print("--- STARTING SCRUB SEARCH ---")
for fn in files:
    path = os.path.join(data_dir, fn)
    if not os.path.exists(path):
        print(f"File {fn} does not exist on VPS.")
        continue
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        modified = False
        if isinstance(data, dict):
            for k in ["active", "closed"]:
                if k in data and isinstance(data[k], list):
                    original_len = len(data[k])
                    # Filter out items that have order_id or parent_order_id or contain target_ids
                    new_list = []
                    for item in data[k]:
                        oid = str(item.get("order_id", ""))
                        p_oid = str(item.get("parent_order_id", ""))
                        if any(tid in oid or tid in p_oid for tid in target_ids):
                            print(f"Found match in {fn} -> {k}: ID={oid}, Parent={p_oid}")
                            modified = True
                        else:
                            new_list.append(item)
                    data[k] = new_list
                    if modified:
                        print(f"Filtered {fn} -> {k}: {original_len} -> {len(data[k])}")
                        
        if modified:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Saved modified {fn}")
        else:
            print(f"No changes made to {fn}")
            
    except Exception as e:
        print(f"Error processing {fn}: {e}")

print("--- SCRUB COMPLETED ---")
