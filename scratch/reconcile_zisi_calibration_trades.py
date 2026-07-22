import glob
import json
import os
import re
from collections import defaultdict
from datetime import datetime

def main():
    pattern = "/root/ZiSi-v2/core/calibration_trades/*.jsonl"
    files = glob.glob(pattern)
    infra_pattern = "/root/ZiSi-v2/infrastructure/calibration_trades/*.jsonl"
    files.extend(glob.glob(infra_pattern))
    
    all_trades = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file_obj:
                for line in file_obj:
                    if line.strip():
                        t = json.loads(line.strip())
                        t["source_file"] = os.path.basename(f)
                        all_trades.append(t)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    total_t = len(all_trades)
    print(f"Loaded {total_t} total calibration trades from daily logs.")
    if not all_trades:
        return
        
    # Analyze the trades in depth
    wins = sum(1 for t in all_trades if t.get("result") == "WIN")
    losses = sum(1 for t in all_trades if t.get("result") == "LOSS")
    flats = sum(1 for t in all_trades if t.get("result") == "FLAT")
    win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0.0
    total_pnl = sum(float(t.get("pnl", 0.0)) for t in all_trades)
    
    print(f"\n==========================================")
    print(f"  ZCC ZISI BOT TOTAL HISTORY AUDIT ({total_t} TRADES)")
    print(f"==========================================")
    print(f"Total Trades: {total_t}")
    print(f"Wins: {wins} | Losses: {losses} | Flats: {flats}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Net PnL: ${total_pnl:,.2f} USDC")
    
    # 1. Strategy Breakdown
    print("\n1. Strategy Breakdown:")
    strat_groups = defaultdict(list)
    for t in all_trades:
        strat_groups[t.get("strategy", "UNKNOWN")].append(t)
    for strat, group in sorted(strat_groups.items(), key=lambda x: len(x[1]), reverse=True):
        s_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        s_wins = sum(1 for x in group if x.get("result") == "WIN")
        s_losses = sum(1 for x in group if x.get("result") == "LOSS")
        s_wr = (s_wins / (s_wins + s_losses)) * 100 if (s_wins + s_losses) > 0 else 0.0
        print(f"  {strat:15}: {len(group):4} trades | Win Rate: {s_wr:5.2f}% | PnL: ${s_pnl:9.2f}")
        
    # 2. Asset Breakdown (SIG Only)
    print("\n2. SIG Asset Breakdown:")
    sig_trades = strat_groups.get("SIG", [])
    asset_groups = defaultdict(list)
    for t in sig_trades:
        asset_groups[t.get("asset", "UNKNOWN").upper()].append(t)
    for asset, group in sorted(asset_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if x.get("result") == "WIN")
        a_losses = sum(1 for x in group if x.get("result") == "LOSS")
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        print(f"  {asset:7}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:9.2f}")
        
    # 3. Timeframe Breakdown (SIG Only)
    print("\n3. SIG Timeframe Breakdown:")
    tf_groups = defaultdict(list)
    for t in sig_trades:
        tf_groups[t.get("timeframe", "5m")].append(t)
    for tf, group in sorted(tf_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if x.get("result") == "WIN")
        a_losses = sum(1 for x in group if x.get("result") == "LOSS")
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        print(f"  {tf:7}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:9.2f}")
        
    # 4. Price Band Breakdown (SIG Only)
    print("\n4. SIG Entry Price Band Performance:")
    price_groups = defaultdict(list)
    for t in sig_trades:
        price = float(t.get("entry_price", 0.50))
        if price < 0.30:
            price_groups["< 30c (Low)        "].append(t)
        elif 0.30 <= price < 0.50:
            price_groups["30c - 50c (Mid-Low)"].append(t)
        elif 0.50 <= price < 0.70:
            price_groups["50c - 70c (Mid-High)"].append(t)
        elif 0.70 <= price < 0.85:
            price_groups["70c - 85c (High)   "].append(t)
        else:
            price_groups[">= 85c (Certainty) "].append(t)
            
    for band, group in sorted(price_groups.items()):
        a_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if x.get("result") == "WIN")
        a_losses = sum(1 for x in group if x.get("result") == "LOSS")
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        print(f"  {band}: {len(group):4} trades | Win Rate: {a_wr:5.2f}% | PnL: ${a_pnl:9.2f}")
        
    # 5. Exit Reasons (SIG Only)
    print("\n5. SIG Exit Reasons:")
    exit_groups = defaultdict(list)
    for t in sig_trades:
        exit_groups[t.get("exit_reason", "UNKNOWN")].append(t)
    for reason, group in sorted(exit_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {reason:25}: {len(group):4} trades")

    # Generate MD Report
    report_lines = [
        f"# 📊 ZCC ZISI Bot Complete Historical Audit Report",
        f"* **Source Logs:** Reconstructed from 24 daily jsonl files in `/root/ZiSi-v2/core/calibration_trades/` and `/root/ZiSi-v2/infrastructure/calibration_trades/`.",
        f"* **Total Trades Analyzed:** {total_t}",
        f"",
        f"## 🚀 1. Overall Performance Metrics",
        f"- **Total Closed Trades:** {total_t}",
        f"- **Wins / Losses / Flats:** {wins}W / {losses}L / {flats}F",
        f"- **Win Rate:** **{win_rate:.2f}%**",
        f"- **Total Net P&L:** **${total_pnl:,.2f} USDC**",
        f"",
        f"## ⚙️ 2. Strategy Breakdown",
        f"| Strategy | Trades | Wins | Losses | Flats | Win Rate | Net PnL |",
        f"|---|---|---|---|---|---|---|",
    ]
    for strat, group in sorted(strat_groups.items(), key=lambda x: len(x[1]), reverse=True):
        s_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        s_wins = sum(1 for x in group if x.get("result") == "WIN")
        s_losses = sum(1 for x in group if x.get("result") == "LOSS")
        s_flats = sum(1 for x in group if x.get("result") == "FLAT")
        s_wr = (s_wins / (s_wins + s_losses)) * 100 if (s_wins + s_losses) > 0 else 0.0
        report_lines.append(f"| **{strat}** | {len(group)} | {s_wins} | {s_losses} | {s_flats} | {s_wr:.2f}% | ${s_pnl:.2f} |")

    # Add SIG section
    sig_wr = (sum(1 for x in sig_trades if x.get("result") == "WIN") / 
              max(1, sum(1 for x in sig_trades if x.get("result") in ("WIN", "LOSS")))) * 100
    sig_pnl = sum(float(x.get("pnl", 0.0)) for x in sig_trades)
    
    report_lines.extend([
        f"",
        f"## 📈 3. ZCC ZISI Core SIG Strategy performance",
        f"*   **Total SIG Trades:** {len(sig_trades)}",
        f"*   **Win Rate:** **{sig_wr:.2f}%**",
        f"*   **Total Net PnL:** **${sig_pnl:,.2f} USDC**",
        f"",
        f"### SIG Asset Performance",
        f"| Asset | Trades | Wins | Losses | Win Rate | Net PnL |",
        f"|---|---|---|---|---|---|",
    ])
    for asset, group in sorted(asset_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if x.get("result") == "WIN")
        a_losses = sum(1 for x in group if x.get("result") == "LOSS")
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        report_lines.append(f"| **{asset}** | {len(group)} | {a_wins} | {a_losses} | {a_wr:.2f}% | ${a_pnl:.2f} |")

    report_lines.extend([
        f"",
        f"### SIG Timeframe Performance",
        f"| Timeframe | Trades | Wins | Losses | Win Rate | Net PnL |",
        f"|---|---|---|---|---|---|",
    ])
    for tf, group in sorted(tf_groups.items(), key=lambda x: len(x[1]), reverse=True):
        a_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if x.get("result") == "WIN")
        a_losses = sum(1 for x in group if x.get("result") == "LOSS")
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        report_lines.append(f"| **{tf}** | {len(group)} | {a_wins} | {a_losses} | {a_wr:.2f}% | ${a_pnl:.2f} |")

    report_lines.extend([
        f"",
        f"### SIG Entry Price Band Performance",
        f"| Price Band | Trades | Wins | Losses | Win Rate | Net PnL |",
        f"|---|---|---|---|---|---|",
    ])
    for band, group in sorted(price_groups.items()):
        a_pnl = sum(float(x.get("pnl", 0.0)) for x in group)
        a_wins = sum(1 for x in group if x.get("result") == "WIN")
        a_losses = sum(1 for x in group if x.get("result") == "LOSS")
        a_wr = (a_wins / (a_wins + a_losses)) * 100 if (a_wins + a_losses) > 0 else 0.0
        report_lines.append(f"| **{band.strip()}** | {len(group)} | {a_wins} | {a_losses} | {a_wr:.2f}% | ${a_pnl:.2f} |")

    report_lines.extend([
        f"",
        f"### SIG Exit Reason Analysis",
        f"| Exit Reason | Trades |",
        f"|---|---|",
    ])
    for reason, group in sorted(exit_groups.items(), key=lambda x: len(x[1]), reverse=True):
        report_lines.append(f"| {reason} | {len(group)} |")

    with open("/root/ZiSi-v2/wallet/wallet_reconciliation_total.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("\nSaved report to /root/ZiSi-v2/wallet/wallet_reconciliation_total.md")

if __name__ == '__main__':
    main()
