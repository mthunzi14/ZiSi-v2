import requests
import json
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, "/root/ZiSi-v2")

from core.engine.trader import _build_clob_auth_headers, _get_config

cfg = _get_config()
clob_url = cfg.get("POLYMARKET_CLOB_API_URL", "https://clob.polymarket.com").rstrip("/")

print("=== QUERYING OFFICIAL POLYMARKET CLOB API ===")
print("CLOB URL:", clob_url)

endpoints = [
    ("/data/orders", ""),
    ("/data/trades", ""),
    (f"/trades?maker_address=0xC91627ee52494F2D2276Ad13Dae06151E28dAcCC", "")
]

for ep, body in endpoints:
    print(f"\n--- Testing Endpoint: {ep} ---")
    headers = _build_clob_auth_headers("GET", ep, body)
    try:
        res = requests.get(f"{clob_url}{ep}", headers=headers, timeout=10)
        print("Response Status Code:", res.status_code)
        print("Raw Response Text:")
        print(res.text[:1000])
    except Exception as e:
        print("API Query Error:", e)

