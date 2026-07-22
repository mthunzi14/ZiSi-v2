import asyncio
import hmac
import hashlib
import time
import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CHAINLINK_DS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CHAINLINK_DS_CLIENT_SECRET", "")
API_KEY = os.getenv("CHAINLINK_DS_CANDLESTICK_API_KEY", "")

def generate_hmac_headers(method: str, path: str, body: str = "") -> dict:
    ts = str(int(time.time() * 1000))
    body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    raw_str = f"{method.upper()}\n{path}\n{body_hash}\n{CLIENT_ID}\n{ts}"
    signature = hmac.new(CLIENT_SECRET.encode('utf-8'), raw_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return {
        "X-Authorization-User": CLIENT_ID,
        "X-Authorization-Key": signature,
        "X-Authorization-Timestamp": ts,
        "Content-Type": "application/json"
    }

async def test_ds_connection():
    print(f"Testing Chainlink Data Streams HMAC auth...")
    print(f"Client ID: {CLIENT_ID}")
    
    headers = generate_hmac_headers("GET", "/api/v1/feeds")
    url = "https://api.chain.link/api/v1/feeds"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=5) as resp:
                print(f"REST Status: {resp.status}")
                text = await resp.text()
                print(f"Response: {text[:200]}")
        except Exception as e:
            print(f"REST Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_ds_connection())
