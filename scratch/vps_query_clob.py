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

headers = _build_clob_auth_headers("GET", "/orders", "")
print("Generated Auth Headers:", list(headers.keys()))

try:
    res = requests.get(f"{clob_url}/orders", headers=headers, timeout=10)
    print("Response Status Code:", res.status_code)
    print("Raw Response Text:")
    print(res.text[:2000])
except Exception as e:
    print("API Query Error:", e)
