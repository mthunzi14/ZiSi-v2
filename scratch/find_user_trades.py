import os
import json
import glob

def main():
    root_dir = "/root/ZiSi-v2"
    json_files = glob.glob(os.path.join(root_dir, "**/*.json"), recursive=True)
    md_files = glob.glob(os.path.join(root_dir, "**/*.md"), recursive=True)
    
    print(f"Scanning {len(json_files)} json files and {len(md_files)} md files...")
    
    # 1. Scan JSON files for lists with ~1500 elements or keys containing 'closed' with ~1500 elements
    for f in json_files:
        # skip wallet large runs if they don't match
        if "wallet_0xeebde7a0" in f:
            continue
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()
                # quick check on size
                if len(content) < 1000:
                    continue
                data = json.loads(content)
                if isinstance(data, list):
                    if 1400 <= len(data) <= 1600:
                        print(f"MATCH (List): {f} has {len(data)} items.")
                elif isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, list) and 1400 <= len(v) <= 1600:
                            print(f"MATCH (Dict key '{k}'): {f} has {len(v)} items in key.")
        except Exception as e:
            pass
            
    # 2. Search MD files for "1509" or "1,509"
    for f in md_files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()
                if "1509" in content or "1,509" in content or "1500" in content:
                    print(f"MATCH (Text): {f} mentions '1509' or '1,509' or '1500'.")
        except:
            pass

if __name__ == '__main__':
    main()
