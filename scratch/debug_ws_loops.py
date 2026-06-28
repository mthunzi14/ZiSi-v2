import asyncio
import json
import time
import websockets
import traceback

async def binance_spot_listener():
    url = "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker/xrpusdt@ticker/dogeusdt@ticker"
    print("Binance: Connecting...")
    try:
        async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
            print("Binance: Connected!")
            for _ in range(5):
                msg = await ws.recv()
                data = json.loads(msg)
                print(f"Binance msg: {data.get('s')} -> {data.get('c')}")
    except Exception as e:
        print(f"Binance Error: {type(e).__name__}: {e}")
        traceback.print_exc()

async def polymarket_clob_listener():
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    print("Polymarket CLOB: Connecting...")
    try:
        async with websockets.connect(url, additional_headers=headers, ping_interval=20, ping_timeout=10) as ws:
            print("Polymarket CLOB: Connected!")
            # Subscribe to Solana YES token: 39980849115215085367587859295380354624197620184840811226652289232446500038476
            sub_msg = {
                "type": "market",
                "assets_ids": ["39980849115215085367587859295380354624197620184840811226652289232446500038476"],
                "custom_feature_enabled": True
            }
            await ws.send(json.dumps(sub_msg))
            print("Polymarket CLOB: Subscribed!")
            for _ in range(5):
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(msg)
                print(f"Polymarket CLOB msg: {type(data)}")
    except Exception as e:
        print(f"Polymarket CLOB Error: {type(e).__name__}: {e}")
        traceback.print_exc()

async def main():
    await asyncio.gather(
        binance_spot_listener(),
        polymarket_clob_listener()
    )

asyncio.run(main())
