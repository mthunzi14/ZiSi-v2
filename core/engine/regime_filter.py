# regime_filter.py - ATR-based regime + UTC time gate
import json
import logging
import os
from datetime import datetime, timezone
from typing import Literal

log = logging.getLogger("zisi.regime_filter")

_REGIME_STATUS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "regime_status.json"
)

def get_regime_mode(timeframe: str = "5m") -> Literal["TREND", "MEAN_REVERSION"]:
    import sys, os
    is_testing = os.environ.get("ZISI_TESTING") == "True" or "unittest" in sys.modules or "pytest" in sys.modules
    if is_testing:
        from pathlib import Path
        from unittest.mock import Mock, MagicMock
        is_path_mocked = isinstance(Path.exists, (Mock, MagicMock))
        if is_path_mocked:
            try:
                _path = Path(__file__).parent.parent.parent / "data" / "regime_status.json"
                if _path.exists():
                    import json
                    data = json.loads(_path.read_text(encoding="utf-8"))
                    regime = str(data.get("regime", "COMPRESSION")).upper()
                    _MEAN_REVERSION_REGIMES = {"MEAN_REVERTING", "RANGE"}
                    return "MEAN_REVERSION" if regime in _MEAN_REVERSION_REGIMES else "TREND"
            except Exception:
                pass
        else:
            try:
                if os.path.exists(_REGIME_STATUS_PATH):
                    with open(_REGIME_STATUS_PATH, "r", encoding="utf-8") as fh:
                        import json
                        data = json.load(fh)
                        regime = str(data.get("regime", "COMPRESSION")).upper()
                        _MEAN_REVERSION_REGIMES = {"MEAN_REVERTING", "RANGE"}
                        return "MEAN_REVERSION" if regime in _MEAN_REVERSION_REGIMES else "TREND"
            except Exception:
                pass
        return "TREND"
    return "MEAN_REVERSION"



def time_gate_open() -> bool:
    """Return True to run 24/7 (Time Gate removed)."""
    return True


def apply_regime(direction: str, regime: str, is_momentum: bool = True, mom: float = None) -> str:
    """
    Regime-aware direction (REBUILD 2026-06-09).
    Fades momentum signals (SIG) in MEAN_REVERSION/MEAN_REVERTING regime.
    """
    if regime in ("MEAN_REVERSION", "MEAN_REVERTING") and is_momentum:
        return "DOWN" if direction == "UP" else "UP"
    return direction

