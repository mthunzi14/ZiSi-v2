import requests
from datetime import datetime, timezone

def check_binance_klines(symbol, timestamp_ms):
    # Fetch klines around the timestamp
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1m",
        "startTime": timestamp_ms - 600 * 1000,
        "endTime": timestamp_ms + 600 * 1000,
        "limit": 20
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        klines = r.json()
        return klines
    else:
        print(f"Error fetching Binance data: {r.text}")
        return []

# July 19, 14:50:00 UTC is:
dt = datetime(2026, 7, 19, 14, 50, 0, tzinfo=timezone.utc)
ts_ms = int(dt.timestamp() * 1000)

print(f"Target timestamp: {dt.isoformat()} ({ts_ms})")

for symbol in ["BTCUSDT", "SOLUSDT", "ETHUSDT", "BNBUSDT"]:
    print(f"\n=== {symbol} ===")
    klines = check_binance_klines(symbol, ts_ms)
    for k in klines:
        open_time = datetime.fromtimestamp(k[0] / 1000, timezone.utc)
        open_p = float(k[1])
        high_p = float(k[2])
        low_p = float(k[3])
        close_p = float(k[4])
        print(f"Candle {open_time.strftime('%H:%M:%S')} UTC | Open: {open_p:.2f} | Close: {close_p:.2f}")
