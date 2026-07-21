#!/usr/bin/env python3
"""
zisi_terminal.py — Rich Terminal Dashboard for ZiSi-v2.
Features live-updating WebSockets for Binance Spot and Polymarket CLOB feeds,
displays live Chainlink and Pyth oracle prices, calculates real-time unrealized P&L,
and provides a clean, premium "Titanium Gray" design with light steel blue assets.
"""

import os
import sys
import json
import time
import asyncio
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
try:
    import select
    import termios
    import tty
except ImportError:
    select = None
    termios = None
    tty = None

# Try importing rich. Exit gracefully if missing.
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.box import ROUNDED
except ImportError:
    print("Error: 'rich' library is required. Install it using: pip install rich")
    sys.exit(1)

# Try importing websockets. Exit if missing.
try:
    import websockets
except ImportError:
    print("Error: 'websockets' library is required. Install it using: pip install websockets")
    sys.exit(1)

# Initialize console
console = Console()

def safe_float(val, default=0.0) -> float:
    if val is None:
        return float(default)
    try:
        return float(val)
    except (ValueError, TypeError):
        return float(default)


# Resolve paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

STATE_FILE = DATA_DIR / "account_state.json"
POSITIONS_FILE = DATA_DIR / "positions_state.json"
REGIME_FILE = DATA_DIR / "regime_status.json"
SENTIMENT_FILE = DATA_DIR / "sentiment_state.json"
CHAINLINK_FILE = DATA_DIR / "chainlink_prices.json"
HFT_METRICS_FILE = DATA_DIR / "hft_metrics.json"
POTENTIAL_TRADES_FILE = DATA_DIR / "potential_trades.json"

PM2_LOG_PATH = Path("/root/.pm2/logs/ZiSi-Core-Engine-error.log")
LOCAL_LOG_PATH = PROJECT_ROOT / "zisi_bot_console.log"
LOG_FILE = PM2_LOG_PATH if PM2_LOG_PATH.exists() else LOCAL_LOG_PATH

# Premium color codes
COLOR_ASSET = "color(153)"     # Muted premium steel color for assets
COLOR_LABEL = "grey70"              # Titanium Gray for regular labels
COLOR_VAL = "grey85"                # Premium soft white for regular values
COLOR_BORDER = "grey37"             # Low-profile dark border gray

# Pastel color codes (replaces green, red, and magenta tags throughout the UI)
COLOR_PASTEL_GREEN = "#8ae28a"
COLOR_PASTEL_RED = "#ff746c"
COLOR_PASTEL_PINK = "#f4b3c2"

# Turquoise palette for trade types
COLOR_ES = "#79ECE0"
COLOR_EX = "#40E0D0"
COLOR_LS = "#B2F7EF"


# Global state thread-safe container
class GlobalDashboardState:
    def __init__(self):
        self.lock = threading.Lock()
        # Live WebSocket data (added DOGE)
        self.spot_prices = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0, "XRP": 0.0, "DOGE": 0.0, "BNB": 0.0, "HYPE": 0.0, "LINK": 0.0}
        self.clob_prices = {}  # token_id -> {"yes_price": float, "last_update": float}
        self.clob_spreads = {}  # token_id -> float
        
        # Resolved active 5m market token IDs
        self.asset_token_ids = {}  # asset -> {"yes": token_id, "no": token_id}
        
        # File-based state
        self.account_state = {}
        self.positions_state = {}
        self.regime_state = {}
        self.sentiment_state = {}
        self.chainlink_prices = {}
        self.hft_metrics = {}
        self.potential_trades = {}
        self.closed_scroll_offset = 0
        self.logs_scroll_offset = 0
        self.metrics_scroll_offset = 0
        self.fullscreen_mode = None
        self.redraw_event = threading.Event()
        
        # Timing
        self.start_time = time.time()
        self.active_market_ids = set()  # set of token IDs to subscribe to


g_state = GlobalDashboardState()


# ── WebSocket & API Resolvers ──────────────────────────────────────────────────

def fetch_asset_slug(asset: str, ts: int) -> tuple[str, dict]:
    coin_lower = asset.lower()
    slug = f"{coin_lower}-updown-5m-{ts}"
    url = f"https://gamma-api.polymarket.com/events?slug={slug}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=1.0) as r:
            data = json.loads(r.read())
            if data and isinstance(data, list) and len(data) > 0:
                event_slug = data[0].get("slug", "")
                if event_slug.lower() != slug.lower():
                    return asset, None
                markets = data[0].get("markets", [])
                if markets:
                    clob_token_ids = markets[0].get("clobTokenIds")
                    if isinstance(clob_token_ids, str):
                        clob_token_ids = json.loads(clob_token_ids)
                    if clob_token_ids and len(clob_token_ids) >= 2:
                        return asset, {"yes": clob_token_ids[0], "no": clob_token_ids[1]}
    except Exception:
        pass
    return asset, None


