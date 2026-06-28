#!/usr/bin/env python3
"""
zisi_terminal.py — Rich Terminal Dashboard for ZiSi-v2.
Features live-updating WebSockets for Binance Spot and Polymarket CLOB feeds,
displays live Chainlink and Pyth oracle prices, calculates real-time unrealized P&L,
and provides a clean, premium "Titanium Gray" design.
"""

import os
import sys
import json
import time
import asyncio
import threading
from datetime import datetime, timezone
from pathlib import Path

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

# Resolve paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

STATE_FILE = DATA_DIR / "account_state.json"
POSITIONS_FILE = DATA_DIR / "positions_state.json"
REGIME_FILE = DATA_DIR / "regime_status.json"
SENTIMENT_FILE = DATA_DIR / "sentiment_state.json"
CHAINLINK_FILE = DATA_DIR / "chainlink_prices.json"
PYTH_FILE = DATA_DIR / "pyth_prices.json"

PM2_LOG_PATH = Path("/root/.pm2/logs/ZiSi-Core-Engine-out.log")
LOCAL_LOG_PATH = PROJECT_ROOT / "zisi_bot_console.log"
LOG_FILE = PM2_LOG_PATH if PM2_LOG_PATH.exists() else LOCAL_LOG_PATH


# Global state thread-safe container
class GlobalDashboardState:
    def __init__(self):
        self.lock = threading.Lock()
        # Live WebSocket data
        self.spot_prices = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0, "XRP": 0.0}
        self.clob_prices = {}  # market_id -> {"yes_price": float, "last_update": float}
        self.clob_spreads = {}  # market_id -> float
        
        # File-based state
        self.account_state = {}
        self.positions_state = {}
        self.regime_state = {}
        self.sentiment_state = {}
        self.chainlink_prices = {}
        self.pyth_prices = {}
        
        # Timing
        self.start_time = time.time()
        self.active_market_ids = set()


g_state = GlobalDashboardState()


