import os
import glob

def main():
    root_dir = "/root/ZiSi-v2"
    py_files = glob.glob(os.path.join(root_dir, "**/*.py"), recursive=True)
    
    print(f"Scanning {len(py_files)} python files for the number 1509...")
    for f in py_files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                lines = file_obj.readlines()
            for idx, line in enumerate(lines):
                if "1509" in line:
                    print(f"MATCH: {f}:{idx+1} | {line.strip()}")
        except:
            pass

if __name__ == '__main__':
    main()
