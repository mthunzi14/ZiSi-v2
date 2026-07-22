import os
from pathlib import Path

print("Current Directory:", os.getcwd())
data_dir = Path("data")
if data_dir.exists():
    print("Files in data/:", os.listdir(data_dir))
else:
    print("data/ directory does not exist.")
