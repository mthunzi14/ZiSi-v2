import re

POSITIONS_PATH = r"c:\Users\mthun\Downloads\ZiSi-v2\data\positions_state.json"

try:
    with open(POSITIONS_PATH, "rb") as f:
        content = f.read()
    print("Read bytes:", len(content))
    # Replace null bytes with spaces
    content_clean = content.replace(b"\x00", b" ")
    # Replace control characters except tab, newline, carriage return
    # Let's decode to utf-8, replace, and encode back
    text = content_clean.decode("utf-8", errors="replace")
    # Remove control characters like \x00-\x08, \x0b-\x0c, \x0e-\x1f
    text_clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text)
    
    with open(POSITIONS_PATH, "w", encoding="utf-8") as f:
        f.write(text_clean)
    print("Scrubbed invalid control characters from local positions_state.json successfully.")
except Exception as e:
    print(f"Error scrubbing JSON file: {e}")
