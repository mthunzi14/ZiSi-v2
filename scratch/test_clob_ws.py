import asyncio
import json
import websockets

async def test_ws():
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    print(f"Connecting to {url}...")
    try:
        async with websockets.connect(url, additional_headers=headers, ping_interval=20, ping_timeout=10) as ws:
            print("Connected! Sending subscription for a test token ID...")
            
            # Let's subscribe to a known active token ID
            # e.g. Solana YES token from our earlier resolver test: 39980849115215085367587859295380354624197620184840811226652289232446500038476
            sub_msg = {
                "type": "market",
                "assets_ids": ["39980849115215085367587859295380354624197620184840811226652289232446500038476"],
                "custom_feature_enabled": True
            }
            await ws.send(json.dumps(sub_msg))
            print("Subscription message sent. Waiting for message...")
            
            for _ in range(5):
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(msg)
                print(f"Received message: {data.get('event_type')} / keys: {list(data.keys())}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test_ws())
