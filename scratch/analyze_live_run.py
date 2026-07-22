#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def parse_time(ts_str):
    if not ts_str:
        return None
    try:
        ts_str = ts_str.replace("Z", "").split("+")[0]
        if "T" in ts_str:
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%f")
        elif "-" in ts_str and ":" in ts_str:
            if "." in ts_str:
                return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
            else:
                return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return None

def analyze():
    project_root = Path("/root/ZiSi-v2")
    data_dir = project_root / "data"
    calib_dir = project_root / "core/calibration_trades"
    
    all_trades = []
    
    # 1. Parse positions_state.json closed trades
    pos_file = data_dir / "positions_state.json"
    if pos_file.exists():
        try:
            with open(pos_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_trades.extend(data.get("closed", []))
        except Exception as e:
            print(f"Error reading positions_state.json: {e}")
            
    # 2. Parse daily calibration trades jsonl files
    if calib_dir.exists():
        for f in sorted(calib_dir.glob("trades_*.jsonl")):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    for line in fh:
                        if line.strip():
                            all_trades.append(json.loads(line))
            except Exception as e:
                print(f"Error reading daily file {f.name}: {e}")

    # Dedup trades by order_id or unique timestamps
    seen_ids = set()
    unique_trades = []
    for t in all_trades:
        # Schema unified unique key
        ts_val = t.get("ts") or t.get("exit_time") or t.get("closed_time") or t.get("entry_time")
        pnl_val = t.get("pnl") if t.get("pnl") is not None else t.get("realized_pnl", 0.0)
        size_val = t.get("size") if t.get("size") is not None else t.get("shares", 0.0)
        
        oid = t.get("order_id") or f"{ts_val}_{size_val}_{pnl_val}"
        if oid not in seen_ids:
            seen_ids.add(oid)
            unique_trades.append(t)
            
    # Group trades by date ranges
    groups = {
        "Prime Session 1 (June 13-17)": [],
        "Gap Days (June 18-20)": [],
        "Prime Session 2 (June 21-23)": [],
        "Nonsense Session (June 24-July 10)": []
    }
    
    for t in unique_trades:
        exit_time_str = t.get("exit_time") or t.get("closed_time") or t.get("entry_time") or t.get("ts")
        dt = parse_time(exit_time_str)
        if not dt:
            continue
            
        date_str = dt.strftime("%Y-%m-%d")
        if "2026-06-13" <= date_str <= "2026-06-17":
            groups["Prime Session 1 (June 13-17)"].append(t)
        elif "2026-06-18" <= date_str <= "2026-06-20":
            groups["Gap Days (June 18-20)"].append(t)
        elif "2026-06-21" <= date_str <= "2026-06-23":
            groups["Prime Session 2 (June 21-23)"].append(t)
        elif date_str >= "2026-06-24":
            groups["Nonsense Session (June 24-July 10)"].append(t)

    report = []
    report.append("# 📊 ZiSi-v2 Deep Reconciliation Audit Report")
    report.append(f"Generated at: {datetime.now().isoformat()} UTC\n")

    for g_name, g_trades in groups.items():
        if not g_trades:
            report.append(f"## {g_name}\n*No trades found.*\n")
            continue
            
        wins = 0
        losses = 0
        flats = 0
        net_pnl = 0.0
        win_pnl = 0.0
        loss_pnl = 0.0
        
        entry_prices = []
        win_entry_prices = []
        loss_entry_prices = []
        
        price_bands = {"under_40c": 0, "40c_60c": 0, "60c_80c": 0, "above_80c": 0}
        assets = {}
        exit_reasons = {}
        
        for t in g_trades:
            pnl = float(t.get("pnl") if t.get("pnl") is not None else t.get("realized_pnl", 0.0))
            net_pnl += pnl
            
            entry_p = float(t.get("entry_price", 0.0))
            if entry_p > 0:
                entry_prices.append(entry_p)
                if entry_p < 0.40:
                    price_bands["under_40c"] += 1
                elif entry_p <= 0.60:
                    price_bands["40c_60c"] += 1
                elif entry_p <= 0.80:
                    price_bands["60c_80c"] += 1
                else:
                    price_bands["above_80c"] += 1
            
            # Outcome
            if pnl > 0.01:
                wins += 1
                win_pnl += pnl
                if entry_p > 0:
                    win_entry_prices.append(entry_p)
            elif pnl < -0.01:
                losses += 1
                loss_pnl += pnl
                if entry_p > 0:
                    loss_entry_prices.append(entry_p)
            else:
                flats += 1
                
            # Asset parse
            title = t.get("event_title", "")
            asset = "UNKNOWN"
            for possible in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:
                if f"[{possible}]" in title.upper() or possible in title.upper() or t.get("asset", "").upper() == possible:
                    asset = possible
                    break
            assets[asset] = assets.get(asset, {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0})
            assets[asset]["trades"] += 1
            if pnl > 0.01:
                assets[asset]["wins"] += 1
            elif pnl < -0.01:
                assets[asset]["losses"] += 1
            assets[asset]["pnl"] += pnl
            
            # Exit reason
            reason = t.get("exit_reason") or "UNKNOWN"
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
            
        total_closed = wins + losses
        win_rate = (wins / total_closed) * 100 if total_closed > 0 else 0.0
        avg_win = win_pnl / wins if wins > 0 else 0.0
        avg_loss = loss_pnl / losses if losses > 0 else 0.0
        avg_entry = sum(entry_prices) / len(entry_prices) if entry_prices else 0.0
        avg_win_entry = sum(win_entry_prices) / len(win_entry_prices) if win_entry_prices else 0.0
        avg_loss_entry = sum(loss_entry_prices) / len(loss_entry_prices) if loss_entry_prices else 0.0
        
        report.append(f"## {g_name}")
        report.append(f"* **Total Trades**: {len(g_trades)}")
        report.append(f"* **Wins / Losses / Flats**: {wins}W / {losses}L / {flats}F")
        report.append(f"* **Win Rate**: **{win_rate:.2f}%**")
        report.append(f"* **Net PnL**: **${net_pnl:+,.2f} USDC**")
        report.append(f"* **Average Win**: ${avg_win:.2f} | **Average Loss**: ${avg_loss:.2f}")
        report.append(f"* **Average Entry Price**: {avg_entry:.3f} (Wins: {avg_win_entry:.3f} | Losses: {avg_loss_entry:.3f})")
        report.append(f"* **Price Band Distribution**:")
        report.append(f"  * Under 40¢: {price_bands['under_40c']} trades")
        report.append(f"  * 40¢ - 60¢: {price_bands['40c_60c']} trades")
        report.append(f"  * 60¢ - 80¢: {price_bands['60c_80c']} trades")
        report.append(f"  * Above 80¢ (Poison): {price_bands['above_80c']} trades")
        
        report.append("\n### Asset Performance:")
        report.append("| Asset | Trades | Wins | Losses | Win Rate | Net PnL |")
        report.append("|---|---|---|---|---|---|")
        for asset, stats in sorted(assets.items(), key=lambda x: x[1]["pnl"], reverse=True):
            a_total = stats["wins"] + stats["losses"]
            a_wr = (stats["wins"] / a_total) * 100 if a_total > 0 else 0.0
            report.append(f"| **{asset}** | {stats['trades']} | {stats['wins']} | {stats['losses']} | {a_wr:.1f}% | ${stats['pnl']:+,.2f} USDC |")
            
        report.append("\n### Exit Reasons:")
        for r, count in sorted(exit_reasons.items(), key=lambda x: x[1], reverse=True):
            report.append(f"* **{r}**: {count} trades")
        report.append("\n" + "—"*40 + "\n")

    print("\n".join(report))

if __name__ == "__main__":
    analyze()
