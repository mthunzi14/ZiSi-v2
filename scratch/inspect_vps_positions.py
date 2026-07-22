import subprocess
import json
import sys

cmd = [
    "ssh", "root@204.168.222.48",
    "python3 -c 'import json, os; p=\"/root/ZiSi-v2/data/positions_state.json\"; print(open(p).read() if os.path.exists(p) else \"{}\")'"
]

try:
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    closed = data.get("closed", [])
    print(f"Total closed: {len(closed)}")
    for i, pos in enumerate(closed):
        reason = str(pos.get("exit_reason", ""))
        pnl = float(pos.get("realized_pnl", pos.get("pnl", pos.get("profit", 0))) or 0)
        title = pos.get("event_title", "")
        direction = pos.get("direction", "")
        entry = pos.get("entry_price", 0)
        exit_p = pos.get("exit_price", 0)
        print(f"[{i+1:2d}] PnL: ${pnl:+.2f} | Dir: {direction:4s} | Entry: {entry:.3f} -> Exit: {exit_p:.3f} | Reason: {reason} | Title: {title}")
except Exception as e:
    print(f"Error: {e}")