def update_active_market_ids():
    """Query Polymarket Gamma API concurrently to resolve YES/NO token IDs for all assets."""
    assets = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]
    now = time.time()
    ts_current = int(now // 300) * 300
    
    # Compile 16 tasks to run concurrently in parallel (8 assets * 2 boundaries)
    tasks = []
    for asset in assets:
        for ts in [ts_current, ts_current + 300]:
            tasks.append((asset, ts))
            
    new_tokens = {}
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(lambda t: fetch_asset_slug(t[0], t[1]), tasks)
        for asset, token_dict in results:
            if token_dict:
                # If we get a valid dictionary, store it. The order ensures next boundary overwrites if present.
                new_tokens[asset] = token_dict
                
    if new_tokens:
        with g_state.lock:
            g_state.asset_token_ids.update(new_tokens)
            # Add yes and no token IDs to active subscription set
            for t_dict in new_tokens.values():
                g_state.active_market_ids.add(t_dict["yes"])
                g_state.active_market_ids.add(t_dict["no"])


def run_market_resolver_loop():
    """Background loop to query Gamma API for active markets every 3 minutes."""
    while True:
        try:
            update_active_market_ids()
        except Exception:
            pass
        time.sleep(180)


async def binance_spot_listener():
    """Connect to Binance Spot + Futures WebSockets for sub-second price updates."""
    async def listen_loop(label: str, url: str):
        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        symbol = data.get("s", "")
                        if not symbol:
                            continue
                        
                        event_type = data.get("e", "")
                        if event_type == "bookTicker":
                            bid = safe_float(data.get("b", 0.0))
                            ask = safe_float(data.get("a", 0.0))
                            price = (bid + ask) / 2.0 if (bid > 0 and ask > 0) else (bid or ask)
                        else:
                            price = safe_float(data.get("c", 0.0))
                        
                        asset = symbol.upper().replace("USDT", "")
                        if asset in g_state.spot_prices:
                            with g_state.lock:
                                g_state.spot_prices[asset] = price
                            g_state.redraw_event.set()
            except Exception:
                await asyncio.sleep(2)  # Reconnect
                
    spot_url = "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker/xrpusdt@ticker/dogeusdt@ticker/bnbusdt@ticker/linkusdt@ticker"
    futures_url = "wss://fstream.binance.com/ws/hypeusdt@bookTicker"
    
    await asyncio.gather(
        listen_loop("SPOT", spot_url),
        listen_loop("FUTURES", futures_url)
    )


def process_clob_message(data: dict):
    """Parse incoming event data from the Polymarket CLOB WebSocket stream."""
    if not isinstance(data, dict):
        return
    event_type = data.get("event_type", "")
    
    # Handle price_change
    if event_type == "price_change":
        for change in data.get("price_changes", []):
            aid = change.get("asset_id")
            best_bid = change.get("best_bid")
            best_ask = change.get("best_ask")
            if aid and best_bid is not None and best_ask is not None:
                mid = (safe_float(best_bid) + safe_float(best_ask)) / 2
                spread = safe_float(best_ask) - safe_float(best_bid)
                with g_state.lock:
                    g_state.clob_prices[aid] = {"yes_price": mid, "last_update": time.time()}
                    g_state.clob_spreads[aid] = spread
                g_state.redraw_event.set()
                    
    # Handle best_bid_ask
    elif event_type == "best_bid_ask":
        aid = data.get("asset_id") or data.get("token_id")
        best_bid = data.get("best_bid")
        best_ask = data.get("best_ask")
        if aid and best_bid is not None and best_ask is not None:
            mid = (safe_float(best_bid) + safe_float(best_ask)) / 2
            spread = safe_float(best_ask) - safe_float(best_bid)
            with g_state.lock:
                g_state.clob_prices[aid] = {"yes_price": mid, "last_update": time.time()}
                g_state.clob_spreads[aid] = spread
            g_state.redraw_event.set()
                
    # Handle book snapshots
    elif event_type == "book":
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        aid = data.get("asset_id") or data.get("token_id")
        if aid and bids and asks:
            best_bid = safe_float(bids[-1].get("price", 0))
            best_ask = safe_float(asks[0].get("price", 0))
            mid = (best_bid + best_ask) / 2
            spread = best_ask - best_bid
            with g_state.lock:
                g_state.clob_prices[aid] = {"yes_price": mid, "last_update": time.time()}
                g_state.clob_spreads[aid] = spread
            g_state.redraw_event.set()


async def polymarket_clob_listener():
    """Connect to Polymarket CLOB WebSocket using the correct user agent and list-unpacking."""
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    while True:
        try:
            async with websockets.connect(url, additional_headers=headers, ping_interval=20, ping_timeout=10) as ws:
                subscribed_markets = set()
                
                while True:
                    with g_state.lock:
                        current_active_tokens = set(g_state.active_market_ids)
                    
                    # Replace subscription list if it changed
                    if current_active_tokens != subscribed_markets:
                        sub_msg = {
                            "type": "market",
                            "assets_ids": list(current_active_tokens),
                            "custom_feature_enabled": True
                        }
                        await ws.send(json.dumps(sub_msg))
                        subscribed_markets = set(current_active_tokens)
                    
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
                        payload = json.loads(msg)
                        if isinstance(payload, list):
                            for item in payload:
                                process_clob_message(item)
                        else:
                            process_clob_message(payload)
                    except asyncio.TimeoutError:
                        pass
        except Exception:
            await asyncio.sleep(0.5)  # Reconnect


def run_ws_event_loop():
    """Background thread worker to run the async listeners."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(binance_spot_listener())
    loop.create_task(polymarket_clob_listener())
    loop.run_forever()


# Start background tasks
resolver_thread = threading.Thread(target=run_market_resolver_loop, daemon=True)
resolver_thread.start()

ws_thread = threading.Thread(target=run_ws_event_loop, daemon=True)
ws_thread.start()


# ── File Loading & State Processing ───────────────────────────────────────────

_file_caches = {}

def load_json_file(file_path: Path) -> dict:
    """Safely load JSON, caching by mtime to avoid redundant disk read/parse overhead."""
    if not file_path.exists():
        return {}
    try:
        mtime = os.path.getmtime(file_path)
    except Exception:
        mtime = 0.0
        
    global _file_caches
    if file_path in _file_caches:
        cached_mtime, cached_data = _file_caches[file_path]
        if mtime == cached_mtime:
            return cached_data

    for _ in range(3):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _file_caches[file_path] = (mtime, data)
                return data
        except (json.JSONDecodeError, PermissionError):
            time.sleep(0.05)
            
    if file_path in _file_caches:
        return _file_caches[file_path][1]
    return {}


def generate_trade_history_report(closed_positions):
    """Write all closed trades to a local markdown report file for in-depth analysis."""
    report_path = DATA_DIR / "trade_history_report.md"
    try:
        total = len(closed_positions)
        wins = sum(1 for p in closed_positions if safe_float(p.get("realized_pnl", 0.0)) > 0.01)
        losses = sum(1 for p in closed_positions if safe_float(p.get("realized_pnl", 0.0)) < -0.01)
        pnl = sum(safe_float(p.get("realized_pnl", 0.0)) for p in closed_positions)
        breakevens = sum(1 for p in closed_positions if -0.01 <= safe_float(p.get("realized_pnl", 0.0)) <= 0.01)
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0.0
        
        lines = [
            "# ZiSi-v2 - Complete Trade History Report",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## Summary Metrics",
            f"- **Total Trades:** {total}",
            f"- **Wins / Losses:** {wins}W / {losses}L",
            f"- **Win Rate:** {win_rate:.1f}%",
            f"- **Total Realized P&L:** ${pnl:+.2f} USDC",
            "",
            "## Closed Positions List",
            "| Closed Time (UTC) | Asset | TF | Direction | Size | Entry Price | Exit Price | Hold | Exit Reason | Realized P&L |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        
        for pos in closed_positions:
            title = pos.get("event_title", "")
            asset = "UNKNOWN"
            for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]:
                if f"[{possible}]" in title.upper() or possible in title.upper():
                    asset = possible
                    break
            tf = "5m"
            if "15M" in title.upper():
                tf = "15m"
            elif "1H" in title.upper():
                tf = "1h"
            
            pnl_val = safe_float(pos.get("realized_pnl", 0.0))
            pnl_str = f"${pnl_val:+.2f}"
            hold_min = safe_float(pos.get("hold_hours", 0.0)) * 60
            
            lines.append(
                f"| {pos.get('exit_time', '')} | {asset} | {tf} | {pos.get('direction', 'YES')} | ${pos.get('size', 0.0):.2f} | {pos.get('entry_price', 0.0)} | {pos.get('exit_price', 0.0)} | {hold_min:.1f}m | {pos.get('exit_reason', '')} | {pnl_str} |"
            )
            
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass
_last_closed_count = -1


def sync_file_states():
    """Load latest states from local files into global state."""
    global _last_closed_count
    account = load_json_file(STATE_FILE)
    positions = load_json_file(POSITIONS_FILE)
    regime = load_json_file(REGIME_FILE)
    sentiment = load_json_file(SENTIMENT_FILE)
    chainlink = load_json_file(CHAINLINK_FILE)
    hft = load_json_file(HFT_METRICS_FILE)
    potential_trades = load_json_file(POTENTIAL_TRADES_FILE)

    with g_state.lock:
        g_state.account_state = account
        g_state.positions_state = positions
        g_state.regime_state = regime
        g_state.sentiment_state = sentiment
        g_state.chainlink_prices = chainlink
        g_state.hft_metrics = hft
        g_state.potential_trades = potential_trades
        
        # Pre-populate spot prices from Chainlink at startup to prevent "CONNECTING..."
        for asset in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]:
            if g_state.spot_prices.get(asset, 0.0) == 0.0:
                cl_entry = chainlink.get(asset, {})
                cl_price = safe_float(cl_entry.get("price", 0.0)) if isinstance(cl_entry, dict) else safe_float(cl_entry or 0.0)
                if cl_price > 0.0:
                    g_state.spot_prices[asset] = cl_price
        
        # Merge active position token IDs directly with resolved token IDs
        active_list = positions.get("active", [])
        active_ids = set()
        for pos in active_list:
            if pos.get("market_id"):
                active_ids.add(pos["market_id"])
            if pos.get("yes_market_id"):
                active_ids.add(pos["yes_market_id"])
        
        resolved_token_ids = set()
        for token_dict in g_state.asset_token_ids.values():
            resolved_token_ids.add(token_dict["yes"])
            resolved_token_ids.add(token_dict["no"])
            
        g_state.active_market_ids = active_ids.union(resolved_token_ids)
        
        # Generate persistent trade history report locally only when new trades are closed
        closed_positions = list(positions.get("closed", []))
        if len(closed_positions) != _last_closed_count:
            _last_closed_count = len(closed_positions)
            generate_trade_history_report(closed_positions)


def tail_log_file(file_path: Path, num_lines: int = 10, offset: int = 0) -> list[str]:
    """Tail the log file safely with scroll offset without reading the whole file to prevent I/O blocking."""
    if not file_path.exists():
        return [f"[{COLOR_LABEL}]Waiting for log file to generate...[/{COLOR_LABEL}]"]
    try:
        with open(file_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            if file_size == 0:
                return []
                
            needed = num_lines + offset
            chunk_size = max(1024, needed * 150)
            lines = []
            while chunk_size <= 262144 and len(lines) <= needed:
                seek_offset = min(file_size, chunk_size)
                f.seek(file_size - seek_offset)
                chunk = f.read(seek_offset).decode("utf-8", errors="ignore")
                lines = [l for l in chunk.splitlines() if "[HISTORY] Persisted" not in l]
                if seek_offset == file_size:
                    break
                chunk_size *= 2
                
            total_lines = len(lines)
            max_offset = max(0, total_lines - num_lines)
            if offset > max_offset:
                offset = max_offset
                with g_state.lock:
                    g_state.logs_scroll_offset = offset
                    
            if offset > 0:
                end_idx = -offset
                start_idx = -num_lines - offset
                if abs(start_idx) > len(lines):
                    start_idx = 0
                return lines[start_idx:end_idx]
            else:
                return lines[-num_lines:]
    except Exception as e:
        return [f"[#ff746c]Error reading logs: {e}[/#ff746c]"]


def colorize_log_line(line: str) -> Text:
    """Apply visual hierarchy to logs using Titanium Gray as the default base."""
    clean_line = line.strip()
    text = Text.from_ansi(clean_line)
    lower_line = clean_line.lower()
    
    style_up = f"bold {COLOR_PASTEL_GREEN}"
    style_down = f"bold {COLOR_PASTEL_RED}"
    style_yes = f"bold {COLOR_PASTEL_GREEN}"
    style_no = f"bold {COLOR_PASTEL_RED}"
    style_win = f"bold {COLOR_PASTEL_GREEN}"
    style_loss = f"bold {COLOR_PASTEL_PINK}"
    style_stop = f"bold {COLOR_PASTEL_RED}"
    style_target = f"bold {COLOR_PASTEL_GREEN}"
    style_inversion = "bold #f5f5dc"
    
    if "\033" not in clean_line:
        if "[netting-exit]" in lower_line:
            if "target" in lower_line:
                text.stylize(f"bold {COLOR_PASTEL_GREEN}")
            else:
                text.stylize(f"bold {COLOR_PASTEL_RED}")
        elif "slippage" in lower_line or "slippage_abort" in lower_line:
            text.stylize("bold #f5f5dc")
        elif "error" in lower_line or "exception" in lower_line or "fail" in lower_line or "stop loss" in lower_line:
            text.stylize(f"bold {COLOR_PASTEL_RED}")
        elif "warning" in lower_line or "paused" in lower_line:
            text.stylize("bright_yellow")
        elif any(k in lower_line for k in (
            "skip", "veto", "kelly", "confirm", "sizer", "size", "ptc", "potential", 
            "pre-flight", "preflight", "breaker", "sentiment", "leader-prop", 
            "ttl-gate", "markov", "duration-wr", "coinglass", "lunarcrush", "ladder"
        )):
            text.stylize("#E5DECA")
        else:
            text.stylize(COLOR_LABEL)  # Titanium Gray default

    # Regex Highlights for tokens inside logs
    text.highlight_regex(r"\bUP\b", style_up)
    text.highlight_regex(r"\[UP\]", style_up)
    text.highlight_regex(r"\bDOWN\b", style_down)
    text.highlight_regex(r"\[DOWN\]", style_down)
    text.highlight_regex(r"\bYES\b", style_yes)
    text.highlight_regex(r"\[YES\]", style_yes)
    text.highlight_regex(r"\bNO\b", style_no)
    text.highlight_regex(r"\[NO\]", style_no)
    text.highlight_regex(r"\bWIN\b", style_win)
    text.highlight_regex(r"\(WIN\)", style_win)
    text.highlight_regex(r"\bLOSS\b", style_loss)
    text.highlight_regex(r"\(LOSS\)", style_loss)
    text.highlight_regex(r"STOP LOSS HIT", style_stop)
    text.highlight_regex(r"STOP LOSS", style_stop)
    text.highlight_regex(r"TARGET HIT", style_target)
    text.highlight_regex(r"TARGET", style_target)
    text.highlight_regex(r"MARKET EXPIRED", style_stop)
    text.highlight_regex(r"INVERSION", style_inversion)
    text.highlight_regex(r"\[INVERSION\]", style_inversion)
    text.highlight_regex(r"SLIPPAGE_ABORT", style_inversion)
    text.highlight_regex(r"\bHEALTHY\b", f"bold {COLOR_PASTEL_GREEN}")
    text.highlight_regex(r"\bRECOVERING\b", "bold #ffb347")
    text.highlight_regex(r"\bACTIVE\b", f"bold {COLOR_PASTEL_GREEN}")
    text.highlight_regex(r"\bES\b", f"bold {COLOR_ES}")
    text.highlight_regex(r"\bEX\b", f"bold {COLOR_EX}")
    text.highlight_regex(r"\bLS\b", f"bold {COLOR_LS}")
    text.highlight_regex(r"Tranche A", f"bold {COLOR_ES}")
    text.highlight_regex(r"Tranche B", f"bold {COLOR_EX}")
    text.highlight_regex(r"HEAVY DRAWDOWN", f"bold {COLOR_PASTEL_RED}")
    text.highlight_regex(r"LOSING STREAK", f"bold {COLOR_PASTEL_RED}")
    text.highlight_regex(r"\bNORMAL\b", f"bold {COLOR_PASTEL_GREEN}")
    text.highlight_regex(r"\bSTABLE\b", f"bold {COLOR_PASTEL_GREEN}")
    
    return text


def format_iso_timestamp(iso_str: str) -> str:
    """Convert ISO timestamp to YYYY-MM-DD HH:MM:SS SAST."""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        # Add 2 hours for SAST (UTC+2)
        sast_hour = (dt.hour + 2) % 24
        return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d} {sast_hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    except Exception:
        return iso_str[:19]


def get_uptime_str(start_time: float) -> str:
    """Format duration into a readable uptime string."""
    diff = int(time.time() - start_time)
    days, remain = divmod(diff, 86400)
    hours, remain = divmod(remain, 3600)
    minutes, seconds = divmod(remain, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ── Render Panels ─────────────────────────────────────────────────────────────

def build_header_panel() -> Panel:
    """Build system status clocks and candle close countdowns."""
    now = time.time()
    now_utc = datetime.now(timezone.utc)
    
    # SAST & UTC clocks in Yellow
    sast_hour = (now_utc.hour + 2) % 24
    sast_str = f"{sast_hour:02d}:{now_utc.minute:02d}:{now_utc.second:02d} SAST"
    utc_str = now_utc.strftime("%H:%M:%S UTC")

    # Countdown calculations
    sec_5m = 300 - (int(now) % 300)
    
    cd_5m_str = f"{sec_5m // 60:02d}:{sec_5m % 60:02d}"
    
    style_5m = COLOR_ASSET

    # Uptime in Titanium Gray
    uptime = get_uptime_str(g_state.start_time)
    
    # Log liveness
    liveness_status = "[#ff746c]OFFLINE[/#ff746c]"
    if LOG_FILE.exists():
        mtime = os.path.getmtime(LOG_FILE)
        if now - mtime < 360.0:
            liveness_status = f"[bold {COLOR_PASTEL_GREEN}]● ACTIVE[/bold {COLOR_PASTEL_GREEN}]"
        else:
            liveness_status = "[bold yellow]● STANDBY[/bold yellow]"

    date_str = now_utc.strftime("%Y-%m-%d")
    location_str = "Johannesburg"

    header_text = Text.assemble(
        ("ZiSi-v2 ", f"bold {COLOR_LABEL}"),  # Naming alignment: ZiSi-v2 in Titanium Gray
        ("│ ", "bright_black"),
        ("Status: ", f"bold {COLOR_LABEL}"),
        Text.from_markup(liveness_status),
        (" │ ", "bright_black"),
        ("UTC: ", f"bold {COLOR_LABEL}"),
        (utc_str, f"bold {COLOR_ASSET}"),
        (" │ ", "bright_black"),
        ("Date: ", f"bold {COLOR_LABEL}"),
        (f"{date_str} ({location_str})", f"bold {COLOR_ASSET}"),
        (" │ ", "bright_black"),
        ("SAST: ", f"bold {COLOR_LABEL}"),
        (sast_str, f"bold {COLOR_ASSET}"),
        (" │ ", "bright_black"),
        ("5m Candle: ", f"bold {COLOR_LABEL}"),
        (cd_5m_str, style_5m),
        (" │ ", "bright_black"),
        ("Uptime: ", f"bold {COLOR_LABEL}"),
        (uptime, f"bold {COLOR_ASSET}")
    )
    
    return Panel(Align.center(header_text), box=ROUNDED, style="bright_black")


def format_cents(val: float) -> str:
    if val is None or val == 0:
        return "-"
    cents = round(val * 100, 2)
    if cents == int(cents):
        return f"{int(cents)}¢"
    s = f"{cents:.2f}"
    if s.endswith("0"):
        s = s[:-1]
    return f"{s}¢"


def make_sparkline(values: list[float]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return "#"
    points = values[-12:]
    min_val = min(points)
    max_val = max(points)
    val_range = max_val - min_val
    if val_range == 0:
        return "-" * len(points)
    spark_chars = ["_", ".", "-", "~", "=", "+", "*", "#"]
    sparkline = []
    for val in points:
        idx = int((val - min_val) / val_range * (len(spark_chars) - 1))
        sparkline.append(spark_chars[idx])
    return "".join(sparkline)


def build_equity_chart(width: int = 34) -> str:
    try:
        from data.balance_history import load_history
        history = load_history()
    except Exception:
        history = []
        
    if not history:
        return "[grey50]  Chart: No history recorded yet[/grey50]"
        
    balances = [safe_float(h["balance"]) for h in history]
    if len(balances) < 2:
        return "[grey50]  Chart: Accumulating data points...[/grey50]"
        
    height = 3
    val_min = min(balances)
    val_max = max(balances)
    val_range = val_max - val_min
    if val_range == 0:
        val_range = 1.0
        
    # sample to match width
    sampled_points = []
    for i in range(width):
        idx = int(i * (len(balances) - 1) / (width - 1))
        sampled_points.append(balances[idx])
        
    grid = [[" " for _ in range(width)] for _ in range(height)]
    
    for col, val in enumerate(sampled_points):
        pct = (val - val_min) / val_range
        fill_height = pct * height
        for r in range(height):
            row_from_bottom = height - 1 - r
            if fill_height >= row_from_bottom + 0.8:
                grid[r][col] = "█"
            elif fill_height >= row_from_bottom + 0.4:
                grid[r][col] = "▄"
            else:
                grid[r][col] = " "
                
    trend_color = COLOR_PASTEL_GREEN if balances[-1] >= balances[0] else COLOR_PASTEL_RED
    
    chart_lines = []
    for r in range(height):
        if r == 0:
            lbl = f"${val_max:6.2f} ┐"
        elif r == height - 1:
            lbl = f"${val_min:6.2f} ┘"
        else:
            lbl = "        │"
        row_content = "".join(grid[r])
        chart_lines.append(f"  [grey60]{lbl}[/grey60] [bold {trend_color}]{row_content}[/bold {trend_color}]")
        
    return "\n".join(chart_lines)


def build_metrics_panel(fullscreen: bool = False) -> Panel:
    """Build performance summary showing real-time fluctuating unrealized stats."""
    with g_state.lock:
        start_bal = safe_float(g_state.account_state.get("starting_balance", 50.00))
        current_bal = safe_float(g_state.account_state.get("balance", start_bal))
        summary = g_state.positions_state.get("summary", {})
        active_positions = g_state.positions_state.get("active", [])

    realized = safe_float(summary.get("realized_pnl", 0.0))
    
    # Calculate live unrealized PnL from real-time WebSocket feeds
    total_live_unrealized = 0.0
    for pos in active_positions:
        market_id = pos.get("market_id")
        shares = safe_float(pos.get("shares", 0.0))
        size = safe_float(pos.get("size", 0.0))
        direction = pos.get("direction", "YES")
        
        live_entry = g_state.clob_prices.get(market_id)
        if live_entry and shares > 0:
            yes_price = live_entry["yes_price"]
            live_price = yes_price if direction == "YES" else (1.0 - yes_price)
            unreal = (shares * live_price) - size
            total_live_unrealized += unreal
        else:
            total_live_unrealized += safe_float(pos.get("unrealized_pnl", 0.0))

    live_balance = current_bal + total_live_unrealized
    realized_roi = (realized / start_bal) * 100 if start_bal > 0 else 0.0

    wins = int(summary.get("win_count", 0))
    losses = int(summary.get("loss_count", 0))
    breakevens = int(summary.get("breakeven_count", 0))
    total_closed = wins + losses + breakevens
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0.0

    real_color = COLOR_PASTEL_GREEN if realized > 0.01 else (COLOR_PASTEL_RED if realized < -0.01 else COLOR_LABEL)
    unreal_color = COLOR_PASTEL_GREEN if total_live_unrealized > 0.01 else (COLOR_PASTEL_RED if total_live_unrealized < -0.01 else COLOR_LABEL)

    metrics_table = Table.grid(expand=True, padding=(0, 1))
    metrics_table.add_column("Metric", style=f"bold {COLOR_LABEL}", width=21)
    metrics_table.add_column("Value", justify="right")

    metrics_table.add_row("Start Capital:", f"[{COLOR_LABEL}]${start_bal:,.2f} USDC[/{COLOR_LABEL}]")
    metrics_table.add_row("Live Capital:", f"[{COLOR_LABEL}]${live_balance:,.2f} USDC[/{COLOR_LABEL}]")
    metrics_table.add_row("Realized P&L:", f"[{real_color}]${realized:+,.2f} ({realized_roi:+.2f}%)[/{real_color}]" if realized != 0 else f"[{COLOR_LABEL}]$0.00 (0.00%)[/{COLOR_LABEL}]")
    metrics_table.add_row("Live Unrealized P&L:", f"[{unreal_color}]${total_live_unrealized:+,.2f}[/{unreal_color}]" if total_live_unrealized != 0 else f"[{COLOR_LABEL}]$0.00[/{COLOR_LABEL}]")
    metrics_table.add_row("Total Trades:", f"[grey70]{total_closed}T[/grey70] | [#8ae28a]{wins}W[/#8ae28a] / [#ff746c]{losses}L[/#ff746c] / [grey50]{breakevens}BE[/grey50] ([{COLOR_LABEL}]{win_rate:.1f}% WR[/{COLOR_LABEL}])")


    # Win/Loss breakdown and P&L by asset
    asset_stats = {}
    regime_stats = {}
    session_stats = {}
    hourly_stats = {}
    half_stats = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
    runner_stats = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
    ls_stats = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
    band_stats = {
        "0-19¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "20-39¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "40-59¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "60-79¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "80-99¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
    }
    slippage_stats = {
        "0 to 5¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "5 to 10¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "10 to 15¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "15 to 20¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
        "20 to 25¢": {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []},
    }
    closed_pos = g_state.positions_state.get("closed", [])

    for pos in (closed_pos or []):
        title = pos.get("event_title", "Unknown")
        asset = "UNKNOWN"
        for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE"]:
            if f"[{possible}]" in title.upper() or possible in title.upper():
                asset = possible
                break
        pnl = safe_float(pos.get("realized_pnl", 0.0))
        hold_hours = safe_float(pos.get("hold_hours", 0.0))
        hold_sec = int(hold_hours * 3600)
        
        # Slippage stats
        raw_slp = pos.get("slp")
        if raw_slp is None:
            raw_slp = pos.get("slippage", 0.0)
        slp_cents = abs(safe_float(raw_slp or 0.0))

        if 0.0 <= slp_cents < 5.0:
            slp_key = "0 to 5¢"
        elif 5.0 <= slp_cents < 10.0:
            slp_key = "5 to 10¢"
        elif 10.0 <= slp_cents < 15.0:
            slp_key = "10 to 15¢"
        elif 15.0 <= slp_cents < 20.0:
            slp_key = "15 to 20¢"
        else:
            slp_key = "20 to 25¢"

        slippage_stats[slp_key]["pnl"] += pnl
        slippage_stats[slp_key]["hold_secs"].append(hold_sec)
        if pnl > 0.01:
            slippage_stats[slp_key]["wins"] += 1
        elif pnl < -0.01:
            slippage_stats[slp_key]["losses"] += 1
        else:
            slippage_stats[slp_key]["breakevens"] += 1

        # Regime stats
        _reg = str(pos.get("regime", "UNKNOWN")).upper()
        if _reg not in regime_stats:
            regime_stats[_reg] = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
        regime_stats[_reg]["pnl"] += pnl
        regime_stats[_reg]["hold_secs"].append(hold_sec)
        if pnl > 0.01:
            regime_stats[_reg]["wins"] += 1
        elif pnl < -0.01:
            regime_stats[_reg]["losses"] += 1
        else:
            regime_stats[_reg]["breakevens"] += 1
        
        if asset not in asset_stats:
            asset_stats[asset] = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
        asset_stats[asset]["pnl"] += pnl
        asset_stats[asset]["hold_secs"].append(hold_sec)
        if pnl > 0.01:
            asset_stats[asset]["wins"] += 1
        elif pnl < -0.01:
            asset_stats[asset]["losses"] += 1
        else:
            asset_stats[asset]["breakevens"] += 1

        # Scale Breakdown stats (supporting both old TRANCHE names and new HALF/RUNNER/ES/RS names)
        tranche_type = str(pos.get("tranche", "")).upper()
        entry_type = str(pos.get("entry_type", "")).upper()
        event_title = str(pos.get("event_title", "")).upper()
        reason = str(pos.get("exit_reason", "")).upper()

        is_ls = "LS" in entry_type or "LS" in tranche_type or "SNIPE" in entry_type or "SNIPE" in event_title or "LS" in reason or "LATE" in reason
        is_half = not is_ls and (tranche_type == "A" or "HALF" in reason or "TRANCHE_A" in reason or "ES" in reason or "ES" in entry_type)
        is_runner = not is_ls and (tranche_type == "B" or "RUNNER" in reason or "TRANCHE_B" in reason or "RS" in reason or "EX" in reason or "EX" in entry_type)

        if is_ls:
            ls_stats["pnl"] += pnl
            ls_stats["hold_secs"].append(hold_sec)
            if pnl > 0.01:
                ls_stats["wins"] += 1
            elif pnl < -0.01:
                ls_stats["losses"] += 1
            else:
                ls_stats["breakevens"] += 1
        elif is_half:
            half_stats["pnl"] += pnl
            half_stats["hold_secs"].append(hold_sec)
            if pnl > 0.01:
                half_stats["wins"] += 1
            elif pnl < -0.01:
                half_stats["losses"] += 1
            else:
                half_stats["breakevens"] += 1
        elif is_runner:
            runner_stats["pnl"] += pnl
            runner_stats["hold_secs"].append(hold_sec)
            if pnl > 0.01:
                runner_stats["wins"] += 1
            elif pnl < -0.01:
                runner_stats["losses"] += 1
            else:
                runner_stats["breakevens"] += 1

        # Entry Bands stats
        entry_price = safe_float(pos.get("entry_price", 0.0))
        cents = round(entry_price * 100)
        if 0 <= cents <= 19:
            band_key = "0-19¢"
        elif 20 <= cents <= 39:
            band_key = "20-39¢"
        elif 40 <= cents <= 59:
            band_key = "40-59¢"
        elif 60 <= cents <= 79:
            band_key = "60-79¢"
        else:
            band_key = "80-99¢"

        band_stats[band_key]["pnl"] += pnl
        band_stats[band_key]["hold_secs"].append(hold_sec)
        if pnl > 0.01:
            band_stats[band_key]["wins"] += 1
        elif pnl < -0.01:
            band_stats[band_key]["losses"] += 1
        else:
            band_stats[band_key]["breakevens"] += 1

        # Timezone conversions & session/hourly breakdown
        try:
            from datetime import datetime, timezone, timedelta
            if pos.get("entry_time"):
                dt_utc = datetime.fromisoformat(pos.get("entry_time").replace('Z', '+00:00'))
                
                # Session classifier
                def get_session_name(dt) -> str:
                    hour = dt.hour
                    if 8 <= hour < 13:
                        return "London Session"
                    elif 13 <= hour < 16:
                        return "London/NY Overlap"
                    elif 16 <= hour < 21:
                        return "New York Session"
                    elif 21 <= hour < 24:
                        return "Pacific/Sydney Session"
                    else:
                        return "Asian/Tokyo Session"
                
                sess_name = get_session_name(dt_utc)
                if sess_name not in session_stats:
                    session_stats[sess_name] = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
                session_stats[sess_name]["pnl"] += pnl
                session_stats[sess_name]["hold_secs"].append(hold_sec)
                if pnl > 0.01:
                    session_stats[sess_name]["wins"] += 1
                elif pnl < -0.01:
                    session_stats[sess_name]["losses"] += 1
                else:
                    session_stats[sess_name]["breakevens"] += 1
                
                # Hourly SAST (UTC+2) classifier
                tz_sast = timezone(timedelta(hours=2))
                dt_sast = dt_utc.astimezone(tz_sast)
                hr_key = f"{dt_sast.hour:02d}:00 SAST"
                if hr_key not in hourly_stats:
                    hourly_stats[hr_key] = {"wins": 0, "losses": 0, "breakevens": 0, "pnl": 0.0, "hold_secs": []}
                hourly_stats[hr_key]["pnl"] += pnl
                hourly_stats[hr_key]["hold_secs"].append(hold_sec)
                if pnl > 0.01:
                    hourly_stats[hr_key]["wins"] += 1
                elif pnl < -0.01:
                    hourly_stats[hr_key]["losses"] += 1
                else:
                    hourly_stats[hr_key]["breakevens"] += 1
        except Exception:
            pass

    breakdown_rows = []

    if asset_stats:
        breakdown_rows.append(("", ""))
        breakdown_rows.append(("[bold grey70]Asset Breakdown:[/bold grey70]", ""))
        for asset, stats in sorted(asset_stats.items()):
            pnl_val = stats["pnl"]
            pnl_color = COLOR_PASTEL_GREEN if pnl_val >= 0.01 else (COLOR_PASTEL_RED if pnl_val < -0.01 else COLOR_LABEL)
            pnl_pct = (pnl_val / start_bal) * 100 if start_bal > 0.0 else 0.0
            
            # Average hold time
            avg_hold_sec = int(sum(stats["hold_secs"]) / len(stats["hold_secs"])) if stats["hold_secs"] else 0
            if avg_hold_sec >= 60:
                avg_hold_str = f"{avg_hold_sec // 60}m {avg_hold_sec % 60}s"
            else:
                avg_hold_str = f"{avg_hold_sec}s"
                
            tot = stats['wins'] + stats['losses'] + stats['breakevens']
            wr = (stats['wins'] / (stats['wins'] + stats['losses']) * 100) if (stats['wins'] + stats['losses']) > 0 else 0.0
            breakdown_rows.append((
                f"  [{COLOR_ASSET}]{asset}:[/{COLOR_ASSET}]",
                f"[grey70]{tot}T[/grey70] | [#8ae28a]{stats['wins']}W[/#8ae28a] / [#ff746c]{stats['losses']}L[/#ff746c] / [grey50]{stats['breakevens']}BE[/grey50] ({wr:.1f}% WR) | ([{pnl_color}]${pnl_val:+,.2f}[/{pnl_color}], [{pnl_color}]{pnl_pct:+,.1f}%[/{pnl_color}]) | avg hold: {avg_hold_str}"
            ))

    def format_breakdown_line(stats_dict):
        w = stats_dict["wins"]
        l = stats_dict["losses"]
        be = stats_dict["breakevens"]
        total = w + l + be
        wr = (w / (w + l) * 100) if (w + l) > 0 else 0.0
        pnl_val = stats_dict["pnl"]
        pnl_color = COLOR_PASTEL_GREEN if pnl_val >= 0.01 else (COLOR_PASTEL_RED if pnl_val < -0.01 else COLOR_LABEL)
        pnl_pct = (pnl_val / start_bal) * 100 if start_bal > 0.0 else 0.0

        avg_hold_sec = int(sum(stats_dict["hold_secs"]) / len(stats_dict["hold_secs"])) if stats_dict["hold_secs"] else 0
        if avg_hold_sec >= 60:
            avg_hold_str = f"{avg_hold_sec // 60}m {avg_hold_sec % 60}s"
        else:
            avg_hold_str = f"{avg_hold_sec}s"

        return f"[grey70]{total}T[/grey70] | [#8ae28a]{w}W[/#8ae28a] / [#ff746c]{l}L[/#ff746c] / [grey50]{be}BE[/grey50] ({wr:.1f}% WR) | [{pnl_color}]${pnl_val:+,.2f}[/{pnl_color}] ([{pnl_color}]{pnl_pct:+,.1f}%[/{pnl_color}]) | avg hold: {avg_hold_str}"

    # Scale Breakdown Display
    breakdown_rows.append(("", ""))
    breakdown_rows.append(("[bold grey70]Scale Breakdown:[/bold grey70]", ""))
    breakdown_rows.append((f"  Early Scalping ([bold {COLOR_ES}]ES[/bold {COLOR_ES}]):", format_breakdown_line(half_stats)))
    breakdown_rows.append((f"  Extended Execution ([bold {COLOR_EX}]EX[/bold {COLOR_EX}]):", format_breakdown_line(runner_stats)))

    # Entry Bands Display
    breakdown_rows.append(("", ""))
    breakdown_rows.append(("[bold grey70]Entry Bands:[/bold grey70]", ""))
    for band_name in ["0-19¢", "20-39¢", "40-59¢", "60-79¢", "80-99¢"]:
        stats_b = band_stats[band_name]
        if (stats_b["wins"] + stats_b["losses"]) > 0:
            breakdown_rows.append((f"  {band_name}:", format_breakdown_line(stats_b)))

    # Session Breakdown Display
    if session_stats:
        breakdown_rows.append(("", ""))
        breakdown_rows.append(("[bold grey70]Session Breakdown:[/bold grey70]", ""))
        sess_order = ["Asian/Tokyo Session", "London Session", "London/NY Overlap", "New York Session", "Pacific/Sydney Session"]
        for sess_name in sess_order:
            if sess_name in session_stats and (session_stats[sess_name]["wins"] + session_stats[sess_name]["losses"]) > 0:
                breakdown_rows.append((f"  {sess_name}:", format_breakdown_line(session_stats[sess_name])))

    # Hourly Breakdown Display
    if hourly_stats:
        breakdown_rows.append(("", ""))
        breakdown_rows.append(("[bold grey70]Hourly Breakdown (SAST):[/bold grey70]", ""))
        for hr_key in sorted(hourly_stats.keys()):
            if (hourly_stats[hr_key]["wins"] + hourly_stats[hr_key]["losses"]) > 0:
                breakdown_rows.append((f"  {hr_key}:", format_breakdown_line(hourly_stats[hr_key])))

    # Read offset and console height to slice visible rows
    with g_state.lock:
        offset = g_state.metrics_scroll_offset
    
    h = console.height or 40
    max_lines = max(5, h - 10) if fullscreen else 14
    
    # Append sliced rows to layout table
    for r in breakdown_rows[offset : offset + max_lines]:
        metrics_table.add_row(*r)

    # Dynamic scroll indicator in panel title
    scroll_indicator = f" [Scroll: -{offset}]" if offset > 0 else ""
    title_str = f"Performance Summary{scroll_indicator} (K/J to Scroll, M or H to Minimize)" if fullscreen else f"Performance Summary{scroll_indicator} (K/J to Scroll, M to Fullscreen)"
    return Panel(metrics_table, title=f"[bold {COLOR_LABEL}]{title_str}[/bold {COLOR_LABEL}]", box=ROUNDED, border_style=COLOR_BORDER)


def build_spot_prices_panel() -> Panel:
    """Build pricing layout displaying spot, Chainlink, YES, NO, and Spread values."""
    table = Table(box=ROUNDED, expand=True, padding=(0, 0))
    table.add_column("Asset", header_style=f"bold {COLOR_LABEL}", style=f"bold {COLOR_ASSET}")
    table.add_column("Binance", justify="right", header_style=COLOR_LABEL, style=COLOR_VAL)
    table.add_column("Chainlink", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("YES", justify="right", header_style=COLOR_LABEL, style=COLOR_VAL)
    table.add_column("NO", justify="right", header_style=COLOR_LABEL, style=COLOR_VAL)
    table.add_column("Spread", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)

    with g_state.lock:
        spot_copy = dict(g_state.spot_prices)
        cl_copy = dict(g_state.chainlink_prices)
        clob_token_ids = dict(g_state.asset_token_ids)
        positions = list(g_state.positions_state.get("active", []))

    # Compile table rows for all assets
    for asset in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]:
        spot_price = spot_copy.get(asset, 0.0)
        
        # Decimal formatting based on asset price scale
        if asset == "DOGE":
            spot_str = f"${spot_price:.5f}" if spot_price > 0 else "CONNECTING..."
        else:
            spot_str = f"${spot_price:,.2f}" if spot_price > 0 else "CONNECTING..."
        
        # Load values from local oracle dumps
        cl_entry = cl_copy.get(asset, {})
        cl_price = safe_float(cl_entry.get("price", 0.0)) if isinstance(cl_entry, dict) else safe_float(cl_entry or 0.0)
        if asset == "DOGE":
            cl_str = f"${cl_price:.5f}" if cl_price > 0 else "-"
        else:
            cl_str = f"${cl_price:,.2f}" if cl_price > 0 else "-"
            
        # Resolve YES and NO token IDs for this asset
        token_info = clob_token_ids.get(asset, {})
        yes_tk = token_info.get("yes")
        no_tk = token_info.get("no")
        
        # Open positions overwrite (to match active trade token ID)
        for pos in positions:
            title = pos.get("event_title", "")
            if f"[{asset}]" in title.upper() or asset in title.upper():
                p_tk = pos.get("market_id")
                p_dir = pos.get("direction", "YES")
                if p_dir == "YES":
                    yes_tk = p_tk
                else:
                    no_tk = p_tk
                break
        
        yes_price_str = "-"
        no_price_str = "-"
        spread_str = "-"
        
        if yes_tk:
            # Query in-memory live WebSocket cache for the active YES token ID
            live_entry = g_state.clob_prices.get(yes_tk)
            spread = g_state.clob_spreads.get(yes_tk)
            if live_entry:
                yes_val = live_entry["yes_price"]
                yes_price_str = format_cents(yes_val)
                if spread is not None:
                    spread_str = f"{spread * 100:.1f}¢"
                # Infer NO price mathematically if not yet directly populated
                no_price_str = format_cents(1.0 - yes_val)
                
        if no_tk:
            live_entry_no = g_state.clob_prices.get(no_tk)
            if live_entry_no:
                no_val = live_entry_no["yes_price"]
                no_price_str = format_cents(no_val)
                # Infer YES price mathematically if not yet directly populated
                if yes_price_str == "-":
                    yes_price_str = format_cents(1.0 - no_val)

        table.add_row(asset, spot_str, cl_str, yes_price_str, no_price_str, spread_str)

    return Panel(table, title=f"[bold {COLOR_LABEL}]Spot & Oracle Price Matrix[/bold {COLOR_LABEL}]", box=ROUNDED, border_style=COLOR_BORDER)


def get_rolling_avg_slippage(window: int = 50) -> float:
    try:
        from pathlib import Path
        import json
        log_file = Path(__file__).parent / "data" / "slippage_log.jsonl"
        if not log_file.exists():
            return 0.0
            
        slippages = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "slippage_cents" in data:
                        slippages.append(safe_float(data["slippage_cents"]))
                except Exception:
                    continue
                    
        if not slippages:
            return 0.0
            
        last_n = slippages[-window:]
        return round(sum(last_n) / len(last_n), 2)
    except Exception:
        return 0.0


def get_rolling_fill_rate(window: int = 50) -> float:
    try:
        from pathlib import Path
        import json
        log_file = Path(__file__).parent / "data" / "order_placements.jsonl"
        if not log_file.exists():
            return 100.0
            
        events = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    events.append(data)
                except Exception:
                    continue
                    
        if not events:
            return 100.0
            
        order_status = {}
        for ev in events:
            oid = ev["order_id"]
            stat = ev["status"]
            order_status[oid] = stat
            
        unique_orders = list(order_status.values())[-window:]
        if not unique_orders:
            return 100.0
            
        filled = sum(1 for stat in unique_orders if stat == "FILLED")
        return round((filled / len(unique_orders)) * 100.0, 1)
    except Exception:
        return 100.0


def get_current_session() -> str:
    """Return active trading session(s) based on current UTC hour."""
    from datetime import datetime, timezone
    utc_hour = datetime.now(timezone.utc).hour
    
    sessions = []
    # London: 08:00 - 17:00 London local (typically 07:00 - 16:00 UTC)
    if 7 <= utc_hour < 16:
        sessions.append("LONDON")
    # New York: 08:00 - 17:00 NY local (typically 13:00 - 22:00 UTC)
    if 13 <= utc_hour < 22:
        sessions.append("NEW YORK")
    # Tokyo: 09:00 - 18:00 Tokyo local (typically 00:00 - 09:00 UTC)
    if 0 <= utc_hour < 9:
        sessions.append("TOKYO")
    # Sydney: 09:00 - 18:00 Sydney local (typically 23:00 - 08:00 UTC)
    if 23 <= utc_hour or utc_hour < 8:
        sessions.append("SYDNEY")
        
    return " / ".join(sessions) if sessions else "LATE WORK"


def build_regime_panel(fullscreen: bool = False) -> Panel:
    """Build the current regime classifications and indicators."""
    with g_state.lock:
        reg = dict(g_state.regime_state)
        hft = dict(g_state.hft_metrics)

    raw_reg = str(reg.get("regime", "UNKNOWN")).upper()
    
    # Load gate matrix data
    matrix_file = DATA_DIR / "gate_matrix.json"
    gate_assets = {}
    if matrix_file.exists():
        try:
            gate_data = json.loads(matrix_file.read_text(encoding="utf-8"))
            gate_assets = gate_data.get("assets", {})
        except Exception:
            pass

    # Mapping styles
    regime_color = "white"
    if raw_reg == "TRENDING":
        regime_color = "#c1e1c1 bold"
    elif raw_reg == "MEAN_REVERTING":
        regime_color = "yellow bold"
    elif raw_reg == "COMPRESSION":
        regime_color = "cyan bold"
    elif raw_reg == "VOLATILE_CHAOS":
        regime_color = "#ff746c bold"

    # Get live metrics
    curr_session = get_current_session()

    # Header Table
    header_table = Table.grid(expand=True, padding=(0, 2))
    header_table.add_column("Metric 1", style=f"bold {COLOR_LABEL}", width=20)
    header_table.add_column("Value 1", justify="left", style=COLOR_VAL)
    
    header_table.add_row(
        "Session:", f"[bold {COLOR_ASSET}]{curr_session}[/bold {COLOR_ASSET}]"
    )

    # Combined Layout Container
    panel_content = Table.grid(expand=True)
    panel_content.add_column("Col")
    panel_content.add_row(header_table)

    # Title with key guide
    title_guide = "R or H to Minimize" if fullscreen else "R to Fullscreen"
    title_str = f"Analytics [{title_guide}]"
    return Panel(panel_content, title=f"[bold {COLOR_LABEL}]{title_str}[/bold {COLOR_LABEL}]", box=ROUNDED, border_style=COLOR_BORDER)


def format_regime_str(regime: str) -> str:
    """Format and color regime names for table display."""
    r = str(regime).upper()
    if "MEAN" in r or "REVERT" in r:
        return f"[bold #f5f5dc]MEAN_REVERTING[/bold #f5f5dc]"
    elif "TREND" in r:
        return f"[bold #ffe5cc]TRENDING[/bold #ffe5cc]"
    elif "CHAOS" in r:
        return f"[bold magenta]VOLATILE_CHAOS[/bold magenta]"
    elif "COMPRESS" in r:
        return f"[bold #fff8dc]COMPRESSION[/bold #fff8dc]"
    else:
        return f"[grey50]{r}[/grey50]"


def build_active_positions_panel() -> Panel:
    """Build the active open positions table with full attributes and live PnL."""
    table = Table(box=ROUNDED, expand=True, padding=(0, 1))
    table.add_column("Entry Time (SAST)", justify="center", header_style=COLOR_LABEL, style=COLOR_ASSET)
    table.add_column("Asset", header_style=f"bold {COLOR_LABEL}", style=f"bold {COLOR_ASSET}")
    table.add_column("TF", justify="center", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Dir", justify="center", header_style=COLOR_LABEL)
    table.add_column("Size", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Entry Spot", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Mark Spot", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Entry Token", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Mark Token", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("TP/Target", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Hold", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("SLP", justify="right", header_style=COLOR_LABEL)
    table.add_column("Type", justify="center", header_style=COLOR_LABEL)
    table.add_column("Unrealized PnL", justify="right", header_style=COLOR_LABEL)

    with g_state.lock:
        active_positions = list(g_state.positions_state.get("active", []))
        spot_copy = dict(g_state.spot_prices)
        cl_copy = dict(g_state.chainlink_prices)
        fullscreen = g_state.fullscreen_mode == 'active'

    if not active_positions:
        table.add_row("-", "-", "-", "-", "-", "-", "-", "-", "-", "No active positions running", "-", "-", "-", "-")
    else:
        for pos in active_positions:
            title = pos.get("event_title", "Unknown")
            market_id = pos.get("market_id")
            
            # Asset parse (added DOGE)
            asset = "UNKNOWN"
            for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]:
                if f"[{possible}]" in title.upper() or possible in title.upper():
                    asset = possible
                    break
            
            # Timeframe parse
            tf = "5m"
            if "15M" in title.upper():
                tf = "15m"
            elif "1H" in title.upper():
                tf = "1h"
            elif "5M" in title.upper():
                tf = "5m"
            
            direction = pos.get("direction", "YES")
            dir_color = COLOR_PASTEL_GREEN if direction in ("YES", "UP") else COLOR_PASTEL_RED
            size = float(pos.get("size") or 0.0)
            
            entry_token = float(pos.get("entry_price") or 0.0)
            entry_spot = float(pos.get("entry_spot") or 0.0)
            
            # Get spot price: Chainlink first, Binance fallback
            live_spot = 0.0
            cl_entry = cl_copy.get(asset, {})
            if isinstance(cl_entry, dict):
                live_spot = float(cl_entry.get("price") or 0.0)
            else:
                live_spot = safe_float(cl_entry or 0.0)
            
            if live_spot <= 0.0:
                live_spot = float(spot_copy.get(asset) or 0.0)
            
            # Determine resolving state
            is_resolving = (pos.get("status") == "RESOLVING")
            if not is_resolving and pos.get("expiry_ts"):
                try:
                    import time
                    is_resolving = (time.time() >= safe_float(pos["expiry_ts"]))
                except Exception:
                    pass

            if is_resolving and entry_spot > 0 and live_spot > 0:
                direction_upper = direction.upper()
                if direction_upper in ("YES", "UP"):
                    won = (live_spot > entry_spot)
                else:
                    won = (live_spot < entry_spot)
                mark_token = 0.99 if won else 0.01
                unreal = (float(pos.get("shares") or 0.0) * mark_token) - size
            else:
                # Fetch WebSocket token price
                # If we have yes_market_id stored, query it as YES token is much more liquid.
                # Otherwise fallback to market_id.
                ref_id = pos.get("yes_market_id") or market_id
                live_entry = g_state.clob_prices.get(ref_id)
                if live_entry and not is_resolving:
                    yes_price = live_entry["yes_price"]
                    if pos.get("yes_market_id") and direction.upper() in ("NO", "DOWN"):
                        mark_token = round(1.0 - yes_price, 4)
                    else:
                        mark_token = yes_price
                    unreal = (float(pos.get("shares") or 0.0) * mark_token) - size
                else:
                    mark_token = float(pos.get("current_price") or entry_token or 0.0)
                    unreal = float(pos.get("unrealized_pnl") or 0.0)
            
            # Formulate spot entry estimations
            entry_spot = float(pos.get("entry_spot") or 0.0)
            if asset == "DOGE":
                entry_spot_str = f"${entry_spot:.5f}" if entry_spot > 0 else "-"
                mark_spot_str = f"${live_spot:.5f}" if live_spot > 0 else "-"
            else:
                entry_spot_str = f"${entry_spot:,.2f}" if entry_spot > 0 else "-"
                mark_spot_str = f"${live_spot:,.2f}" if live_spot > 0 else "-"
            
            unreal_color = COLOR_PASTEL_GREEN if unreal > 0.01 else (COLOR_PASTEL_RED if unreal < -0.01 else COLOR_LABEL)
            hold_min = float(pos.get("hold_minutes") or 0.0)
            hold_sec = int(hold_min * 60)
            hold_str = f"{hold_sec // 60}m {hold_sec % 60}s"
            
            tranche_type = str(pos.get("tranche", "")).upper()
            entry_type = str(pos.get("entry_type", "")).upper()
            event_title = str(pos.get("event_title", "Unknown")).upper()
            
            # Color active position type based on tranche closure state
            is_snipe = "LS" in entry_type or "SNIPE" in entry_type or "SNIPE" in event_title
            if is_snipe:
                type_str = f"[bold {COLOR_LS}]LS[/bold {COLOR_LS}]"
            elif pos.get("tranche_a_closed"):
                type_str = f"[bold {COLOR_EX}]EX[/bold {COLOR_EX}]"
            else:
                type_str = f"[bold {COLOR_ES}]ES[/bold {COLOR_ES}]"
            
            formatted_entry_ts = format_iso_timestamp(pos.get("entry_time", ""))

            slp_val = float(pos.get("slp") or 0.0)
            if abs(slp_val) < 0.01:
                slp_str = "[grey50]0.0¢[/grey50]"
            else:
                slp_color = COLOR_PASTEL_RED if slp_val > 0.01 else COLOR_PASTEL_GREEN
                slp_str = f"[{slp_color}]{slp_val:+.1f}¢[/{slp_color}]"

            table.add_row(
                formatted_entry_ts,
                asset,
                tf,
                f"[{dir_color}]{direction}[/{dir_color}]",
                f"${size:,.2f}",
                entry_spot_str,
                mark_spot_str,
                format_cents(entry_token),
                format_cents(mark_token),
                format_cents(safe_float(pos.get('target_price', 0.99))),
                hold_str,
                slp_str,
                type_str,
                f"[{unreal_color}]${unreal:+.2f}[/{unreal_color}]"
            )

    title_str = "Active Positions [P or H to Minimize]" if fullscreen else "Active Positions [P to Fullscreen]"
    return Panel(table, title=f"[bold {COLOR_LABEL}]{title_str}[/bold {COLOR_LABEL}]", box=ROUNDED, border_style=COLOR_BORDER)


def build_closed_positions_panel(num_lines: int = 15) -> Panel:
    """Build the closed trade history table with full timestamps and exit reasons."""
    table = Table(box=ROUNDED, expand=True, padding=(0, 1))
    table.add_column("Closed Time (SAST)", justify="center", header_style=COLOR_LABEL, style=COLOR_ASSET)
    table.add_column("Asset", header_style=f"bold {COLOR_LABEL}", style=f"bold {COLOR_ASSET}")
    table.add_column("TF", justify="center", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Dir", justify="center", header_style=COLOR_LABEL)
    table.add_column("Size", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Entry Token", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Exit Token", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("Hold", justify="right", header_style=COLOR_LABEL, style=COLOR_LABEL)
    table.add_column("SLP", justify="right", header_style=COLOR_LABEL)
    table.add_column("Type", justify="center", header_style=COLOR_LABEL)
    table.add_column("Exit Reason", justify="left", header_style=COLOR_LABEL)
    table.add_column("PnL ($)", justify="right", header_style=COLOR_LABEL)

    with g_state.lock:
        closed_positions = list(g_state.positions_state.get("closed", []))
        offset = g_state.closed_scroll_offset = min(g_state.closed_scroll_offset, max(0, len(closed_positions) - 1))
        fullscreen = g_state.fullscreen_mode == 'closed'

    # Display sliced closed trades based on scroll offset
    visible_positions = closed_positions[offset : offset + num_lines]
    for pos in visible_positions:
        title = pos.get("event_title", "Unknown")
        
        # Asset parse
        asset = "UNKNOWN"
        for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "HYPE", "LINK"]:
            if f"[{possible}]" in title.upper() or possible in title.upper():
                asset = possible
                break
        
        # Timeframe parse
        tf = "5m"
        if "15M" in title.upper():
            tf = "15m"
        elif "1H" in title.upper():
            tf = "1h"
        elif "5M" in title.upper():
            tf = "5m"
        
        direction = pos.get("direction", "YES")
        dir_color = COLOR_PASTEL_GREEN if direction in ("YES", "UP") else COLOR_PASTEL_RED
        
        # Format values
        size = safe_float(pos.get("size", 0.0))
        entry = safe_float(pos.get("entry_price", pos.get("entry_token_price", 0.0)))
        exit_pr = safe_float(pos.get("exit_price", pos.get("exit_token_price", 0.0)))
        hold_hours = safe_float(pos.get("hold_hours", 0.0))
        hold_sec = int(hold_hours * 3600)
        hold_str = f"{hold_sec // 60}m {hold_sec % 60}s"
        pnl = safe_float(pos.get("realized_pnl", 0.0))
        pnl_color = COLOR_PASTEL_GREEN if pnl > 0.01 else (COLOR_PASTEL_RED if pnl < -0.01 else COLOR_LABEL)
        
        formatted_exit_ts = format_iso_timestamp(pos.get("exit_time", ""))
        
        # Format exit reason styles conditionally
        raw_reason = str(pos.get("exit_reason", "RESOLVED")).upper()
        if -0.009 <= pnl <= 0.009:
            reason_str = f"[{COLOR_LABEL}]BREAK EVEN[/{COLOR_LABEL}]"
        elif "EXPIRED" in raw_reason or "MARKET EXPIRED" in raw_reason:
            if pnl > 0.009:
                reason_str = f"[bold {COLOR_PASTEL_GREEN}]WIN, MARKET EXPIRED[/bold {COLOR_PASTEL_GREEN}]"
            else:
                reason_str = f"[bold {COLOR_PASTEL_RED}]LOSS, MARKET EXPIRED[/bold {COLOR_PASTEL_RED}]"
        elif "TARGET" in raw_reason:
            reason_str = f"[{COLOR_PASTEL_GREEN}]TARGET[/{COLOR_PASTEL_GREEN}]"
        elif "STOP" in raw_reason or "LOSS" in raw_reason or "FAIL" in raw_reason:
            reason_str = f"[{COLOR_PASTEL_RED}]LOSS[/{COLOR_PASTEL_RED}]"
        else:
            reason_str = f"[{COLOR_LABEL}]{raw_reason}[/{COLOR_LABEL}]"

        tranche_type = str(pos.get("tranche", "")).upper()
        entry_type = str(pos.get("entry_type", "")).upper()
        event_title = str(pos.get("event_title", "")).upper()

        if "LS" in entry_type or "LS" in tranche_type or "SNIPE" in entry_type or "SNIPE" in event_title:
            type_str = f"[bold {COLOR_LS}]LS[/bold {COLOR_LS}]"
        elif tranche_type == "A" or "HALF" in raw_reason or "TRANCHE_A" in raw_reason or "ES" in raw_reason or "ES" in entry_type:
            type_str = f"[bold {COLOR_ES}]ES[/bold {COLOR_ES}]"
        elif tranche_type == "B" or "RUNNER" in raw_reason or "TRANCHE_B" in raw_reason or "RS" in raw_reason or "EX" in raw_reason or "EX" in entry_type:
            type_str = f"[bold {COLOR_EX}]EX[/bold {COLOR_EX}]"
        else:
            type_str = f"[grey50]ES[/grey50]"

        slp_val = safe_float(pos.get("slp", 0.0))
        if abs(slp_val) < 0.01:
            slp_str = "[grey50]0.0¢[/grey50]"
        else:
            slp_color = COLOR_PASTEL_RED if slp_val > 0.01 else COLOR_PASTEL_GREEN
            slp_str = f"[{slp_color}]{slp_val:+.1f}¢[/{slp_color}]"

        table.add_row(
            formatted_exit_ts,
            asset,
            tf,
            f"[{dir_color}]{direction}[/{dir_color}]",
            f"${size:,.2f}",
            format_cents(entry),
            format_cents(exit_pr),
            hold_str,
            slp_str,
            type_str,
            reason_str,
            f"[{pnl_color}]${pnl:+.2f}[/{pnl_color}]"
        )

    if not closed_positions:
        table.add_row("-", "-", "-", "-", "-", "-", "-", "-", "-", "No trades closed yet.", "-", "-")

    key_guide = "T or H to Minimize" if fullscreen else "T to Fullscreen"
    title_str = f"Trade History [Scroll: -{offset}] ({key_guide}, Up/Down Arrow to Scroll, U to Reset)" if offset > 0 else f"Trade History ({key_guide}, Up/Down Arrow to Scroll, U to Reset)"
    return Panel(table, title=f"[bold {COLOR_LABEL}]{title_str}[/bold {COLOR_LABEL}]", box=ROUNDED, border_style=COLOR_BORDER)


def build_logs_panel(num_lines: int = 8) -> Panel:
    """Build the scrolling log viewer with keyboard controls."""
    with g_state.lock:
        offset = g_state.logs_scroll_offset
        fullscreen = g_state.fullscreen_mode == 'logs'

    log_lines = tail_log_file(LOG_FILE, num_lines=num_lines, offset=offset)
    log_text = Text()
    for idx, line in enumerate(log_lines):
        if idx > 0:
            log_text.append("\n")
        log_text.append(colorize_log_line(line))
        
    key_guide = "L or H to Minimize" if fullscreen else "L to Fullscreen"
    title_str = f"Live Engine Logs [Scroll: -{offset}] ({key_guide}, W/S to Scroll, U to Reset)" if offset > 0 else f"Live Engine Logs ({key_guide}, W/S to Scroll, U to Reset)"
    return Panel(
        log_text,
        title=f"[bold {COLOR_LABEL}]{title_str}[/bold {COLOR_LABEL}]",
        box=ROUNDED,
        border_style=COLOR_BORDER
    )


def run_keyboard_listener():
    """Background listener to process non-blocking keyboard controls for terminal scrollback."""
    if termios is None or tty is None or select is None:
        return
    try:
        fd = sys.stdin.fileno()
        if not os.isatty(fd):
            return
        old_settings = termios.tcgetattr(fd)
    except Exception:
        return
    try:
        tty.setcbreak(fd)
        while True:
            rlist, _, _ = select.select([sys.stdin], [], [], 0.2)
            if rlist:
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # Escape sequences (arrows)
                    rlist2, _, _ = select.select([sys.stdin], [], [], 0.25)
                    if rlist2:
                        extra = sys.stdin.read(2)
                        if extra == '[A':  # Up Arrow -> Scroll Closed positions back (older)
                            with g_state.lock:
                                g_state.closed_scroll_offset += 1
                        elif extra == '[B':  # Down Arrow -> Scroll Closed positions forward (newer)
                            with g_state.lock:
                                g_state.closed_scroll_offset = max(0, g_state.closed_scroll_offset - 1)
                elif ch.lower() == 'w':  # Scroll logs UP (older)
                    with g_state.lock:
                        g_state.logs_scroll_offset += 1
                elif ch.lower() == 's':  # Scroll logs DOWN (newer)
                    with g_state.lock:
                        g_state.logs_scroll_offset = max(0, g_state.logs_scroll_offset - 1)
                elif ch.lower() == 'k':  # Scroll metrics UP (older)
                    with g_state.lock:
                        g_state.metrics_scroll_offset += 1
                elif ch.lower() == 'j':  # Scroll metrics DOWN (newer)
                    with g_state.lock:
                        g_state.metrics_scroll_offset = max(0, g_state.metrics_scroll_offset - 1)
                elif ch.lower() == 'u':  # Reset offsets to live real-time view
                    with g_state.lock:
                        g_state.closed_scroll_offset = 0
                        g_state.logs_scroll_offset = 0
                        g_state.metrics_scroll_offset = 0
                elif ch.lower() == 'l':  # Toggle logs fullscreen
                    with g_state.lock:
                        g_state.fullscreen_mode = 'logs' if g_state.fullscreen_mode != 'logs' else None
                elif ch.lower() == 't':  # Toggle trade history fullscreen
                    with g_state.lock:
                        g_state.fullscreen_mode = 'closed' if g_state.fullscreen_mode != 'closed' else None
                elif ch.lower() == 'p':  # Toggle active positions fullscreen
                    with g_state.lock:
                        g_state.fullscreen_mode = 'active' if g_state.fullscreen_mode != 'active' else None
                elif ch.lower() == 'r':  # Toggle regime/analytics fullscreen
                    with g_state.lock:
                        g_state.fullscreen_mode = 'regime' if g_state.fullscreen_mode != 'regime' else None
                elif ch.lower() == 'm':  # Toggle metrics fullscreen
                    with g_state.lock:
                        g_state.fullscreen_mode = 'metrics' if g_state.fullscreen_mode != 'metrics' else None
                elif ch.lower() == 'h':  # Reset to default layout
                    with g_state.lock:
                        g_state.fullscreen_mode = None
                        g_state.metrics_scroll_offset = 0
                
                # Instantly notify main loop to wake up and redraw
                g_state.redraw_event.set()
    except Exception:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def make_layout() -> Layout:
    """Create screen layout utilizing integers to prevent Python 3.14 TypeError."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="upper_body", size=22),
        Layout(name="active_panel", size=7),
        Layout(name="closed_panel", ratio=1),
        Layout(name="logs_panel", size=10)
    )
    
    layout["upper_body"].split_row(
        Layout(name="metrics", ratio=1),
        Layout(name="prices", ratio=1)
    )
    
    return layout


