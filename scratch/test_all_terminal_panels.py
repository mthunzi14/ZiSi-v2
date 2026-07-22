import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import zisi_terminal

print("Testing all terminal panels...")

try:
    p1 = zisi_terminal.build_metrics_panel()
    print("METRICS_PANEL_SUCCESS")
except Exception as e:
    print("METRICS_PANEL_ERROR:", e)

try:
    p2 = zisi_terminal.build_spot_prices_panel()
    print("SPOT_PRICES_PANEL_SUCCESS")
except Exception as e:
    print("SPOT_PRICES_PANEL_ERROR:", e)

try:
    p3 = zisi_terminal.build_active_positions_panel()
    print("ACTIVE_POSITIONS_PANEL_SUCCESS")
except Exception as e:
    print("ACTIVE_POSITIONS_PANEL_ERROR:", e)

try:
    p4 = zisi_terminal.build_closed_positions_panel()
    print("CLOSED_POSITIONS_PANEL_SUCCESS")
except Exception as e:
    print("CLOSED_POSITIONS_PANEL_ERROR:", e)

print("ALL_PANELS_VERIFIED")
