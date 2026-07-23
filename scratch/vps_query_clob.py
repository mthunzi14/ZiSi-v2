import sys
sys.path.insert(0, "/root/ZiSi-v2")

from py_clob_client.client import ClobClient
from core.engine.trader import _get_config

cfg = _get_config()

print("=== OFFICIAL POLYMARKET CLOB SDK QUERY ===")
try:
    client = ClobClient(
        host=cfg.get("POLYMARKET_CLOB_API_URL", "https://clob.polymarket.com"),
        key=cfg.get("POLYMARKET_CLOB_API_KEY", ""),
        chain_id=137,
        creds=None,
        signature_type=2,
        funder=cfg.get("POLYMARKET_CLOB_API_ADDRESS", "")
    )
    # Set API creds
    from py_clob_client.clob_types import ApiCreds
    client.set_api_creds(ApiCreds(
        api_key=cfg.get("POLYMARKET_CLOB_API_KEY", ""),
        api_secret=cfg.get("POLYMARKET_CLOB_API_SECRET", ""),
        api_passphrase=cfg.get("POLYMARKET_CLOB_API_PASSPHRASE", "")
    ))
    
    print("Fetching active/closed orders from Polymarket CLOB...")
    orders = client.get_orders()
    print("=== CLOB API ORDERS ===")
    print(orders[:5] if isinstance(orders, list) else orders)
    
    trades = client.get_trades()
    print("=== CLOB API TRADES ===")
    print(trades[:5] if isinstance(trades, list) else trades)
except Exception as e:
    print("CLOB SDK Error:", e)


