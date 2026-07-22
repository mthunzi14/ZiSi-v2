import re

file_path = r"c:\Users\mthun\Downloads\ZiSi-v2\zisi_terminal.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add safe_float helper if not present
safe_float_def = """
def safe_float(val, default=0.0) -> float:
    if val is None:
        return float(default)
    try:
        return float(val)
    except (ValueError, TypeError):
        return float(default)
"""

if "def safe_float" not in content:
    content = content.replace("console = Console()", "console = Console()\n" + safe_float_def)

# Replace risky float patterns in data dict lookups
patterns = [
    (r'float\((p(?:os)?\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((h\[[^\]]+\])\)', r'safe_float(\1)'),
    (r'float\((cl_entry\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((cl_entry\s*or\s*0\.0)\)', r'safe_float(\1)'),
    (r'float\((spot_copy\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((data\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((data\[[^\]]+\])\)', r'safe_float(\1)'),
    (r'float\((summary\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((g_state\.account_state\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((pos\["expiry_ts"\])\)', r'safe_float(\1)'),
    (r'float\((best_bid)\)', r'safe_float(\1)'),
    (r'float\((best_ask)\)', r'safe_float(\1)'),
    (r'float\((bids\[-1\]\.get\([^)]+\))\)', r'safe_float(\1)'),
    (r'float\((asks\[0\]\.get\([^)]+\))\)', r'safe_float(\1)'),
]

for pat, repl in patterns:
    content = re.sub(pat, repl, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated zisi_terminal.py with bulletproof safe_float wrappers!")
