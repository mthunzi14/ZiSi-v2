import time
import sys
from pathlib import Path

# Add project root to sys.path to allow import
sys.path.append(str(Path(__file__).resolve().parent.parent))

import zisi_terminal

print("Initializing layout...")
layout = zisi_terminal.make_layout()

print("Testing sync_file_states...")
t0 = time.time()
zisi_terminal.sync_file_states()
print(f"sync_file_states took {time.time() - t0:.4f}s")

print("Testing build_header_panel...")
t0 = time.time()
zisi_terminal.build_header_panel()
print(f"build_header_panel took {time.time() - t0:.4f}s")

print("Testing build_metrics_panel...")
t0 = time.time()
zisi_terminal.build_metrics_panel()
print(f"build_metrics_panel took {time.time() - t0:.4f}s")

print("Testing build_spot_prices_panel...")
t0 = time.time()
zisi_terminal.build_spot_prices_panel()
print(f"build_spot_prices_panel took {time.time() - t0:.4f}s")

print("Testing build_regime_panel...")
t0 = time.time()
zisi_terminal.build_regime_panel()
print(f"build_regime_panel took {time.time() - t0:.4f}s")

print("Testing build_active_positions_panel...")
t0 = time.time()
zisi_terminal.build_active_positions_panel()
print(f"build_active_positions_panel took {time.time() - t0:.4f}s")

print("Testing build_closed_positions_panel...")
t0 = time.time()
zisi_terminal.build_closed_positions_panel()
print(f"build_closed_positions_panel took {time.time() - t0:.4f}s")

print("Testing build_logs_panel...")
t0 = time.time()
zisi_terminal.build_logs_panel()
print(f"build_logs_panel took {time.time() - t0:.4f}s")

print("All tests passed! Running 5 fast loops...")
for i in range(5):
    zisi_terminal.sync_file_states()
    zisi_terminal.build_header_panel()
    zisi_terminal.build_metrics_panel()
    zisi_terminal.build_spot_prices_panel()
    zisi_terminal.build_regime_panel()
    zisi_terminal.build_active_positions_panel()
    zisi_terminal.build_closed_positions_panel()
    zisi_terminal.build_logs_panel()
    print(f"Loop {i+1} OK")
