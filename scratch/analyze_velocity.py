import json
from datetime import datetime

json_path = r"c:\Users\mthun\Downloads\ZiSi-v2\backups\archive_session_best_3205usd_20260719_201044_positions_state.json"
account_path = r"c:\Users\mthun\Downloads\ZiSi-v2\backups\archive_session_best_3205usd_20260719_201044_account_state.json"

with open(json_path, 'r') as f:
    data = json.load(f)

closed = data.get("closed", [])

# Sort closed trades by exit_time / entry_time
closed_sorted = sorted(closed, key=lambda x: x.get('exit_time', x.get('entry_time', '')))

# Track compounding milestones
running_balance = 50.0
balance_curve = []
milestones = {100: None, 250: None, 500: None, 1000: None, 1500: None, 2000: None, 2500: None, 3000: None}

start_time_str = closed_sorted[0].get('entry_time') if closed_sorted else None
end_time_str = closed_sorted[-1].get('exit_time') if closed_sorted else None

start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00')) if start_time_str else None
end_dt = datetime.fromisoformat(end_time_str.replace('Z', '+00:00')) if end_time_str else None

peak_balance = 50.0
in_drawdown = False
dd_start_time = None
dd_max_depth = 0.0
recovery_times_min = []
drawdown_events = []

for idx, p in enumerate(closed_sorted):
    pnl = p.get('realized_pnl', 0.0)
    running_balance += pnl
    t_str = p.get('exit_time', p.get('entry_time'))
    t_dt = datetime.fromisoformat(t_str.replace('Z', '+00:00'))
    
    # Check milestones
    for m in milestones:
        if milestones[m] is None and running_balance >= m:
            elapsed_sec = (t_dt - start_dt).total_seconds() if start_dt else 0
            milestones[m] = {
                'time': t_str,
                'elapsed_min': elapsed_sec / 60.0,
                'elapsed_hours': elapsed_sec / 3600.0,
                'trade_index': idx + 1
            }

    # Drawdown & Recovery analysis
    if running_balance > peak_balance:
        if in_drawdown:
            # Recovered!
            rec_sec = (t_dt - dd_start_time).total_seconds()
            rec_min = rec_sec / 60.0
            recovery_times_min.append(rec_min)
            drawdown_events.append({
                'max_dd_dollars': dd_max_depth,
                'recovery_min': rec_min,
                'start_time': dd_start_time.isoformat(),
                'end_time': t_dt.isoformat()
            })
            in_drawdown = False
            dd_max_depth = 0.0
        peak_balance = running_balance
    else:
        dd = peak_balance - running_balance
        if dd > 0.01:
            if not in_drawdown:
                in_drawdown = True
                dd_start_time = t_dt
                dd_max_depth = dd
            else:
                if dd > dd_max_depth:
                    dd_max_depth = dd

print("==========================================================================")
print("             ZISI-V2 COMPOUNDING VELOCITY & LOSS RECOVERY AUDIT           ")
print("==========================================================================")
print(f"First Trade Entry:  {start_time_str}")
print(f"Last Trade Exit:   {end_time_str}")
if start_dt and end_dt:
    total_hours = (end_dt - start_dt).total_seconds() / 3600.0
    print(f"Total Session Duration: {total_hours:.2f} Hours ({total_hours/24.0:.2f} Days)")
print(f"Total Tranches Executed: {len(closed_sorted)}")
print(f"Final Account Balance:   ${running_balance:,.2f}")

print("\n--------------------------------------------------------------------------")
print("                     COMPOUNDING MILESTONES (VELOCITY)                    ")
print("--------------------------------------------------------------------------")
print(f"{'Milestone':<12} | {'Trades Executed':<16} | {'Elapsed Time (Hours)':<22} | {'Timestamp (UTC)'}")
print("-" * 75)
for m, info in milestones.items():
    if info:
        print(f"${m:<11} | Trade #{info['trade_index']:<13} | {info['elapsed_hours']:<20.2f} hrs | {info['time'][:19]}")
    else:
        print(f"${m:<11} | Not Reached")

print("\n--------------------------------------------------------------------------")
print("                   LOSS RECOVERY SPEED (DRAWDOWN ANALYSIS)                 ")
print("--------------------------------------------------------------------------")
print(f"Total Drawdown Recovery Events: {len(recovery_times_min)}")
if recovery_times_min:
    avg_rec = sum(recovery_times_min) / len(recovery_times_min)
    min_rec = min(recovery_times_min)
    max_rec = max(recovery_times_min)
    median_rec = sorted(recovery_times_min)[len(recovery_times_min)//2]
    print(f"Average Recovery Time:  {avg_rec:.2f} Minutes ({avg_rec*60:.0f} seconds)")
    print(f"Median Recovery Time:   {median_rec:.2f} Minutes")
    print(f"Fastest Recovery Time:  {min_rec:.2f} Minutes ({min_rec*60:.0f} seconds)")
    print(f"Slowest Recovery Time:  {max_rec:.2f} Minutes ({max_rec/60.0:.2f} hours)")

print("\nTop 5 Largest Drawdowns & Recovery Times:")
sorted_dd = sorted(drawdown_events, key=lambda x: x['max_dd_dollars'], reverse=True)[:5]
for idx, dd in enumerate(sorted_dd):
    print(f"  #{idx+1}: Drawdown: -${dd['max_dd_dollars']:.2f} | Recovered in: {dd['recovery_min']:.1f} Minutes ({dd['recovery_min']/60.0:.2f} hrs)")

print("==========================================================================")
