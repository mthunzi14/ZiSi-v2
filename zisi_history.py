#!/usr/bin/env python3
"""
zisi_history.py — Interactive complete trade history browser for ZiSi-v2.
Loads all closed positions and displays them in a scrollable, paginated Rich table.
"""

import json
import sys
from pathlib import Path

# Try importing rich. Exit gracefully if missing.
try:
    from rich.console import Console
    from rich.table import Table
    from rich.box import ROUNDED
except ImportError:
    print("Error: 'rich' library is required. Install it using: pip install rich")
    sys.exit(1)

def main():
    console = Console()
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    positions_file = data_dir / "positions_state.json"
    
    if not positions_file.exists():
        console.print("[red]Error: positions_state.json not found.[/red]")
        sys.exit(1)
        
    try:
        with open(positions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading file: {e}[/red]")
        sys.exit(1)
        
    closed = data.get("closed", [])
    if not closed:
        console.print("[yellow]No closed trades found in history.[/yellow]")
        sys.exit(0)
        
    table = Table(title="ZiSi-v2 Complete Trade History", box=ROUNDED, expand=True)
    table.add_column("Closed Time (UTC)", justify="center", style="grey70")
    table.add_column("Asset", style="bold light_steel_blue")
    table.add_column("TF", justify="center", style="grey70")
    table.add_column("Strategy", justify="center", style="grey70")
    table.add_column("Dir", justify="center")
    table.add_column("Size", justify="right", style="grey70")
    table.add_column("Entry Token", justify="right", style="grey70")
    table.add_column("Exit Token", justify="right", style="grey70")
    table.add_column("Hold", justify="right", style="grey70")
    table.add_column("Exit Reason", justify="left")
    table.add_column("PnL ($)", justify="right")
    
    for pos in closed:
        title = pos.get("event_title", "")
        asset = "UNKNOWN"
        for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:
            if f"[{possible}]" in title.upper() or possible in title.upper():
                asset = possible
                break
        tf = "5m"
        if "15M" in title.upper():
            tf = "15m"
        elif "1H" in title.upper():
            tf = "1h"
        elif "5M" in title.upper():
            tf = "5m"
            
        direction = pos.get("direction", "YES")
        dir_color = "green" if direction == "YES" else "red"
        pnl = float(pos.get("realized_pnl", 0.0))
        pnl_color = "green" if pnl > 0.01 else ("red" if pnl < -0.01 else "grey70")
        hold_hours = float(pos.get("hold_hours", 0.0))
        
        # Color exit reasons
        raw_reason = pos.get("exit_reason", "RESOLVED")
        if raw_reason == "MARKET_EXPIRED":
            reason_str = "[grey70]MARKET_EXPIRED[/grey70]"
        elif "TARGET" in raw_reason:
            reason_str = "[green]" + raw_reason + "[/green]"
        elif "STOP" in raw_reason or "FAIL" in raw_reason:
            reason_str = "[red]" + raw_reason + "[/red]"
        else:
            reason_str = f"[grey70]{raw_reason}[/grey70]"
            
        table.add_row(
            pos.get("exit_time", ""),
            asset,
            tf,
            pos.get("entry_type", "SIG"),
            f"[{dir_color}]{direction}[/{dir_color}]",
            f"${pos.get('size', 0.0):.2f}",
            f"${pos.get('entry_price', 0.0):.3f}",
            f"${pos.get('exit_price', 0.0):.3f}",
            f"{hold_hours * 60:.1f}m",
            reason_str,
            f"[{pnl_color}]${pnl:+.2f}[/{pnl_color}]"
        )
        
    with console.pager(styles=True):
        console.print(table)

if __name__ == "__main__":
    main()