def get_uptime_str(start_time: float) -> str:
    """Format duration into a readable uptime string."""
    diff = int(time.time() - start_time)
    days, remain = divmod(diff, 86400)
    hours, remain = divmod(remain, 3600)
    minutes, seconds = divmod(remain, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# ── WebSocket Listeners ────────────────────────────────────────────────────────

async def binance_spot_listener():
    """Connect to Binance Spot WebSocket for sub-second price updates."""
    url = "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker/xrpusdt@ticker"
    while True:
        try:
            async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    symbol = data.get("s", "")
                    price = float(data.get("c", 0.0))
                    
                    asset = symbol.replace("USDT", "")
                    if asset in g_state.spot_prices:
                        with g_state.lock:
                            g_state.spot_prices[asset] = price
        except Exception:
            await asyncio.sleep(2)  # Reconnect


async def polymarket_clob_listener():
    """Connect to Polymarket CLOB WebSocket to stream order book midpoints for active markets."""
    url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    while True:
        try:
            async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                subscribed_markets = set()
                
                while True:
                    with g_state.lock:
                        current_active_markets = set(g_state.active_market_ids)
                    
                    # Unsubscribe from old
                    to_unsub = subscribed_markets - current_active_markets
                    if to_unsub:
                        unsub_msg = {"type": "unsubscribe", "market_ids": list(to_unsub), "channel": "book"}
                        await ws.send(json.dumps(unsub_msg))
                        subscribed_markets -= to_unsub
                    
                    # Subscribe to new
                    to_sub = current_active_markets - subscribed_markets
                    if to_sub:
                        sub_msg = {"type": "subscribe", "market_ids": list(to_sub), "channel": "book"}
                        await ws.send(json.dumps(sub_msg))
                        subscribed_markets.update(to_sub)
                    
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        if data.get("event_type") == "book":
                            m_id = data.get("market_id")
                            bids = data.get("bids", [])
                            asks = data.get("asks", [])
                            if bids and asks:
                                best_bid = float(bids[0].get("price", 0.0))
                                best_ask = float(asks[0].get("price", 0.0))
                                midpoint = (best_bid + best_ask) / 2
                                spread = best_ask - best_bid
                                with g_state.lock:
                                    g_state.clob_prices[m_id] = {
                                        "yes_price": midpoint,
                                        "last_update": time.time()
                                    }
                                    g_state.clob_spreads[m_id] = spread
                    except asyncio.TimeoutError:
                        pass
        except Exception:
            await asyncio.sleep(2)  # Reconnect


def run_ws_event_loop():
    """Background thread worker to run the async listeners."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(binance_spot_listener())
    loop.create_task(polymarket_clob_listener())
    loop.run_forever()


# Start WebSocket threads
ws_thread = threading.Thread(target=run_ws_event_loop, daemon=True)
ws_thread.start()


# ── File Loading & State Processing ───────────────────────────────────────────

def load_json_file(file_path: Path) -> dict:
    """Safely load JSON to avoid race conditions with bot processes."""
    if not file_path.exists():
        return {}
    for _ in range(3):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            time.sleep(0.05)
    return {}


def sync_file_states():
    """Load latest states from local files into global state."""
    account = load_json_file(STATE_FILE)
    positions = load_json_file(POSITIONS_FILE)
    regime = load_json_file(REGIME_FILE)
    sentiment = load_json_file(SENTIMENT_FILE)
    chainlink = load_json_file(CHAINLINK_FILE)
    pyth = load_json_file(PYTH_FILE)

    with g_state.lock:
        g_state.account_state = account
        g_state.positions_state = positions
        g_state.regime_state = regime
        g_state.sentiment_state = sentiment
        g_state.chainlink_prices = chainlink
        g_state.pyth_prices = pyth
        
        # Update list of active market IDs to track on CLOB WS
        active_list = positions.get("active", [])
        g_state.active_market_ids = {pos["market_id"] for pos in active_list if pos.get("market_id")}


def tail_log_file(file_path: Path, num_lines: int = 10) -> list[str]:
    """Tail the log file safely."""
    if not file_path.exists():
        return ["[grey50]Waiting for log file to generate...[/grey50]"]
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            buffer_size = 4096
            if file_size > 0:
                seek_offset = min(file_size, buffer_size)
                f.seek(file_size - seek_offset)
                chunk = f.read(seek_offset)
                lines = chunk.splitlines()
                if len(lines) < num_lines:
                    f.seek(0)
                    lines = f.read().splitlines()
                return lines[-num_lines:]
            return []
    except Exception as e:
        return [f"[red]Error reading logs: {e}[/red]"]


def colorize_log_line(line: str) -> Text:
    """Apply visual hierarchy to logs using Titanium Gray as the default base."""
    clean_line = line.strip()
    text = Text(clean_line)
    lower_line = clean_line.lower()
    
    if "error" in lower_line or "exception" in lower_line or "fail" in lower_line:
        text.stylize("red bold")
    elif "warning" in lower_line or "paused" in lower_line:
        text.stylize("bright_yellow")
    elif "win" in lower_line or "profit" in lower_line:
        text.stylize("green bold")
    elif "loss" in lower_line or "drawdown" in lower_line:
        text.stylize("magenta bold")
    elif "skip" in lower_line or "veto" in lower_line:
        text.stylize("bright_black")
    elif "signal" in lower_line or "snipe" in lower_line:
        text.stylize("cyan")
    elif "order" in lower_line or "fill" in lower_line:
        text.stylize("green")
    else:
        text.stylize("grey70")  # Titanium Gray default
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


# ── Render Panels ─────────────────────────────────────────────────────────────

def build_header_panel() -> Panel:
    """Build system status clocks and candle close countdowns."""
    now = time.time()
    now_utc = datetime.now(timezone.utc)
    
    # SAST Clock
    sast_hour = (now_utc.hour + 2) % 24
    sast_str = f"{sast_hour:02d}:{now_utc.minute:02d}:{now_utc.second:02d} SAST"
    utc_str = now_utc.strftime("%H:%M:%S UTC")

    # Countdown calculations
    sec_5m = 300 - (int(now) % 300)
    sec_15m = 900 - (int(now) % 900)
    
    cd_5m_str = f"{sec_5m // 60:02d}:{sec_5m % 60:02d}"
    cd_15m_str = f"{sec_15m // 60:02d}:{sec_15m % 60:02d}"
    
    style_5m = "blink red bold" if sec_5m < 30 else "green bold"
    style_15m = "blink red bold" if sec_15m < 60 else "green bold"

    # Uptime
    uptime = get_uptime_str(g_state.start_time)
    
    # Log liveness
    liveness_status = "[red]OFFLINE[/red]"
    if LOG_FILE.exists():
        mtime = os.path.getmtime(LOG_FILE)
        if now - mtime < 60:
            liveness_status = "[blink green]● ACTIVE[/blink green]"
        else:
            liveness_status = "[yellow]● STANDBY[/yellow]"

    header_text = Text.assemble(
        ("ZiSi-v2 Terminal ", "bold cyan"),
        ("│ ", "bright_black"),
        ("Status: ", "bold grey70"),
        Text.from_markup(liveness_status),
        (" │ ", "bright_black"),
        ("UTC: ", "bold grey70"),
        (utc_str, "magenta"),
        (" │ ", "bright_black"),
        ("SAST: ", "bold grey70"),
        (sast_str, "yellow"),
        (" │ ", "bright_black"),
        ("5m Candle: ", "bold grey70"),
        (cd_5m_str, style_5m),
        (" │ ", "bright_black"),
        ("15m Candle: ", "bold grey70"),
        (cd_15m_str, style_15m),
        (" │ ", "bright_black"),
        ("Uptime: ", "bold grey70"),
        (uptime, "green")
    )
    
    return Panel(Align.center(header_text), box=ROUNDED, style="bright_black")


def build_metrics_panel() -> Panel:
    """Build performance summary showing real-time fluctuating unrealized stats."""
    with g_state.lock:
        start_bal = float(g_state.account_state.get("starting_balance", 50.00))
        current_bal = float(g_state.account_state.get("balance", start_bal))
        summary = g_state.positions_state.get("summary", {})
        active_positions = g_state.positions_state.get("active", [])

    realized = float(summary.get("realized_pnl", 0.0))
    
    # Calculate live unrealized PnL from real-time WebSocket feeds
    total_live_unrealized = 0.0
    for pos in active_positions:
        market_id = pos.get("market_id")
        shares = float(pos.get("shares", 0.0))
        size = float(pos.get("size", 0.0))
        direction = pos.get("direction", "YES")
        
        live_entry = g_state.clob_prices.get(market_id)
        if live_entry and shares > 0:
            yes_price = live_entry["yes_price"]
            live_price = yes_price if direction == "YES" else (1.0 - yes_price)
            unreal = (shares * live_price) - size
            total_live_unrealized += unreal
        else:
            total_live_unrealized += float(pos.get("unrealized_pnl", 0.0))

    live_balance = current_bal + total_live_unrealized
    net_pnl = live_balance - start_bal
    roi = (net_pnl / start_bal) * 100 if start_bal > 0 else 0.0

    wins = int(summary.get("win_count", 0))
    losses = int(summary.get("loss_count", 0))
    total_closed = wins + losses
    win_rate = (wins / total_closed) * 100 if total_closed > 0 else 0.0

    pnl_color = "green" if net_pnl > 0.01 else ("red" if net_pnl < -0.01 else "grey70")
    real_color = "green" if realized > 0.01 else ("red" if realized < -0.01 else "grey70")
    unreal_color = "green" if total_live_unrealized > 0.01 else ("red" if total_live_unrealized < -0.01 else "grey70")

    metrics_table = Table.grid(expand=True, padding=(0, 1))
    metrics_table.add_column("Metric", style="bold grey70", width=16)
    metrics_table.add_column("Value", justify="right", style="grey85")

    metrics_table.add_row("Start Capital:", f"${start_bal:,.2f} USDC")
    metrics_table.add_row("Live Capital:", f"${live_balance:,.2f} USDC")
    metrics_table.add_row("Session Net PnL:", f"[{pnl_color}]${net_pnl:+,.2f} ({roi:+.2f}%)[/{pnl_color}]")
    metrics_table.add_row("Realized P&L:", f"[{real_color}]${realized:+,.2f}[/{real_color}]")
    metrics_table.add_row("Live Unrealized:", f"[{unreal_color}]${total_live_unrealized:+,.2f}[/{unreal_color}]")
    metrics_table.add_row("Total Trades:", f"[green]{wins}W[/green] / [red]{losses}L[/red] ({win_rate:.1f}% WR)")

    # Render Win Rate Progress Bar
    bar_len = int(win_rate / 10)
    bar_str = "█" * bar_len + "░" * (10 - bar_len)
    metrics_table.add_row("Win Rate Bar:", f"[cyan][{bar_str}][/cyan]")

    return Panel(metrics_table, title="[bold white]Performance Summary[/bold white]", box=ROUNDED, border_style="grey37")


def build_spot_prices_panel() -> Panel:
    """Build pricing layout displaying spot, Pyth, and Chainlink prices alongside token spreads."""
    table = Table(box=ROUNDED, expand=True, padding=(0, 1))
    table.add_column("Asset", style="bold cyan")
    table.add_column("Binance Spot", justify="right", style="grey85")
    table.add_column("Pyth Oracle", justify="right", style="grey85")
    table.add_column("Chainlink Spot", justify="right", style="grey85")
    table.add_column("YES price", justify="right", style="grey85")
    table.add_column("Spread", justify="right", style="grey85")

    with g_state.lock:
        spot_copy = dict(g_state.spot_prices)
        cl_copy = dict(g_state.chainlink_prices)
        pyth_copy = dict(g_state.pyth_prices)
        positions = list(g_state.positions_state.get("active", []))

    # Compile table rows
    for asset in ["BTC", "ETH", "SOL", "XRP"]:
        spot_price = spot_copy.get(asset, 0.0)
        spot_str = f"${spot_price:,.2f}" if spot_price > 0 else "CONNECTING..."
        
        # Load values from local oracle dumps
        cl_price = float(cl_copy.get(asset, 0.0))
        cl_str = f"${cl_price:,.2f}" if cl_price > 0 else "-"
        
        pyth_price = float(pyth_copy.get(asset, 0.0))
        pyth_str = f"${pyth_price:,.2f}" if pyth_price > 0 else "-"
        
        # Try to find an active trade matching this asset to get live contract spread
        token_price_str = "-"
        spread_str = "-"
        for pos in positions:
            title = pos.get("event_title", "")
            if f"[{asset}]" in title.upper() or asset in title.upper():
                m_id = pos.get("market_id")
                live_entry = g_state.clob_prices.get(m_id)
                spread = g_state.clob_spreads.get(m_id)
                if live_entry:
                    token_price_str = f"${live_entry['yes_price']:.3f}"
                else:
                    token_price_str = f"${pos.get('current_price', 0.0):.3f}"
                if spread is not None:
                    spread_str = f"{spread * 100:.1f}¢"
                break

        table.add_row(asset, spot_str, pyth_str, cl_str, token_price_str, spread_str)

    return Panel(table, title="[bold white]Spot & Oracle Price Matrix[/bold white]", box=ROUNDED, border_style="grey37")


def build_regime_panel() -> Panel:
    """Build the current regime classifications and indicators."""
    with g_state.lock:
        reg = dict(g_state.regime_state)
        sent = dict(g_state.sentiment_state)

    raw_reg = str(reg.get("regime", "UNKNOWN")).upper()
    atr_pct = float(reg.get("atr_percentile", 50.0))
    obi = float(reg.get("obi", 0.0))
    vol_ratio = float(reg.get("volume_ratio", 1.0))
    
    fng_val = int(sent.get("value", 50))
    fng_lbl = str(sent.get("label", "Neutral"))

    # Mapping styles
    regime_color = "white"
    if raw_reg == "TRENDING":
        regime_color = "green bold"
    elif raw_reg == "MEAN_REVERTING":
        regime_color = "yellow bold"
    elif raw_reg == "COMPRESSION":
        regime_color = "cyan bold"
    elif raw_reg == "VOLATILE_CHAOS":
        regime_color = "red bold"

    regime_table = Table.grid(expand=True, padding=(0, 1))
    regime_table.add_column("Metric", style="bold grey70", width=16)
    regime_table.add_column("Value", justify="right", style="grey85")

    regime_table.add_row("Market Regime:", f"[{regime_color}]{raw_reg}[/{regime_color}]")
    regime_table.add_row("ATR Percentile:", f"{atr_pct:.1f}%")
    regime_table.add_row("Order Imbalance:", f"{obi:+.2f}")
    regime_table.add_row("Volume Ratio:", f"{vol_ratio:.2f}x")
    regime_table.add_row("F&G Index:", f"{fng_val} ({fng_lbl})")

    # Size scale multiplier based on regime
    mult = 1.00
    if raw_reg == "TRENDING":
        mult = 1.30
    elif raw_reg == "COMPRESSION":
        mult = 1.10
    elif raw_reg == "MEAN_REVERTING":
        mult = 0.85
    elif raw_reg == "VOLATILE_CHAOS":
        mult = 0.30
    regime_table.add_row("Size Modifier:", f"{mult:.2f}x")

    return Panel(regime_table, title="[bold white]Market Regime & Analytics[/bold white]", box=ROUNDED, border_style="grey37")


def build_active_positions_panel() -> Panel:
    """Build the active open positions table with full attributes and live PnL."""
    table = Table(box=ROUNDED, expand=True, padding=(0, 1))
    table.add_column("Asset", style="bold cyan")
    table.add_column("Strategy", justify="center", style="grey85")
    table.add_column("Dir", justify="center")
    table.add_column("Size", justify="right", style="grey85")
    table.add_column("Entry Spot", justify="right", style="grey85")
    table.add_column("Mark Spot", justify="right", style="grey85")
    table.add_column("Entry Token", justify="right", style="grey85")
    table.add_column("Mark Token", justify="right", style="grey85")
    table.add_column("Entry Time (SAST)", justify="center", style="grey85")
    table.add_column("Hold", justify="right", style="grey85")
    table.add_column("Unrealized PnL", justify="right")

    with g_state.lock:
        active_positions = list(g_state.positions_state.get("active", []))
        spot_copy = dict(g_state.spot_prices)

    if not active_positions:
        table.add_row("-", "-", "-", "-", "-", "-", "-", "-", "No active positions running", "-", "-")
    else:
        for pos in active_positions:
            title = pos.get("event_title", "Unknown")
            market_id = pos.get("market_id")
            
            # Asset parse
            asset = "UNKNOWN"
            for possible in ["BTC", "ETH", "SOL", "XRP"]:
                if f"[{possible}]" in title.upper() or possible in title.upper():
                    asset = possible
                    break
            
            direction = pos.get("direction", "YES")
            dir_color = "green" if direction == "YES" else "red"
            size = float(pos.get("size", 0.0))
            
            # Fetch prices
            entry_token = float(pos.get("entry_price", 0.0))
            live_spot = spot_copy.get(asset, 0.0)
            
            # Fetch WebSocket token price
            live_entry = g_state.clob_prices.get(market_id)
            if live_entry:
                yes_price = live_entry["yes_price"]
                mark_token = yes_price if direction == "YES" else (1.0 - yes_price)
                unreal = (float(pos.get("shares", 0.0)) * mark_token) - size
            else:
                mark_token = float(pos.get("current_price", entry_token))
                unreal = float(pos.get("unrealized_pnl", 0.0))
            
            # Formulate spot entry estimations (if recorded inside calibration metrics, or blank)
            entry_spot_str = "-"
            mark_spot_str = f"${live_spot:,.2f}" if live_spot > 0 else "-"
            
            unreal_color = "green" if unreal > 0.01 else ("red" if unreal < -0.01 else "grey70")
            hold_min = float(pos.get("hold_minutes", 0.0))
            
            formatted_entry_ts = format_iso_timestamp(pos.get("entry_time", ""))

            table.add_row(
                asset,
                pos.get("entry_type", "SIG"),
                f"[{dir_color}]{direction}[/{dir_color}]",
                f"${size:,.2f}",
                entry_spot_str,
                mark_spot_str,
                f"${entry_token:.3f}",
                f"${mark_token:.3f}",
                formatted_entry_ts,
                f"{hold_min:.1f}m",
                f"[{unreal_color}]${unreal:+.2f}[/{unreal_color}]"
            )

    return Panel(table, title="[bold white]Active Open Positions[/bold white]", box=ROUNDED, border_style="grey37")


def build_closed_positions_panel() -> Panel:
    """Build the closed trade history table with full timestamps and exit reasons."""
    table = Table(box=ROUNDED, expand=True, padding=(0, 1))
    table.add_column("Closed Time (SAST)", justify="center", style="grey85")
    table.add_column("Asset", style="bold cyan")
    table.add_column("Strategy", justify="center", style="grey85")
    table.add_column("Dir", justify="center")
    table.add_column("Size", justify="right", style="grey85")
    table.add_column("Entry Token", justify="right", style="grey85")
    table.add_column("Exit Token", justify="right", style="grey85")
    table.add_column("Hold", justify="right", style="grey85")
    table.add_column("Exit Reason", justify="left", style="grey85")
    table.add_column("PnL ($)", justify="right")

    with g_state.lock:
        closed_positions = list(g_state.positions_state.get("closed", []))

    # Display last 5 closed trades
    for pos in closed_positions[:5]:
        title = pos.get("event_title", "Unknown")
        asset = "UNKNOWN"
        for possible in ["BTC", "ETH", "SOL", "XRP"]:
            if f"[{possible}]" in title.upper() or possible in title.upper():
                asset = possible
                break
        
        direction = pos.get("direction", "YES")
        dir_color = "green" if direction == "YES" else "red"
        
        size = float(pos.get("size", 0.0))
        entry = float(pos.get("entry_price", 0.0))
        exit_pr = float(pos.get("exit_price", 0.0))
        pnl = float(pos.get("realized_pnl", 0.0))
        pnl_color = "green" if pnl > 0.01 else ("red" if pnl < -0.01 else "grey70")
        hold_hours = float(pos.get("hold_hours", 0.0))
        
        formatted_exit_ts = format_iso_timestamp(pos.get("exit_time", ""))

        table.add_row(
            formatted_exit_ts,
            asset,
            pos.get("entry_type", "SIG"),
            f"[{dir_color}]{direction}[/{dir_color}]",
            f"${size:,.2f}",
            f"${entry:.3f}",
            f"${exit_pr:.3f}",
            f"{hold_hours * 60:.1f}m",
            pos.get("exit_reason", "RESOLVED"),
            f"[{pnl_color}]${pnl:+.2f}[/{pnl_color}]"
        )

    if not closed_positions:
        table.add_row("-", "-", "-", "-", "-", "-", "-", "-", "No trades closed yet.", "-")

    return Panel(table, title="[bold white]Recent Closed Trades (Trade History)[/bold white]", box=ROUNDED, border_style="grey37")


def build_logs_panel() -> Panel:
    """Build the scrolling log viewer."""
    log_lines = tail_log_file(LOG_FILE, num_lines=10)
    log_text = Text()
    for idx, line in enumerate(log_lines):
        if idx > 0:
            log_text.append("\n")
        log_text.append(colorize_log_line(line))
        
    return Panel(
        log_text,
        title=f"[bold white]Live Engine Logs ({LOG_FILE.name})[/bold white]",
        box=ROUNDED,
        border_style="grey37"
    )


def make_layout() -> Layout:
    """Create screen layout utilizing integers to prevent Python 3.14 TypeError."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="upper_body", size=8),
        Layout(name="active_panel", ratio=1),
        Layout(name="closed_panel", ratio=1),
        Layout(name="logs_panel", size=12)
    )
    
    layout["upper_body"].split_row(
        Layout(name="metrics", ratio=2),
        Layout(name="prices", ratio=3),
        Layout(name="regime", ratio=2)
    )
    
    return layout


def main():
    """Main dashboard rendering loop."""
    layout = make_layout()
    console.clear()
    console.set_window_title("ZiSi-v2 Terminal Dashboard")
    
    with Live(layout, refresh_per_second=2, screen=True) as live:
        while True:
            # Sync states from files
            sync_file_states()
            
            # Update layout pieces
            layout["header"].update(build_header_panel())
            layout["metrics"].update(build_metrics_panel())
            layout["prices"].update(build_spot_prices_panel())
            layout["regime"].update(build_regime_panel())
            layout["active_panel"].update(build_active_positions_panel())
            layout["closed_panel"].update(build_closed_positions_panel())
            layout["logs_panel"].update(build_logs_panel())
            
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        console.print("[bold yellow]ZiSi-v2 terminal dashboard stopped.[/bold yellow]")
        sys.exit(0)