def main():
    """Main rendering loop optimized for high-refresh with throttled disk I/O."""
    console.clear()
    console.set_window_title("ZiSi-v2 Terminal Dashboard")
    
    # Start keyboard listener thread
    keyboard_thread = threading.Thread(target=run_keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    # Load initial states
    sync_file_states()
    
    last_file_sync = time.time()
    
    # Create the layouts
    layout_default = make_layout()
    
    layout_logs = Layout()
    layout_logs.split_column(
        Layout(name="header", size=3),
        Layout(name="logs_panel", ratio=1)
    )
    
    layout_closed = Layout()
    layout_closed.split_column(
        Layout(name="header", size=3),
        Layout(name="closed_panel", ratio=1)
    )
    
    layout_active = Layout()
    layout_active.split_column(
        Layout(name="header", size=3),
        Layout(name="active_panel", ratio=1)
    )
    
    layout_regime = Layout()
    layout_regime.split_column(
        Layout(name="header", size=3),
        Layout(name="regime_panel", ratio=1)
    )

    layout_metrics = Layout()
    layout_metrics.split_column(
        Layout(name="header", size=3),
        Layout(name="metrics_panel", ratio=1)
    )
    
    # 10Hz fluid rendering loop (10 updates per second) for zero-latency keyboard input and instant rendering
    with Live(layout_default, refresh_per_second=10, screen=True) as live:
        last_fs_mode = None
        while True:
            now = time.time()
            
            # Sync local file states at 10Hz (fluid rendering speed) to ensure real-time oracle price updates
            if now - last_file_sync >= 0.10:
                sync_file_states()
                last_file_sync = now
                
            with g_state.lock:
                fs_mode = g_state.fullscreen_mode
                
            if fs_mode != last_fs_mode:
                live.console.clear()
                last_fs_mode = fs_mode
                
            # Render based on fullscreen mode
            if fs_mode == 'logs':
                layout_logs["header"].update(build_header_panel())
                layout_logs["logs_panel"].update(build_logs_panel(num_lines=max(5, live.console.height - 6)))
                live.update(layout_logs)
            elif fs_mode == 'closed':
                layout_closed["header"].update(build_header_panel())
                layout_closed["closed_panel"].update(build_closed_positions_panel(num_lines=max(5, live.console.height - 8)))
                live.update(layout_closed)
            elif fs_mode == 'active':
                layout_active["header"].update(build_header_panel())
                layout_active["active_panel"].update(build_active_positions_panel())
                live.update(layout_active)
            elif fs_mode == 'regime':
                layout_regime["header"].update(build_header_panel())
                layout_regime["regime_panel"].update(build_regime_panel(fullscreen=True))
                live.update(layout_regime)
            elif fs_mode == 'metrics':
                layout_metrics["header"].update(build_header_panel())
                layout_metrics["metrics_panel"].update(build_metrics_panel(fullscreen=True))
                live.update(layout_metrics)
            else:
                # Default layout
                # Dynamically resize default layout panels based on terminal window height to prevent overflow glitches
                h = live.console.height or 40
                if h < 45:
                    layout_default["header"].size = 3
                    layout_default["upper_body"].size = 12
                    layout_default["active_panel"].size = 4
                    layout_default["logs_panel"].size = 6
                    closed_lines = max(2, h - 3 - 12 - 4 - 6 - 4)  # dynamic allocation
                else:
                    layout_default["header"].size = 3
                    layout_default["upper_body"].size = 17
                    layout_default["active_panel"].size = 7
                    layout_default["logs_panel"].size = 10
                    closed_lines = 15

                layout_default["header"].update(build_header_panel())
                layout_default["metrics"].update(build_metrics_panel())
                layout_default["prices"].update(build_spot_prices_panel())
                layout_default["active_panel"].update(build_active_positions_panel())
                layout_default["closed_panel"].update(build_closed_positions_panel(num_lines=closed_lines))
                # Adjust logs height dynamically too
                log_lines = max(3, layout_default["logs_panel"].size - 2)
                layout_default["logs_panel"].update(build_logs_panel(num_lines=log_lines))
                live.update(layout_default)
            
            # Write a heartbeat file to confirm the process loop is running without freezing
            try:
                with open("/tmp/zisi_dash_tick.log", "w") as tf:
                    tf.write(f"HEARTBEAT: {datetime.now().isoformat()}\n")
            except Exception:
                pass
                
            # Sleep for up to 0.10s, but wake up instantly if a redraw is triggered (zero-latency keyboard input)
            g_state.redraw_event.wait(timeout=0.10)
            g_state.redraw_event.clear()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        console.print("[bold yellow]ZiSi-v2 terminal dashboard stopped.[/bold yellow]")
        sys.exit(0)
