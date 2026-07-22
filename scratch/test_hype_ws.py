import asyncio
import websockets
import json

async def test_hype():
    url = "wss://fstream.binance.com/stream?streams=hypeusdt@bookTicker/hypeusdt@aggTrade"
    print(f"Connecting to {url}...")
    try:
        async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
            print("Connected successfully!")
            for i in range(5):
                msg = await ws.recv()
                data = json.loads(msg)
                print(f"Message {i+1}: {data}")
    except Exception as e:
        print(f"Failed to connect or received error: {e}")

if __name__ == "__main__":
    asyncio.run(test_hype())
