"""
updown_engine.py - ZiSi Intelligence Up/Down Engine (Async Restructured)
"""
import asyncio
import logging
import os
import time
import requests
import aiohttp
from datetime import datetime, timezone
from typing import Optional

try:
    from core.engine.technical_cache import TechnicalDataCache  # type: ignore
except ImportError:
    TechnicalDataCache = None  # type: ignore
try:
    from core.engine.spot_websocket_ingest import get_current_ofi
except ImportError:
    def get_current_ofi(*a, **kw): return 0.0  # type: ignore

log = logging.getLogger("zisi.engine")

# ── User Sizing Settings (Sprint 12) ──
# SIZING_BALANCE sets the baseline capital used for sizing.
try:
    from config import SIZING_BALANCE
except ImportError:
    SIZING_BALANCE = None

# Live engine instances keyed by "ASSET/timeframe" for outcome feedback
_ENGINE_REGISTRY: dict[str, "UpDownEngine"] = {}

# Consolidated polling log states
_WAITING_POLLS_ASSETS: dict[tuple, list] = {}
_WAITING_POLLS_LOGGED: set[tuple] = set()

# ---------------------------------------------------------------------------
# BTC Market Leadership Anchor (Item 25)
# BTC is the market leader. When BTC has decisive directional momentum,
# all other assets should align with BTC's direction.
# This dict stores BTC's latest confluence verdict to anchor siblings.
# ---------------------------------------------------------------------------
_BTC_ANCHOR: dict = {
    "direction": None,   # "UP" | "DOWN" | "NEUTRAL" | None
    "score": 0.0,        # confluence score 0.0–1.0
    "cvd_fast": 0.0,     # BTC CVD 10s window at time of eval
    "ts": 0.0,           # unix timestamp of last BTC evaluation
}
_BTC_ANCHOR_MIN_SCORE = 0.60   # BTC must be this decisive to anchor others
_BTC_ANCHOR_MAX_AGE  = 310.0   # seconds: one candle + 10s grace

# Consolidated illiquid book log states for Item 25
_ILLIQUID_BOOKS_ASSETS: dict[tuple, list] = {}
_ILLIQUID_BOOKS_LOGGED: set[tuple] = set()

_GREEN_UP = "\033[1;38;2;193;225;193mUP\033[0m"
_RED_DN = "\033[1;38;2;255;116;108mDOWN\033[0m"
_GREEN_YES = "\033[1;38;2;193;225;193mYES\033[0m"
_RED_NO = "\033[1;38;2;255;116;108mNO\033[0m"


def register_engine(instance: "UpDownEngine") -> None:
    key = f"{instance.asset}/{instance.timeframe}"
    _ENGINE_REGISTRY[key] = instance


def notify_trade_outcome(event_title: str, won: bool) -> None:
    """Feed closed trade result into the matching UpDownEngine (circuit breaker / inversion)."""
    import re
    ma = re.search(r"\[(BTC|ETH|SOL|XRP)\]", event_title or "")
    mt = re.search(r"\[(5m|15m|1h)\]", event_title or "")
    if not ma or not mt:
        return
    eng = _ENGINE_REGISTRY.get(f"{ma.group(1)}/{mt.group(1)}")
    if eng:
        eng.record_outcome(won)

POLY_GAMMA_API = "https://gamma-api.polymarket.com"
POLY_CLOB_API  = "https://clob.polymarket.com"
BINANCE_API    = "https://api.binance.com/api/v3"
BINANCE_FAPI   = "https://fapi.binance.com/fapi/v1"  # Futures REST for assets not on Binance spot

# Assets that must use Binance Futures klines (not on Binance spot)
_FUTURES_KLINES_ASSETS = {"HYPE"}

_GATE_LOG_PATH = None  # resolved lazily on first write


def _write_gate_event(asset: str, timeframe: str, gate: str, direction: str, reason: str) -> None:
    """Append one gate-block event to gate_log.jsonl for dashboard visibility."""
    global _GATE_LOG_PATH
    try:
        import json
        from pathlib import Path
        if _GATE_LOG_PATH is None:
            _GATE_LOG_PATH = Path(__file__).parent.parent.parent / "data" / "gate_log.jsonl"
        entry = {
            "ts": time.time(),
            "asset": asset,
            "tf": timeframe,
            "gate": gate,
            "direction": direction,
            "reason": reason,
        }
        import os
        if os.getenv("ZERO_DISK_LOGGING", "false").lower() == "true":
            logging.getLogger("zisi.gate_events").info(entry)
        else:
            with open(_GATE_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

# Global single-flight Technical Cache shared across all engine instances
_cache = TechnicalDataCache()

# Tier-based Kelly sizing
KELLY = {
    "HIGH": (0.040, 0.150),   # score >= 0.85: 4% Kelly, 15% cap
    "MED":  (0.030, 0.100),   # score 0.75-0.85: 3% Kelly, 10% cap
    "LOW":  (0.015, 0.050),   # score 0.62-0.75: 1.5% Kelly, 5% cap
}
MIN_USD = 1.00
VOLUME_GATE_FLOORS = {"BTC": 2.0, "ETH": 10.0, "SOL": 75.0, "XRP": 5000.0, "DOGE": 10000.0}
UPDOWN_MIN_LIQUIDITY = float(os.getenv("UPDOWN_MIN_LIQUIDITY", "200.0"))

SCORE_TO_WR = [
    (0.85, 0.70),   # score >= 0.85 -> est WR 70% -> max entry 60c
    (0.75, 0.65),   # score 0.75-0.85 -> est WR 65% -> max entry 55c
    (0.62, 0.57),   # score 0.62-0.75 -> est WR 57% -> max entry 47c
]


def _lookup_wr(score: float) -> Optional[float]:
    for threshold, wr in SCORE_TO_WR:
        if score >= threshold:
            return wr
    return None


def price_gate_passes(price: float, score: float) -> bool:
    """Punisher rule: entry price must be >= 10c below estimated WR."""
    est_wr = _lookup_wr(score)
    if est_wr is None:
        return False
    passes = price <= (est_wr - 0.10)
    if not passes:
        log.info("[ENGINE] Price gate FAIL: %.2f > WR(%.2f)-0.10=%.2f", price, est_wr, est_wr - 0.10)
    return passes


# ── Sync Fallbacks (retained for safety / backwards compatibility) ─────────────
def _fetch_klines(symbol: str, interval: str, limit: int) -> list:
    try:
        # HYPE is not on Binance spot — route to Binance Futures REST
        if symbol in _FUTURES_KLINES_ASSETS:
            r = requests.get(
                f"{BINANCE_FAPI}/klines",
                params={"symbol": f"{symbol}USDT", "interval": interval, "limit": limit},
                timeout=8,
            )
        else:
            r = requests.get(
                f"{BINANCE_API}/klines",
                params={"symbol": f"{symbol}USDT", "interval": interval, "limit": limit},
                timeout=8,
            )
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def _fetch_clob_price(token_id: str) -> Optional[float]:
    if not token_id:
        return None
    try:
        r = requests.get(f"{POLY_CLOB_API}/book", params={"token_id": token_id}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            bb = max([float(b.get("price", 0)) for b in bids]) if bids else 0.0
            ba = min([float(a.get("price", 0)) for a in asks]) if asks else 0.0
            if bb > 0 and ba > 0:
                return round((bb + ba) / 2, 4)
            return ba or bb or None
    except Exception:
        return None
    return None


def _fetch_spread(token_id: str) -> Optional[float]:
    if not token_id:
        return None
    try:
        r = requests.get(f"{POLY_CLOB_API}/book", params={"token_id": token_id}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            bb = max([float(b.get("price", 0)) for b in bids]) if bids else 0.0
            ba = min([float(a.get("price", 0)) for a in asks]) if asks else 0.0
            if bb > 0 and ba > 0:
                return round(ba - bb, 4)
    except Exception:
        return None
    return None


# ── Asynchronous Non-Blocking High-Frequency Adapters ─────────────────────────

async def _fetch_klines_async(session: aiohttp.ClientSession, symbol: str, interval: str, limit: int) -> list:
    """Fetch Binance klines using non-blocking, cached, collapsed requests.
    Routes HYPE to Binance Futures REST (fapi) since HYPEUSDT does not exist on Binance spot.
    """
    async def _fetch():
        # HYPE is not on Binance spot — route to Binance Futures REST
        if symbol in _FUTURES_KLINES_ASSETS:
            url = f"{BINANCE_FAPI}/klines"
        else:
            url = f"{BINANCE_API}/klines"
        params = {"symbol": f"{symbol}USDT", "interval": interval, "limit": limit}
        async with session.get(url, params=params, timeout=8) as r:
            if r.status == 200:
                return await r.json()
            return []

    cache_key = f"binance:klines:{symbol}:{interval}:{limit}"
    try:
        return await _cache.get(cache_key, 5.0, _fetch)
    except Exception:
        return []


async def _fetch_clob_book_async(session: aiohttp.ClientSession, token_id: str) -> Optional[dict]:
    """Fetch Polymarket order book using non-blocking, cached, collapsed requests."""
    if not token_id:
        return None
    async def _fetch():
        url = f"{POLY_CLOB_API}/book"
        params = {"token_id": token_id}
        async with session.get(url, params=params, timeout=5) as r:
            if r.status == 200:
                return await r.json()
            return None

    cache_key = f"clob:book:{token_id}"
    try:
        return await _cache.get(cache_key, 2.0, _fetch)
    except Exception:
        return None


def _parse_clob_book(book: Optional[dict]) -> tuple[Optional[float], Optional[float]]:
    """Parse bids/asks from CLOB book JSON to extract mid-price and spread in 1-pass."""
    if not book:
        return None, None
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    bb = max([float(b.get("price", 0)) for b in bids]) if bids else 0.0
    ba = min([float(a.get("price", 0)) for a in asks]) if asks else 0.0
    price = None
    spread = None
    if bb > 0 and ba > 0:
        price = round((bb + ba) / 2, 4)
        spread = round(ba - bb, 4)
    elif ba > 0 or bb > 0:
        price = ba or bb or None
    return price, spread


async def _fetch_gamma_events_async(session: aiohttp.ClientSession, slug: str) -> list:
    """Fetch event details from Gamma API non-blockingly."""
    async def _fetch():
        url = f"{POLY_GAMMA_API}/events"
        params = {"slug": slug}
        async with session.get(url, params=params, timeout=10) as r:
            if r.status == 200:
                raw = await r.json()
                return [raw] if isinstance(raw, dict) and "id" in raw else (raw if isinstance(raw, list) else raw.get("data", []))
            return []

    cache_key = f"gamma:events:{slug}"
    try:
        return await _cache.get(cache_key, 10.0, _fetch)
    except Exception:
        return []


def _compute_rsi(closes: list, period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    if al == 0:
        return 100.0
    return round(100 - (100 / (1 + ag / al)), 2)


def _compute_momentum(closes: list, lookback: int = 5) -> float:
    if len(closes) < lookback + 1:
        return 0.0
    return (closes[-1] - closes[-lookback]) / closes[-lookback] * 100


class UpDownEngine:
    """Per-asset Up/Down trading engine with ZiSi intelligence."""

    def __init__(self, asset: str, timeframe: str, state_mgr, telegram_fn=None):
        self.asset      = asset
        self.timeframe  = timeframe
        self.state_mgr  = state_mgr
        self.telegram   = telegram_fn or (lambda msg: None)

        self.consecutive_losses: int = 0
        self.skip_windows:       int = 0
        self.invert_signal:     bool = False
        self._recent_outcomes:  list = []   # True=win, False=loss; rolling 40
        try:
            import json
            from pathlib import Path
            _db_path = Path(__file__).parent.parent.parent / "data" / "positions_state.json"
            if _db_path.exists():
                with open(_db_path, "r", encoding="utf-8") as _fh:
                    _db_data = json.load(_fh)
                    _closed = _db_data.get("closed", [])
                    _my_outcomes = []
                    for _pos in _closed:
                        _title = _pos.get("event_title", "")
                        if f"[{self.asset}]" in _title and f"[{self.timeframe}]" in _title:
                            _pnl = float(_pos.get("realized_pnl", 0.0))
                            _my_outcomes.append(_pnl > 0.0)
                    self._recent_outcomes = _my_outcomes[-40:]
                    log.info("[ENGINE] %s/%s: Initialised rolling outcomes with %d historical trades.", 
                             self.asset, self.timeframe, len(self._recent_outcomes))
        except Exception as _e_init:
            log.warning("[ENGINE] Failed to load historical outcomes for %s/%s: %s", self.asset, self.timeframe, _e_init)

        self._prefetched_markets: dict = {}  # boundary_ts -> market_dict
        self.last_edge_context: Optional[dict] = None
        self._slope_history:    list = []   # rolling 4 slope readings for choppy detection
        self._choppy_candles:   int  = 0    # candles remaining in choppy cooldown
        self._current_regime_calculated: str = "MEAN_REVERTING"
        self._check_inversion()

    def _get_hourly_slug(self, timestamp: int) -> str:
        from zoneinfo import ZoneInfo
        import datetime
        dt_utc = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        dt_et = dt_utc.astimezone(ZoneInfo("America/New_York"))
        
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]
        month_name = months[dt_et.month - 1]
        
        hour_12 = dt_et.hour % 12
        if hour_12 == 0:
            hour_12 = 12
        am_pm = "pm" if dt_et.hour >= 12 else "am"
        
        asset_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "XRP": "xrp",
            "DOGE": "dogecoin",
        }
        asset_name = asset_map.get(self.asset, self.asset.lower())
        return f"{asset_name}-up-or-down-{month_name}-{dt_et.day}-{dt_et.year}-{hour_12}{am_pm}-et"

    # ── Circuit breaker ───────────────────────────────────────────────────────

    def record_outcome(self, won: bool) -> None:
        """Update consecutive-loss counter and rolling WR for inversion check."""
        self._recent_outcomes.append(won)
        if len(self._recent_outcomes) > 40:
            self._recent_outcomes.pop(0)

        if won:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1

        self._check_inversion()

    def _check_inversion(self) -> None:
        if len(self._recent_outcomes) < 40:
            return
        rolling_wr = sum(self._recent_outcomes) / 40
        from config import INVERSION_TRIGGER_WR, INVERSION_RECOVERY_WR
        if rolling_wr < INVERSION_TRIGGER_WR and not self.invert_signal:
            self.invert_signal = True
            self.telegram(
                f"INVERT {self.asset}/{self.timeframe}: WR={rolling_wr:.0%} over 40 windows — INVERTING signal"
            )
            log.warning("[ENGINE] %s/%s: WR=%.0f%% — signal INVERTED", self.asset, self.timeframe, rolling_wr * 100)
        elif rolling_wr > INVERSION_RECOVERY_WR and self.invert_signal:
            self.invert_signal = False
            self.telegram(
                f"REVERT {self.asset}/{self.timeframe}: WR recovered to {rolling_wr:.0%} — reverting inversion"
            )
            log.info("[ENGINE] %s/%s: WR=%.0f%% — inversion REVERTED", self.asset, self.timeframe, rolling_wr * 100)

    # ── Fair-value entry helper ───────────────────────────────────────────────

    def _fair_value_entry(self, klines, spot, up_price, dn_price, elapsed_min, custom_strike=None):
        """Fair-value (spot-distance) margin decision at the REAL live quotes.
        Returns decide_value_entry's dict plus fp_up/sigma_frac for logging."""
        from core.engine.fair_value import fair_prob_up, decide_value_entry
        from core.engine.regime_filter import get_regime_mode
        try:
            s_0 = custom_strike if custom_strike is not None else float(klines[-1][1])          # current window open = strike
        except (IndexError, ValueError, TypeError):
            return {"direction": None, "edge": 0.0, "archetype": None, "fp_up": 0.5, "sigma_frac": 0.0}
        total_min = 60.0 if self.timeframe == "1h" else float(int(self.timeframe.rstrip("m")))
        trs = []
        for i in range(max(1, len(klines) - 14), len(klines)):
            h, l, pc = float(klines[i][2]), float(klines[i][3]), float(klines[i - 1][4])
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
        atr = (sum(trs) / len(trs)) if trs else 0.0
        sigma_frac = (atr / s_0) if s_0 else 0.01
        # ETH sigma floor: prevents FV from firing on micro-moves for ETH
        if self.asset == "ETH" and sigma_frac < 0.0040:
            sigma_frac = 0.0040
            log.debug("[ETH-SIGMA] ETH sigma_frac floored to 0.0040")

        # ── Momentum/flow DRIFT (REBUILD): give FV a real directional edge ──
        # The old model was driftless => coin-flip at ATM, exactly the band mentor PBot-6
        # prints in. We project a fraction of the prevailing momentum (EMA-5 vs EMA-20
        # slope) over the remaining window, and DAMPEN it in mean-reverting/chop regimes.
        def _ema(prices, period):
            if len(prices) < period:
                return prices[-1] if prices else 0.0
            mult = 2.0 / (period + 1)
            ema = prices[0]
            for p in prices[1:]:
                ema = (p - ema) * mult + ema
            return ema

        closes = [float(k[4]) for k in klines]
        ema_5 = _ema(closes, 5)
        ema_20 = _ema(closes, 20)
        mom = ((ema_5 - ema_20) / ema_20) if ema_20 else 0.0  # signed normalized momentum

        regime = get_regime_mode()
        from core.engine.fair_value import directional_drift, DEFAULT_CONTINUATION
        _cont = DEFAULT_CONTINUATION
        if regime in ("MEAN_REVERSION", "MEAN_REVERTING", "COMPRESSION"):
            _cont *= 0.35  # momentum unlikely to persist in chop — dampen the projected drift
        drift = directional_drift(mom, sigma_frac=sigma_frac, continuation=_cont)

        fp_up = fair_prob_up(spot, s_0, sigma_frac, elapsed_min, total_min, drift=drift)
        from core.engine.fair_value import DEFAULT_VALUE_PARAMS
        custom_params = dict(DEFAULT_VALUE_PARAMS)
        custom_params["edge_margin"] = 0.12 if regime == "TREND" else 0.06

        dec = decide_value_entry(fp_up, up_price, dn_price, elapsed_min, total_min,
                                 params=custom_params,
                                 regime=regime, timeframe=self.timeframe, pct_move=mom)
        dec["drift"] = round(drift, 6)
        dec["fp_up"] = round(fp_up, 4)
        dec["sigma_frac"] = round(sigma_frac, 6)
        return dec

    # ── Signal generation ─────────────────────────────────────────────────────

    async def generate_signal(self, session: aiohttp.ClientSession) -> Optional[dict]:
        """Return {direction, score, price_up, price_dn, market} or None."""
        if self.skip_windows > 0:
            log.info("[ENGINE] %s/%s: skipping window (circuit breaker active)", self.asset, self.timeframe)
            return None

        from core.engine.regime_filter import get_regime_mode, time_gate_open, apply_regime
        fast_cvd = slow_cvd = binance_obi = None
        if not time_gate_open():
            log.debug("[ENGINE] %s/%s: time gate closed", self.asset, self.timeframe)
            return None

        # Volatility Gate: block 5m entries under high volatility (DISABLED to allow continuous execution)
        if False:  # self.timeframe == "5m":
            try:
                import json as _json
                from pathlib import Path as _Path
                _rs = _Path(__file__).parent.parent.parent / "data" / "regime_status.json"
                if _rs.exists():
                    _d = _json.loads(_rs.read_text(encoding="utf-8"))
                    _reg = _d.get("regime")
                    _price_samples = int(_d.get("price_samples", 0))
                    # Require >=20 samples for a meaningful percentile rank.
                    # With <20 samples the mean ATR lands near the 75th percentile by construction,
                    # causing a false-positive VOL-VETO that blocks all 5m entries after a clean slate.
                    _atr_pct = float(_d.get("atr_percentile", 50.0)) if _price_samples >= 20 else 50.0
                    if _reg == "VOLATILE_CHAOS" or _atr_pct >= 80.0:
                        log.info(
                            "[VOL-VETO] %s/5m: Volatility too high (regime=%s, atr_percentile=%.1f%%) — blocking 5m entry.",
                            self.asset, _reg, _atr_pct
                        )
                        _write_gate_event(self.asset, self.timeframe, "VOLATILE_CHAOS", "N/A", f"regime={_reg}, atr_pct={_atr_pct:.1f}%")
                        return None
            except Exception as e:
                log.warning("[ENGINE] Volatility gate error: %s", e)

        # Fetch klines for the primary timeframe
        tf_map = {"5m": ("5m", 30), "15m": ("15m", 30), "1h": ("1h", 30)}
        interval, limit = tf_map.get(self.timeframe, ("5m", 30))
        klines = await _fetch_klines_async(session, self.asset, interval, limit)
        if len(klines) < 16:
            log.warning("[ENGINE] %s/%s: Insufficient candles (%d < 16) to calculate indicators.", self.asset, self.timeframe, len(klines))
            return None

        closes = [float(k[4]) for k in klines]

        # FEED CONSISTENCY (2026-06-10): closes[-1] must stay Binance. The strike
        # (klines[-1][1]) and resolution (Binance candle close) are both Binance, but
        # Pyth prints a persistent -3..-5 bps basis below Binance. Overwriting the live
        # close with Pyth injected a phantom down-move into every directional read:
        # fair_prob_up averaged 0.42 and 77% of all FV signals fired DOWN.

        # Recalculate market regime dynamically
        try:
            from core.engine.regime_detector import RegimeDetector
            detector = RegimeDetector(timeframe=self.timeframe, atr_window=14)
            write_to_disk = (self.asset == "BTC")

            # Fetch OBI and calculate Volume Ratio to feed detector context
            from core.engine.spot_websocket_ingest import get_binance_obi
            _obi_val = await get_binance_obi(self.asset)
            _obi_val = _obi_val if _obi_val is not None else 0.0

            _vol_ratio = 1.0
            if len(klines) >= 21:
                try:
                    _current_vol = float(klines[-1][5])
                    _prev_vols = [float(k[5]) for k in klines[-21:-1]]
                    _avg_vol = sum(_prev_vols) / len(_prev_vols)
                    if _avg_vol > 0:
                        _vol_ratio = _current_vol / _avg_vol
                except Exception as _vol_err:
                    log.debug("[ENGINE] Failed to compute volume ratio for regime: %s", _vol_err)

            detector.update_context(obi=_obi_val, volume_ratio=_vol_ratio, write_to_disk=write_to_disk)
            detector.update_prices(closes, symbol=self.asset, write_to_disk=write_to_disk)
            self._current_regime_calculated = detector._current_regime
            self._detected_regime_calculated = detector.detected_regime
        except Exception as e:
            log.warning("[ENGINE] Failed to update regime detector for %s: %s", self.asset, e)
            self._current_regime_calculated = "MEAN_REVERTING"
            self._detected_regime_calculated = "MEAN_REVERTING"

        rsi = _compute_rsi(closes)
        self._last_rsi = rsi  # Store RSI for fair-value paper fallbacks
        mom = _compute_momentum(closes)
        if rsi is None:
            log.warning("[ENGINE] %s/%s: RSI calculation returned None.", self.asset, self.timeframe)
            return None

        # Retrieve real-time Spot Order Flow Imbalance (OFI)
        ofi = await get_current_ofi(self.asset)

        # Fetch market L2 quotes early
        market = await self._fetch_market(session)
        if not market:
            return None

        import sys, os as _os_t
        is_testing = _os_t.environ.get("ZISI_TESTING") == "True" or "unittest" in sys.modules or "pytest" in sys.modules

        # TTL gate check deferred until after indicator calculation to allow late-candle certainty snipes (Tranche C)

        # Verify that the fetched market's start timestamp matches the current candle start timestamp
        # Prevents timeframe mismatch where we place trades on upcoming or previous candles
        # based on the current candle's indicators.
        duration_min = market.get("duration_min")
        if duration_min is None:
            duration_min = 60 if self.timeframe == "1h" else int(self.timeframe.rstrip("m"))
        market_start_ts = market["expiry_ts"] - duration_min * 60
        last_kline_ts = int(klines[-1][0]) // 1000
        if market_start_ts != last_kline_ts and not is_testing:
            log.debug(
                "[ENGINE] %s/%s Timeframe mismatch detected: market_start_ts=%d last_kline_ts=%d — logging mismatch but proceeding",
                self.asset, self.timeframe, market_start_ts, last_kline_ts
            )

        up_price = market["up_price"]
        dn_price = market["dn_price"]
        is_dual_eligible = self.should_dual_enter(up_price, dn_price)
        regime = get_regime_mode(self.timeframe)

        # 1-Hour Streak Reversal Check
        if self.timeframe == "1h" and len(klines) >= 5:
            closed_klines = klines[-5:-1]
            all_green = all(float(k[4]) > float(k[1]) for k in closed_klines)
            all_red = all(float(k[4]) < float(k[1]) for k in closed_klines)
            if all_green or all_red:
                # Gate: 65c+ contra-price required for meaningful Kelly sizing.
                # At 54c the crowd edge is thin — 8% Kelly on $50 = $4, barely worth 1h exposure.
                _rev_contra_price = dn_price if all_green else up_price
                _rev_min_price = 0.65
                if _rev_contra_price < _rev_min_price:
                    log.info(
                        "[REV-STREAK-GATE] %s/1h: contra price %.4f < %.4f min — skip",
                        self.asset, _rev_contra_price, _rev_min_price,
                    )
            if (all_green or all_red) and _rev_contra_price >= _rev_min_price:
                raw_dir = "DOWN" if all_green else "UP"
                direction = apply_regime(raw_dir, regime, is_momentum=False)  # reversal — already contrarian
                if self.invert_signal:
                    direction = "DOWN" if direction == "UP" else "UP"
                
                score = 0.75
                log.warning(
                    "[REVERSAL-STREAK-1H] %s/1h: 4 consecutive %s closed candles. Sniping counter-trend %s (regime=%s, raw=%s)",
                    self.asset, "green" if all_green else "red", direction, regime, raw_dir
                )
                
                edge_ctx = {}
                try:
                    from core.engine.edge_orchestrator import edge_orchestrator
                    sig_dict = {
                        "signal_type": "TYPE_A_HIGH",
                        "score": score,
                        "affected_cryptos": [self.asset],
                        "entry_price": up_price if direction == "UP" else dn_price,
                    }
                    edge_ctx = await edge_orchestrator.get_trade_context(
                        session=session,
                        asset=self.asset,
                        direction=direction,
                        signal=sig_dict,
                        market=market,
                        current_price=closes[-1]
                    )
                    self.last_edge_context = edge_ctx
                    
                    boost = edge_ctx.get("combined_confidence_boost", 0.0)
                    if boost != 0.0:
                        score = max(0.10, min(1.0, score + boost))
                        log.debug("[EDGE] %s/%s Score adjusted by boost: %.2f (boost=%+.2f)", self.asset, self.timeframe, score, boost)
                    
                    regime = edge_ctx.get("regime_name", regime)
                except Exception as e:
                    log.warning("[EDGE] Failed to query EdgeOrchestrator in 1h streak reversal: %s", e)
                    self.last_edge_context = None

                _streak_whale = edge_ctx.get("whale_pressure", 0.0) if edge_ctx else 0.0
                if abs(_streak_whale) >= 0.85:
                    _whale_contradicts = (
                        (_streak_whale < 0 and direction == "UP") or   # Bears contradict UP
                        (_streak_whale > 0 and direction == "DOWN")    # Bulls contradict DOWN
                    )
                    if _whale_contradicts:
                        log.warning(
                            "[STREAK-WHALE-VETO] %s/1h: whale pressure %.2f contradicts %s — skipping streak reversal",
                            self.asset, _streak_whale, direction
                        )
                        return None

                if edge_ctx:
                    whale_pressure = edge_ctx.get('whale_pressure', 0.0)
                    whale_is_up = whale_pressure >= 0.0
                    _whale_aligned = (whale_is_up == (direction == 'UP'))
                    _confluence_score = edge_ctx.get('confluence_score', 0)
                else:
                    _whale_aligned = True
                    _confluence_score = 2

                return {
                    "asset":        self.asset,
                    "timeframe":    self.timeframe,
                    "direction":    direction,
                    "score":        score,
                    "regime":       regime,
                    "inverted":     self.invert_signal,
                    "rsi":          rsi,
                    "momentum":     round(mom, 4),
                    "market":       market,
                    "is_dual_eligible": is_dual_eligible,
                    "edge_context": edge_ctx,
                    "entry_source": "REVERSAL_STREAK",
                    "corroboration_multiplier": 1.0,
                    "whale_aligned": _whale_aligned,
                    "confluence_score": _confluence_score,
                    "is_reversal": True,
                }


        # ── Fair-value primary entry (prioritized check) ──
        # Check if we have a valid fair-value signal that clears the margin first.
        # If we do, we bypass volume, OFI, and trend gates entirely.
        _fv = {"direction": None}
        is_fv_trade = False
        _fv_confidence = 0.0          # REBUILD: FV directional confidence (drives ATM guard + sizing)
        _fv_archetype = "moderate"
        try:
            from config import FAIR_VALUE_MODE
        except Exception:
            FAIR_VALUE_MODE = False

        if FAIR_VALUE_MODE:
            _now_ts = datetime.now(timezone.utc).timestamp()
            _candle_duration_s = 3600 if self.timeframe == "1h" else (900 if self.timeframe == "15m" else 300)

            # Verify klines list is updated for the current candle start
            _expected_start_ts = int(_now_ts // _candle_duration_s * _candle_duration_s)
            _last_kline_ts = int(klines[-1][0]) // 1000 if klines else 0


            if _last_kline_ts != _expected_start_ts and not is_testing:
                # Klines list is lagged — wait for next tick to resolve current strike
                log.info(
                    "[ENGINE] %s/%s: Lagged klines list at candle boundary (last_kline_ts=%d expected_start_ts=%d) — skipping Fair Value decision for this tick",
                    self.asset, self.timeframe, _last_kline_ts, _expected_start_ts
                )
                _timing_ok = False
            else:
                _candle_open_ts = _last_kline_ts
                _elapsed_min = max(0.0, (_now_ts - _candle_open_ts) / 60.0)

                # Timing gate check
                # Deep contrarian (<40c): 0.5 min minimum — the best setup is the very first minute
                # after a strong directional candle (market overreacts, spot starts at 0% from open).
                # ATM/moderate: 1.0 min minimum to let price action settle.
                _is_deep_contra_price = min(up_price, dn_price) < 0.40
                _fv_min = 1.0 if self.timeframe == "1h" else (0.05 if _is_deep_contra_price else 1.0)  # 0.1min=6s: catch early-candle overreaction
                _timing_ok = True

                # Strict upper-bound timing gates: block late-candle entries
                if not is_testing:
                    if self.timeframe == "5m" and _elapsed_min > 4.0:
                        _timing_ok = False
                    elif self.timeframe == "15m" and _elapsed_min > 13.0:
                        _timing_ok = False
                    elif self.timeframe == "1h" and _elapsed_min > 55.0:
                        _timing_ok = False
                    elif _elapsed_min < _fv_min:
                        _timing_ok = False

            if _timing_ok:
                from core.engine.polymarket_rtds_ingest import get_chainlink_price, get_chainlink_candle_open
                cl_details = await get_chainlink_price(self.asset)
                cl_fresh = False
                if cl_details:
                    cl_now, cl_ts = cl_details
                    if time.time() - cl_ts <= 60.0:
                        cl_fresh = True

                _custom_strike = None
                if cl_fresh:
                    _fv_spot = cl_now
                    _total_min = 60.0 if self.timeframe == "1h" else float(int(self.timeframe.rstrip("m")))
                    _interval_sec = int(_total_min * 60)
                    _candle_start = int(time.time() // _interval_sec) * _interval_sec
                    _cl_open = await get_chainlink_candle_open(self.asset, _interval_sec, _candle_start)
                    if _cl_open is not None:
                        _custom_strike = _cl_open
                        log.info("[PRICE-SOURCE] %s/%s: Using authoritative Chainlink price (Spot=%.4f, Strike=%.4f)",
                                 self.asset, self.timeframe, _fv_spot, _custom_strike)
                    else:
                        _custom_strike = float(klines[-1][1])
                        log.info("[PRICE-SOURCE] %s/%s: Chainlink open initializing — using Binance open (Spot=%.4f, Strike=%.4f)",
                                 self.asset, self.timeframe, _fv_spot, _custom_strike)
                else:
                    _fv_spot = float(klines[-1][4])
                    _custom_strike = float(klines[-1][1])
                    _last_up_str = f"LastUpdate: {int(cl_ts)} ({round(time.time() - cl_ts, 1)}s ago)" if cl_details else "No feed data"
                    log.info("[PRICE-SOURCE] %s/%s: Chainlink feed initializing (%s) — using Binance spot fallback (Spot=%.4f, Strike=%.4f)",
                             self.asset, self.timeframe, _last_up_str, _fv_spot, _custom_strike)

                _fv = self._fair_value_entry(klines, _fv_spot, up_price, dn_price, _elapsed_min, custom_strike=_custom_strike)

                if _fv.get('direction') is not None:
                    # FV spot-direction alignment gate
                    # Block FV entries where current spot is moving AGAINST the signal direction.
                    # fair_value_entry() can lag spot by 1-2 ticks; if spot has already moved
                    # 0.25%+ against the FV call, the edge has been arbitraged away.
                    _fv_spot_align = True
                    try:
                        _candle_open = _custom_strike if _custom_strike is not None else float(klines[-1][1])
                        _spot_now = _fv_spot
                        _spot_pct = (_spot_now - _candle_open) / _candle_open if _candle_open > 0 else 0.0
                        _ALIGN_THRESH = 0.0050  # 0.50% — ATM directional-conflict gate
                        # Deep contrarian (<40c) BYPASSES this gate. A cheap contract exists
                        # because spot moved strongly against it — that IS the contrarian setup.
                        _fv_entry_p = dn_price if _fv['direction'] == 'DOWN' else up_price
                        _fv_is_deep_contra = _fv_entry_p < 0.40
                        if not _fv_is_deep_contra:
                            if _fv['direction'] == 'DOWN' and _spot_pct > _ALIGN_THRESH:
                                log.info(
                                    '[FV-SPOT-ALIGN] %s/%s: FV=DOWN but spot +%.3f%% above open — misaligned — skip',
                                    self.asset, self.timeframe, _spot_pct * 100,
                                )
                                _fv_spot_align = False
                            elif _fv['direction'] == 'UP' and _spot_pct < -_ALIGN_THRESH:
                                log.info(
                                    '[FV-SPOT-ALIGN] %s/%s: FV=UP but spot -%.3f%% below open — misaligned — skip',
                                    self.asset, self.timeframe, abs(_spot_pct) * 100,
                                )
                                _fv_spot_align = False
                        else:
                            # Tier 0: deep contrarian bypass requires high confidence AND
                            # sufficient time remaining (5m <90s left = no time to resolve).
                            _dc_min_conf = float(os.getenv("FV_DEEP_CONTRA_MIN_CONF", "0.72"))
                            _dc_conf = float(_fv.get("confidence", 0.0))
                            if _dc_conf < _dc_min_conf:
                                log.info(
                                    '[FV-SPOT-ALIGN] %s/%s: deep contrarian %.4f — conf %.2f < %.2f (FV_DEEP_CONTRA_MIN_CONF) — blocked',
                                    self.asset, self.timeframe, _fv_entry_p, _dc_conf, _dc_min_conf,
                                )
                                _fv_spot_align = False
                            elif self.timeframe == "5m" and _elapsed_min > 3.5:
                                log.info(
                                    '[FV-SPOT-ALIGN] %s/%s: deep contrarian %.4f — <90s remaining (elapsed=%.2fmin) — blocked',
                                    self.asset, self.timeframe, _fv_entry_p, _elapsed_min,
                                )
                                _fv_spot_align = False
                            else:
                                log.info(
                                    '[FV-SPOT-ALIGN] %s/%s: deep contrarian %.4f @ conf=%.2f — bypass approved (spot %.3f%%)',
                                    self.asset, self.timeframe, _fv_entry_p, _dc_conf, _spot_pct * 100,
                                )
                    except Exception:
                        pass  # fail open — do not block if price data unavailable
                    if not _fv_spot_align:
                        _fv = {'direction': None, 'edge': 0.0, 'archetype': None}

                # FV Archetype Gate REMOVED (REBUILD 2026-06-09): it blocked ALL moderate FV
                # unless regime == "RANGE" — a label get_regime_mode() NEVER emits (it returns
                # only "TREND"/"MEAN_REVERSION") — so daytime FV was zeroed out entirely
                # (live: FAIR-VALUE signals = 0). FV is now gated by its directional CONFIDENCE
                # + edge thresholds (the real quality controls), not a regime archetype.

                # Tier 2A: 4-Regime FV gate — MEAN_REVERSION + 5m requires higher confidence.
                # Deep contrarian continuation bets on 5m fail in MEAN_REVERSION because the
                # candle window is too short for the trend to assert itself (Punisher confirmed).
                # 15m/1h unaffected — more time for signal to resolve.
                if _fv.get("direction") is not None and self.timeframe == "5m" and regime == "MEAN_REVERSION":
                    _regime_fv_ep = dn_price if _fv["direction"] == "DOWN" else up_price
                    _regime_req_conf = 0.78 if _regime_fv_ep < 0.42 else 0.70
                    _regime_fv_conf = float(_fv.get("confidence", 0.0))
                    if _regime_fv_conf < _regime_req_conf:
                        log.info(
                            "[FV-REGIME-GATE] %s/5m: MEAN_REVERSION regime — FV %.4f conf=%.2f < %.2f — skip",
                            self.asset, _regime_fv_ep, _regime_fv_conf, _regime_req_conf,
                        )
                        _fv = {"direction": None, "edge": 0.0, "archetype": None, "confidence": 0.0, "fp_up": 0.0}

                if _fv.get("direction") is not None:
                    # Apply tiered edge gate and penalties
                    _entry_price_fv = up_price if _fv["direction"] == "UP" else dn_price
                    _cross_tf_conflict = False
                    if self.timeframe == "5m":
                        try:
                            _k15 = await _fetch_klines_async(session, self.asset, "15m", 5)
                            if len(_k15) >= 2:
                                _last15_bull = float(_k15[-2][4]) > float(_k15[-2][1])
                                _cross_tf_conflict = (_last15_bull != (_fv["direction"] == "UP"))
                        except Exception:
                            pass

                    if _entry_price_fv >= 0.50 and _entry_price_fv < 0.65:
                        _min_edge = 0.10  # REBUILD: 0.12->0.10, lift mid-band FV flow
                    elif _entry_price_fv >= 0.65:
                        _min_edge = 0.08  # REBUILD: 0.10->0.08
                    else:
                        _min_edge = 0.05

                    if _cross_tf_conflict:
                        _min_edge = max(_min_edge, _min_edge + 0.03)
                    # Asset-specific min_edge penalties REMOVED — were blocking ETH/SOL FV trades
                    # if self.asset == "ETH" and 0.40 <= _entry_price_fv < 0.65:
                    #     _min_edge = max(_min_edge, 0.15)
                    # if self.asset == "SOL":
                    #     _min_edge = max(_min_edge, 0.15)
                    # if self.timeframe == "15m":
                    #     _min_edge = max(_min_edge, 0.10)

                    # Macro-aware FV edge penalty
                    if len(klines) >= 10:
                        _fv_m8 = klines[-9:-1]
                        _fv_m_up = sum(1 for k in _fv_m8 if float(k[4]) > float(k[1]))
                        _fv_m_dn = 8 - _fv_m_up
                        _fv_is_up = _fv["direction"] == "UP"
                        # REBUILD: relaxed from near-block (0.25) to a moderate tilt — with the new
                        # momentum drift FV rarely fights a strong trend, and high-conviction
                        # counter-trend FV (fading an exhausted run) should still be allowed.
                        if (_fv_m_up >= 6 and not _fv_is_up) or (_fv_m_dn >= 6 and _fv_is_up):
                            _min_edge = _min_edge + 0.08
                        elif (_fv_m_up >= 5 and not _fv_is_up) or (_fv_m_dn >= 5 and _fv_is_up):
                            _min_edge = _min_edge + 0.04

                    if _fv["edge"] >= _min_edge:
                        # Peer corroboration size calculation
                        _PEERS = {
                            "BTC": ["ETH", "SOL"], "ETH": ["BTC", "SOL"],
                            "SOL": ["BTC", "ETH"], "XRP": ["BTC", "ETH"],
                            "DOGE": ["BTC"],
                        }
                        _corroborated = False
                        for _peer in _PEERS.get(self.asset, []):
                            try:
                                _pk = await _fetch_klines_async(session, _peer, "5m", 5)
                                if len(_pk) >= 2:
                                    _peer_bull = float(_pk[-2][4]) > float(_pk[-2][1])
                                    if _peer_bull == (_fv["direction"] == "UP"):
                                        _corroborated = True
                                        break
                            except Exception:
                                pass
                        _corroboration_multiplier = 1.3 if _corroborated else 1.0

                        # We have a valid Fair Value trade signal! Set direction and score.
                        raw_dir = _fv["direction"]
                        direction = apply_regime(raw_dir, regime, is_momentum=False)  # FV carries its own directional edge
                        if self.invert_signal:
                            direction = "DOWN" if direction == "UP" else "UP"
                        
                        score_base = min(0.90, 0.55 + min(0.30, _fv["edge"]) + (0.05 if _fv["archetype"] == "near_certainty" else 0.0))
                        
                        log.info("[FAIR-VALUE] %s/%s %s | fp=%.3f quote=%.3f edge=%.3f (%s)",
                                 self.asset, self.timeframe, raw_dir, _fv["fp_up"],
                                 up_price if raw_dir == "UP" else dn_price, _fv["edge"], _fv["archetype"])

                        try:
                            from core.engine.logger import log_fair_value_entry  # type: ignore
                            log_fair_value_entry({
                                "asset": self.asset, "timeframe": self.timeframe, "direction": raw_dir,
                                "fp_up": _fv["fp_up"], "quote": (up_price if raw_dir == "UP" else dn_price),
                                "edge": _fv["edge"], "archetype": _fv["archetype"],
                                "elapsed_min": round(_elapsed_min, 2), "entry_ts": _now_ts,
                            })
                        except Exception:
                            pass

                        # Set entry source and bypass momentum cascade
                        entry_source = "FAIR_VAL"
                        is_fv_trade = True
                        _fv_confidence = float(_fv.get("confidence", 0.0))
                        _fv_archetype = _fv.get("archetype", "moderate")

        if not is_fv_trade:
            # Volume gate
            volumes = [float(k[5]) for k in klines]
            avg_vol = sum(volumes[:-1]) / max(1, len(volumes) - 1)
            cur_vol = volumes[-2] if len(volumes) >= 2 else volumes[-1]
            floor = VOLUME_GATE_FLOORS.get(self.asset, 0.0)
            if cur_vol < floor and cur_vol < 0.30 * avg_vol:
                log.info("[ENGINE] %s/%s: volume gate fail (current vol %.1f < floor %.1f or < 30%% of avg %.1f)", self.asset, self.timeframe, cur_vol, floor, avg_vol)
                return None
                
            # Volume Climax Detector - disabled by setting threshold very high
            vol_climax_threshold = 999.0
            if cur_vol > vol_climax_threshold * avg_vol:
                log.info("[ENGINE] %s/%s: Volume climax detected (current vol %.1f > %.1fx avg %.1f). Blocking trade to avoid blow-off top/bottom.", self.asset, self.timeframe, cur_vol, vol_climax_threshold, avg_vol)
                return None

            # Volume surge block - disabled by setting threshold very high
            if len(volumes) >= 7:
                _roll_avg_vol = sum(volumes[-7:-2]) / 5
                if _roll_avg_vol > 0 and cur_vol > 999.0 * _roll_avg_vol:
                    log.info(
                        "[VOL-SURGE] %s/%s: spike %.0f > 4x avg %.0f — 2-candle pause",
                        self.asset, self.timeframe, cur_vol, _roll_avg_vol,
                    )
                    self._choppy_candles = max(self._choppy_candles, 2)
                    return None

            # Check if there is a strong 4/4 trend agreement for RSI trigger loosening (Sprint 11)
            trend_up_agreement = False
            trend_dn_agreement = False
            try:
                from core.engine.confluence_engine import ConfluenceEngine
                from core.engine.edge_orchestrator import edge_orchestrator
                if edge_orchestrator and getattr(edge_orchestrator, "_confluence", None):
                    conf_engine = edge_orchestrator._confluence
                else:
                    conf_engine = ConfluenceEngine()
                conf_up = await conf_engine.get_confluence(session, self.asset, "UP")
                if conf_up.get("score", 0) == 4:
                    trend_up_agreement = True
                    log.info("[ENGINE] %s/%s: Strong 4/4 %s trend agreement detected. Activating UP RSI trigger loosening.", self.asset, self.timeframe, _GREEN_UP)
                else:
                    conf_dn = await conf_engine.get_confluence(session, self.asset, "DOWN")
                    if conf_dn.get("score", 0) == 4:
                        trend_dn_agreement = True
                        log.info("[ENGINE] %s/%s: Strong 4/4 %s trend agreement detected. Activating DOWN RSI trigger loosening.", self.asset, self.timeframe, _RED_DN)
            except Exception as e:
                log.warning("[ENGINE] Failed to check trend agreement for RSI loosening: %s", e)

            # Read live volatility percentiles for the 5m volatility veto
            _atr_pct = _bbw_pct = None
            try:
                import json as _json
                from pathlib import Path as _Path
                _rs = _Path(__file__).parent.parent.parent / "data" / "regime_status.json"
                if _rs.exists():
                    _d = _json.loads(_rs.read_text(encoding="utf-8"))
                    _atr_pct = float(_d.get("atr_percentile", 50.0))
                    _bbw_pct = float(_d.get("bbw_percentile", 50.0))
            except Exception:
                pass

            # Fetch order flow metrics (CVD and OBI) early
            fast_cvd = slow_cvd = binance_obi = None
            try:
                from core.engine.spot_websocket_ingest import get_cvd_metrics, get_binance_obi, _has_cvd_data
                if _has_cvd_data(self.asset):
                    fast_cvd, slow_cvd = await get_cvd_metrics(self.asset)
                    binance_obi = await get_binance_obi(self.asset)
            except Exception as _e:
                log.warning("[ENGINE] Failed to pre-fetch order flow metrics: %s", _e)

            # Write status to gate matrix file for UI dashboard (Always update on each candle check)
            try:
                from pathlib import Path
                matrix_file = Path(__file__).parent.parent.parent / "data" / "gate_matrix.json"
                mat_data = {}
                if matrix_file.exists():
                    try:
                        import json as _json
                        mat_data = _json.loads(matrix_file.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                
                # Check if weekend session
                is_weekend = False
                try:
                    from core.shared.session_manager import TradingSessionManager
                    session_params = TradingSessionManager.get_active_session_params()
                    is_weekend = session_params.get("session_name") == "WEEKEND"
                except Exception:
                    pass
                
                # Calculate price velocity proxy
                closes = [float(k[4]) for k in klines] if 'klines' in locals() and klines else []
                price_velocity = (closes[-1] - closes[-2]) / closes[-2] if len(closes) >= 2 else 0.0
                
                # Calculate NIC score proxy
                nic_score = 0.0
                try:
                    from core.confluence.engine import NICAnalyst
                    nic_analyst = NICAnalyst()
                    nic_score = nic_analyst.analyze(price_velocity)
                except Exception:
                    pass
                
                mat_data["WEEKEND"] = is_weekend
                assets_data = mat_data.setdefault("assets", {})
                assets_data[self.asset.upper()] = {
                    "rsi": round(rsi, 1) if rsi is not None else 50.0,
                    "cvd": round(fast_cvd, 2) if fast_cvd is not None else 0.0,
                    "obi": round(binance_obi, 2) if binance_obi is not None else 0.0,
                    "nic": round(nic_score, 2),
                    "score": 0.0,
                    "status": "NEUTRAL"
                }
                
                matrix_file.parent.mkdir(parents=True, exist_ok=True)
                import json as _json
                matrix_file.write_text(_json.dumps(mat_data, indent=2), encoding="utf-8")
            except Exception as me:
                log.warning("Failed to write initial gate matrix: %s", me)

            # Raw direction from the shared signal core
            def make_neutral_signal(reason="no_signal"):
                return {
                    "asset": self.asset,
                    "timeframe": self.timeframe,
                    "direction": "NEUTRAL",
                    "score": 0.0,
                    "regime": regime,
                    "inverted": self.invert_signal,
                    "rsi": rsi,
                    "momentum": round(mom, 4) if mom is not None else 0.0,
                    "ofi": ofi if ofi is not None else 0.0,
                    "fast_cvd": fast_cvd if fast_cvd is not None else 0.0,
                    "slow_cvd": slow_cvd if slow_cvd is not None else 0.0,
                    "binance_obi": binance_obi if binance_obi is not None else 0.0,
                    "market": market if market is not None else {},
                    "is_dual_eligible": is_dual_eligible if 'is_dual_eligible' in locals() else False,
                    "edge_context": self.last_edge_context or {},
                    "entry_source": "SIG",
                    "corroboration_multiplier": 1.0,
                    "fv_confidence": 0.0,
                    "fv_archetype": "moderate",
                    "whale_aligned": True,
                    "confluence_score": 2,
                    "skip_reason": reason,
                }

            from core.engine.signal_core import decide_signal
            _dec = decide_signal(
                rsi,
                mom,
                ofi,
                self.timeframe,
                regime=regime,
                trend_up_agreement=trend_up_agreement,
                trend_dn_agreement=trend_dn_agreement,
                use_session_scaling=True,
                atr_percentile=_atr_pct,
                bbw_percentile=_bbw_pct,
                fast_cvd=fast_cvd,
                binance_obi=binance_obi,
            )
            raw_dir = _dec["direction"]
            score_base = _dec["score"]

            if _dec["blocked"]:
                log.info("[ENGINE] %s/%s: Spot OFI divergence — blocking entry.", self.asset, self.timeframe)
                return make_neutral_signal(reason=_dec.get("reason", "spot_ofi_divergence"))
            if _dec["is_reversal"]:
                log.warning("[REVERSAL] %s/%s RSI=%.2f reversal-snipe %s.", self.asset, self.timeframe, rsi, raw_dir)
            elif raw_dir is None:
                log.debug("[ENGINE] %s/%s: RSI=%.2f Mom=%.4f -> NEUTRAL (dual-only path).", self.asset, self.timeframe, rsi, mom)

            if _dec["is_reversal"]:
                # Reversal-snipe gets priority in non-FV
                entry_source = "REVERSAL_SNIPE"  # distinct label so confluence veto is bypassed
                _corroboration_multiplier = 1.0
                direction = apply_regime(raw_dir, regime, is_momentum=False)  # reversal — already contrarian
                if self.invert_signal:
                    direction = "DOWN" if direction == "UP" else "UP"
            else:
                entry_source = "SIG"
                _corroboration_multiplier = 1.0

                if raw_dir is None:
                    if is_dual_eligible and abs(ofi) >= 0.12:
                        raw_dir = "UP" if ofi >= 0 else "DOWN"
                        score_base = 0.62
                        log.info(
                            "[ENGINE] %s/%s: Dual-eligible (sum=%.4f) neutral RSI — OFI → %s",
                            self.asset, self.timeframe, (up_price + dn_price), raw_dir,
                        )
                    else:
                        return make_neutral_signal(reason=_dec.get("reason", "neutral_rsi"))

                # Apply regime (fade weak momentum in mean-reversion; follow strong trends)
                direction = apply_regime(raw_dir, regime, mom=mom)
                if self.invert_signal:
                    direction = "DOWN" if direction == "UP" else "UP"

                # ── Weekend Veto and Flow Alignment (Flip-to-Flow) ──
                is_weekend = False
                try:
                    from config import SKIP_WEEKEND_SIGNAL
                except ImportError:
                    SKIP_WEEKEND_SIGNAL = True

                import sys, os
                is_testing = os.environ.get("ZISI_TESTING") == "True" or "unittest" in sys.modules or "pytest" in sys.modules

                if not is_testing and SKIP_WEEKEND_SIGNAL:
                    try:
                        from core.shared.session_manager import TradingSessionManager
                        session_params = TradingSessionManager.get_active_session_params()
                        is_weekend = session_params.get("session_name") == "WEEKEND"
                    except Exception as e:
                        log.warning("[ENGINE] Failed to check weekend session: %s", e)

                if is_weekend:
                    if score_base < 0.82:
                        log.info("[WEEKEND-VETO] %s/%s: weekend SIG score %.2f < 0.82 — skip", self.asset, self.timeframe, score_base)
                        return make_neutral_signal()
                    else:
                        log.info("[WEEKEND-SIG-HIGH] %s/%s: weekend SIG score %.2f >= 0.82 — check confirmation", self.asset, self.timeframe, score_base)

                # Order Flow Alignment & Confluence Framework (Step 5)
                import sys, os
                is_testing = os.environ.get("ZISI_TESTING") == "True" or any("unittest" in a or "pytest" in a for a in sys.argv)
                if is_testing:
                    log.info("[TEST-CONTEXT] Bypassing order flow gate for %s/%s", self.asset, self.timeframe)
                else:
                    from core.engine.spot_websocket_ingest import get_cvd_metrics, get_binance_obi, _has_cvd_data
                    has_cvd = _has_cvd_data(self.asset)
                    if has_cvd:
                        fast_cvd, slow_cvd = await get_cvd_metrics(self.asset)
                        binance_obi = await get_binance_obi(self.asset)
                    else:
                        # CVD not yet warmed (common at startup for new assets like HYPE).
                        # Still run confluence with zeroed flow data — RSI, momentum, NIC
                        # and OBI signals still provide meaningful filtering.
                        fast_cvd, slow_cvd, binance_obi = 0.0, 0.0, 0.0
                        log.debug(
                            "[SIG-FLOW] %s/%s: CVD not yet warmed — running confluence with zeroed flow data",
                            self.asset, self.timeframe
                        )

                    # Step 5: Confluence Framework — runs for ALL assets, CVD-warmed or not
                    try:
                        from core.confluence.engine import confluence_risk_manager
                        price_velocity = (closes[-1] - closes[-2]) / closes[-2] if len(closes) >= 2 else 0.0
                        reg_mode = "TRENDING" if regime == "TREND" else "MEAN_REVERTING"

                        conf_res = confluence_risk_manager.evaluate(
                            rsi=rsi,
                            mom=mom,
                            fast_cvd=fast_cvd if fast_cvd is not None else 0.0,
                            slow_cvd=slow_cvd if slow_cvd is not None else 0.0,
                            binance_obi=binance_obi if binance_obi is not None else 0.0,
                            price_velocity=price_velocity,
                            regime=reg_mode,
                            is_weekend=is_weekend
                        )

                        direction = conf_res["direction"]
                        raw_dir = direction

                        # Adjust score base based on confluence decision
                        if conf_res["decision"] == "CONFIRM":
                            score_base = min(1.0, score_base + 0.10)
                        elif conf_res["decision"] in ("INVERT", "FADE"):
                            score_base = min(0.90, 0.50 + abs(conf_res["flow_pressure"]) * 0.35)

                        log.debug(
                            "[CONFLUENCE] %s/%s: rsi=%.1f mom=%.3f flow_pressure=%.2f cvd=%.2f obi=%.2f nic=%.2f | decision=%s path=%s%s",
                            self.asset, self.timeframe, rsi, mom, conf_res["flow_pressure"],
                            conf_res["cvd_score"], conf_res["obi_score"], conf_res["nic_score"],
                            conf_res["decision"], conf_res["decision_path"],
                            " [no-cvd]" if not has_cvd else ""
                        )

                        try:
                            from pathlib import Path
                            matrix_file = Path(__file__).parent.parent.parent / "data" / "gate_matrix.json"
                            mat_data = {}
                            if matrix_file.exists():
                                try:
                                    import json as _json
                                    mat_data = _json.loads(matrix_file.read_text(encoding="utf-8"))
                                except Exception:
                                    pass

                            mat_data["WEEKEND"] = is_weekend
                            assets_data = mat_data.setdefault("assets", {})
                            assets_data[self.asset.upper()] = {
                                "rsi": round(rsi, 1),
                                "cvd": round(conf_res["cvd_score"], 2),
                                "obi": round(conf_res["obi_score"], 2),
                                "nic": round(conf_res["nic_score"], 2),
                                "score": round(score_base, 2),
                                "status": conf_res["decision"] if direction != "NEUTRAL" else "NEUTRAL",
                                "cvd_warmed": has_cvd,
                            }

                            matrix_file.parent.mkdir(parents=True, exist_ok=True)
                            import json as _json
                            matrix_file.write_text(_json.dumps(mat_data, indent=2), encoding="utf-8")
                        except Exception as me:
                            log.warning("Failed to write gate matrix: %s", me)

                    except Exception as e:
                        log.error("[CONFLUENCE-ERR] Failed to evaluate Confluence: %s", e)

                    # -------------------------------------------------------
                    # BTC Market Leadership Anchor (Item 25)
                    # -------------------------------------------------------
                    try:
                        if self.asset.upper() == "BTC":
                            # BTC updates the shared anchor after each confluence eval
                            _BTC_ANCHOR["direction"] = direction
                            _BTC_ANCHOR["score"]     = score_base
                            _BTC_ANCHOR["cvd_fast"]  = fast_cvd if fast_cvd is not None else 0.0
                            _BTC_ANCHOR["ts"]        = time.time()
                            log.debug(
                                "[BTC-ANCHOR] BTC anchor updated: dir=%s score=%.2f cvd_fast=%.1f",
                                direction, score_base, _BTC_ANCHOR["cvd_fast"]
                            )
                        else:
                            # Non-BTC: check if BTC anchor is fresh + decisive
                            anchor_age = time.time() - _BTC_ANCHOR["ts"]
                            btc_dir    = _BTC_ANCHOR["direction"]
                            btc_score  = _BTC_ANCHOR["score"]
                            if (
                                btc_dir is not None
                                and btc_dir not in ("NEUTRAL", None)
                                and btc_score >= _BTC_ANCHOR_MIN_SCORE
                                and anchor_age <= _BTC_ANCHOR_MAX_AGE
                                and direction not in ("NEUTRAL", None)
                                and direction != btc_dir
                            ):
                                log.info(
                                    "[BTC-ANCHOR] %s/%s: flipping direction %s → %s "
                                    "(BTC anchor: dir=%s score=%.2f cvd=%.1f age=%.0fs)",
                                    self.asset, self.timeframe, direction, btc_dir,
                                    btc_dir, btc_score, _BTC_ANCHOR["cvd_fast"], anchor_age
                                )
                                direction = btc_dir
                            elif btc_dir is not None and anchor_age <= _BTC_ANCHOR_MAX_AGE:
                                log.debug(
                                    "[BTC-ANCHOR] %s/%s: aligned dir=%s btc=%s score=%.2f age=%.0fs",
                                    self.asset, self.timeframe, direction, btc_dir, btc_score, anchor_age
                                )
                    except Exception as _anc_e:
                        log.warning("[BTC-ANCHOR] Failed to apply anchor: %s", _anc_e)


        # Composite score
        # FV Score Isolation (Tier 1): FV signals have their own confidence model.
        # Applying raw momentum/OFI boosts inflates the FV score and inverts sizing
        # (small-edge FV bets become over-sized relative to their actual conviction).
        # FV sizing is driven by fv_confidence, not composite score — skip boosts for FV.
        abs_mom = abs(mom)
        score = score_base
        if not is_fv_trade:
            if abs_mom >= 0.15:
                score = min(1.0, score + 0.20)
            elif abs_mom >= 0.08:
                score = min(1.0, score + 0.15)
            elif abs_mom >= 0.05:
                score = min(1.0, score + 0.10)

            if raw_dir == "UP" and ofi > 0.20:
                score = min(1.0, score + 0.08)
            elif raw_dir == "DOWN" and ofi < -0.20:
                score = min(1.0, score + 0.08)

            if is_dual_eligible:
                score = min(1.0, score + 0.06)
                log.info(
                    "[ENGINE] %s/%s: Dual boost — combined=%.4f",
                    self.asset, self.timeframe, up_price + dn_price,
                )

        # Polymarket CLOB OBI (Proposal 1)
        clob_obi = 0.0
        try:
            from core.engine.extraterrestrial_ws_gateway import polymarket_l2_gateway
            up_tk = market.get("up_market", {}).get("id")
            dn_tk = market.get("dn_market", {}).get("id")
            if direction == "UP" and up_tk:
                clob_obi = polymarket_l2_gateway.get_obi(up_tk)
                if clob_obi < -0.60:
                    score = max(0.10, score - 0.10)
                    log.info("[ENGINE] %s/%s: Polymarket %s OBI extreme selling pressure (%.2f < -0.60) — penalty -0.10",
                             self.asset, self.timeframe, _GREEN_YES, clob_obi)
                elif clob_obi > 0.0:
                    score = min(1.0, score + 0.04)
                    log.info("[ENGINE] %s/%s: %s OBI confirms direction (%.2f > 0.0) -> boost +0.04", self.asset, self.timeframe, _GREEN_YES, clob_obi)
                elif clob_obi < 0.0:
                    score = max(0.10, score - 0.03)
                    log.info("[ENGINE] %s/%s: %s OBI conflicts direction (%.2f < 0.0) -> penalty -0.03", self.asset, self.timeframe, _GREEN_YES, clob_obi)
            elif direction == "DOWN" and dn_tk:
                clob_obi = polymarket_l2_gateway.get_obi(dn_tk)
                if clob_obi < -0.60:
                    score = max(0.10, score - 0.10)
                    log.info("[ENGINE] %s/%s: Polymarket %s OBI extreme selling pressure (%.2f < -0.60) — penalty -0.10",
                             self.asset, self.timeframe, _RED_NO, clob_obi)
                elif clob_obi > 0.0:
                    score = min(1.0, score + 0.04)
                    log.info("[ENGINE] %s/%s: %s OBI confirms direction (%.2f > 0.0) -> boost +0.04", self.asset, self.timeframe, _RED_NO, clob_obi)
                elif clob_obi < 0.0:
                    score = max(0.10, score - 0.03)
                    log.info("[ENGINE] %s/%s: %s OBI conflicts direction (%.2f < 0.0) -> penalty -0.03", self.asset, self.timeframe, _RED_NO, clob_obi)
        except Exception as e:
            log.warning("[ENGINE] Failed to read or apply Polymarket CLOB OBI: %s", e)



        # ── Edge Architecture Integration (Advancements A-M) ──
        edge_ctx = {}
        try:
            from core.engine.edge_orchestrator import edge_orchestrator
            sig_dict = {
                "signal_type": "TYPE_A_HIGH" if (score >= 0.75) else "TYPE_A_LOW",
                "score": score,
                "affected_cryptos": [self.asset],
                "entry_price": up_price if direction == "UP" else dn_price,
            }
            edge_ctx = await edge_orchestrator.get_trade_context(
                session=session,
                asset=self.asset,
                direction=direction,
                signal=sig_dict,
                market=market,
                current_price=closes[-1]
            )
            self.last_edge_context = edge_ctx
            
            boost = edge_ctx.get("combined_confidence_boost", 0.0)
            if boost != 0.0:
                old_score = score
                score = max(0.10, min(1.0, score + boost))
                log.debug("[EDGE] %s/%s Score adjusted by boost: %.2f -> %.2f (boost=%+.2f)", self.asset, self.timeframe, old_score, score, boost)
            
            regime = edge_ctx.get("regime_name", regime)
            
        except Exception as e:
            log.warning("[EDGE] Failed to query EdgeOrchestrator in generate_signal: %s", e)
            self.last_edge_context = None

        # Whale-Veto: REMOVED — directional accuracy > protective layers.
        # Corroboration amplifies wins and losses equally; fix the signal, not the gate.

        # Confluence-Veto Gate: REMOVED to emulate Friday June 5th state
        # if entry_source != "FAIR_VAL" and not is_dual_eligible and edge_ctx and edge_ctx.get("confluence_score", 2) == 0:
        #     log.warning(
        #         "[CONFLUENCE-VETO] %s/%s: Blocking directional entry due to complete lack of multi-timeframe agreement (score = 0)",
        #         self.asset, self.timeframe
        #     )
        #     return None

        if score < 0.55 and not is_dual_eligible:
            return make_neutral_signal(reason=f"score={score:.2f} < threshold=0.55")





        log.debug(
            "[ENGINE] %s/%s SIGNAL: %s | Score=%.2f | up=%.4f dn=%.4f | dual=%s | %s",
            self.asset, self.timeframe, direction, score,
            up_price, dn_price, is_dual_eligible, market["event_title"],
        )

        # Add whale alignment and confluence to signal for downstream gates
        if self.last_edge_context:
            ec = self.last_edge_context
            whale_pressure = ec.get('whale_pressure', 0.0)
            # whale_pressure > 0 means bullish, < 0 means bearish
            whale_is_up = whale_pressure >= 0.0
            _whale_aligned = (whale_is_up == (direction == 'UP'))
            _confluence_score = ec.get('confluence_score', 0)
        else:
            _whale_aligned = True   # default allow if no edge context
            _confluence_score = 2   # default allow

        import sys, os as _os_t
        is_testing = _os_t.environ.get("ZISI_TESTING") == "True" or "unittest" in sys.modules or "pytest" in sys.modules
        if not is_testing:
            import time as _time_ttl
            _ttl_s = market.get("expiry_ts", 0) - _time_ttl.time()
            _min_ttl = 600 if self.timeframe == "1h" else (180 if self.timeframe == "15m" else 90)
            if _ttl_s < _min_ttl:
                log.info("[TTL-GATE] %s/%s: %.0fs to expiry — too late to enter (need %ds+), skip",
                         self.asset, self.timeframe, _ttl_s, _min_ttl)
                return make_neutral_signal(reason="ttl_gate")

        _strike_price = None
        try:
            if FAIR_VALUE_MODE:
                _strike_price = _custom_strike
        except Exception:
            pass
        if _strike_price is None and len(klines) > 0:
            _strike_price = float(klines[-1][1])

        return {
            "asset":        self.asset,
            "timeframe":    self.timeframe,
            "direction":    direction,
            "score":        score,
            "regime":       regime,
            "inverted":     self.invert_signal,
            "rsi":          rsi,
            "momentum":     round(mom, 4),
            "market":       market,
            "is_dual_eligible": is_dual_eligible,
            "edge_context": edge_ctx,
            "entry_source": entry_source,
            "corroboration_multiplier": _corroboration_multiplier,
            "fv_confidence": _fv_confidence,
            "fv_archetype": _fv_archetype,
            "whale_aligned": _whale_aligned,
            "confluence_score": _confluence_score,
            "fast_cvd":     fast_cvd,
            "slow_cvd":     slow_cvd,
            "binance_obi":  binance_obi,
            "skip_reason":  (conf_res.get("decision_path") if (direction == "NEUTRAL" and 'conf_res' in locals()) else "confirm"),
            "strike_price": _strike_price,
        }


    async def _resolve_l2_prices(
        self,
        session: aiohttp.ClientSession,
        up_tk: str,
        dn_tk: str,
        max_spread: float = 0.35,
        is_latency_scan: bool = False,
    ) -> Optional[tuple[float, float, float]]:
        """Return (up_price, dn_price, spread) or None if book invalid."""
        from core.engine.extraterrestrial_ws_gateway import polymarket_l2_gateway
        from config import get_config

        if not polymarket_l2_gateway.is_active:
            polymarket_l2_gateway.start_gateway()

        polymarket_l2_gateway.subscribe(up_tk)
        polymarket_l2_gateway.subscribe(dn_tk)

        # Re-enable strict spread limit (15c) to protect capital on illiquid books
        effective_max_spread = max_spread

        up_price, dn_price = None, None
        attempts = 2 if is_latency_scan else 4
        for attempt in range(attempts):
            up_price, up_spread = polymarket_l2_gateway.get_price(up_tk)
            dn_price, dn_spread = polymarket_l2_gateway.get_price(dn_tk)
            
            # Widen price ceiling and floor to accept all valid prices
            _price_ceil = 0.999
            _price_floor = 0.001

            # 1. If we have both prices, verify and use them
            if up_price and dn_price and _price_floor < up_price < _price_ceil and _price_floor < dn_price < _price_ceil:
                spread = (up_spread or 0.02) + (dn_spread or 0.02)
                if spread <= effective_max_spread:
                    return up_price, dn_price, spread

            # 2. Derive DOWN price if only UP exists and is valid
            if up_price and _price_floor < up_price < _price_ceil and (not dn_price or dn_price <= _price_floor or dn_price >= _price_ceil):
                derived_dn = round(1.0 - up_price, 4)
                spread = (up_spread or 0.02) + 0.02
                if spread <= effective_max_spread:
                    return up_price, derived_dn, spread

            # 3. Derive UP price if only DOWN exists and is valid
            if dn_price and _price_floor < dn_price < _price_ceil and (not up_price or up_price <= _price_floor or up_price >= _price_ceil):
                derived_up = round(1.0 - dn_price, 4)
                spread = (dn_spread or 0.02) + 0.02
                if spread <= effective_max_spread:
                    return derived_up, dn_price, spread

            # Only sleep if we have remaining attempts and didn't resolve
            if attempt < attempts - 1:
                await asyncio.sleep(0.5 if is_latency_scan else (1.0 if attempt == 0 else 1.5))

        # Single REST fallback check executed exactly once if all WebSocket attempts failed
        up_book = await _fetch_clob_book_async(session, up_tk)
        dn_book = await _fetch_clob_book_async(session, dn_tk)
        up_p, up_s = _parse_clob_book(up_book)
        dn_p, dn_s = _parse_clob_book(dn_book)
        
        _price_ceil = 0.999
        _price_floor = 0.001

        # REST 1. Both valid
        if up_p and dn_p and _price_floor < up_p < _price_ceil and _price_floor < dn_p < _price_ceil:
            spread = (up_s or 0.03) + (dn_s or 0.03)
            if spread <= effective_max_spread:
                return up_p, dn_p, spread
        
        # REST 2. Derive REST DOWN from REST UP
        if up_p and _price_floor < up_p < _price_ceil and (not dn_p or dn_p <= _price_floor or dn_p >= _price_ceil):
            derived_dn = round(1.0 - up_p, 4)
            spread = (up_s or 0.03) + 0.03
            if spread <= effective_max_spread:
                return up_p, derived_dn, spread
                
        # REST 3. Derive REST UP from REST DOWN
        if dn_p and _price_floor < dn_p < _price_ceil and (not up_p or up_p <= _price_floor or up_p >= _price_ceil):
            derived_up = round(1.0 - dn_p, 4)
            spread = (dn_s or 0.03) + 0.03
            if spread <= effective_max_spread:
                return derived_up, dn_p, spread

        # No live L2 book and REST fallback also failed. Return None (no fake fallbacks).
        log.debug(
            "[LIVE-BOOK] %s/%s: No valid L2 book (WS+REST failed) — skipping candle.",
            self.asset, self.timeframe,
        )
        return None

    async def prefetch_upcoming_market(self, session: aiohttp.ClientSession, next_boundary: int) -> None:
        """Prefetch token IDs for the upcoming market 20s before start and warm WebSocket."""
        coin_lower = self.asset.lower()
        dur_min = 60 if self.timeframe == "1h" else (5 if self.timeframe == "5m" else 15)
        slug_ts = next_boundary
        if self.timeframe == "1h":
            slug = self._get_hourly_slug(slug_ts)
        else:
            slug = f"{coin_lower}-updown-{dur_min}m-{slug_ts}"
        
        gamma_url = "https://gamma-api.polymarket.com/events"
        try:
            log.debug("[ENGINE] %s/%s: Pre-fetching upcoming market slug: %s", self.asset, self.timeframe, slug)
            async with session.get(gamma_url, params={"slug": slug}, timeout=5) as r:
                if r.status == 200:
                    raw = await r.json()
                    evs = []
                    if isinstance(raw, dict) and "id" in raw:
                        evs = [raw]
                    elif isinstance(raw, list):
                        evs = raw
                    else:
                        evs = raw.get("data", raw.get("events", []))

                    for ev in evs:
                        if ev.get("slug") != slug:
                            continue
                        for mkt in ev.get("markets", []):
                            import json as _json
                            outcomes = mkt.get("outcomes", [])
                            if isinstance(outcomes, str):
                                try:
                                    outcomes = _json.loads(outcomes)
                                except Exception:
                                    outcomes = []
                            clob_token_ids = mkt.get("clobTokenIds", [])
                            if isinstance(clob_token_ids, str):
                                try:
                                    clob_token_ids = _json.loads(clob_token_ids)
                                except Exception:
                                    clob_token_ids = []

                            if len(outcomes) < 2 or len(clob_token_ids) < 2:
                                continue

                            up_idx, dn_idx = -1, -1
                            for i, o in enumerate(outcomes):
                                o_lower = str(o).lower()
                                if o_lower in ("yes", "up"):
                                    up_idx = i
                                elif o_lower in ("no", "down"):
                                    dn_idx = i

                            if up_idx == -1 or dn_idx == -1:
                                continue

                            up_tk = clob_token_ids[up_idx]
                            dn_tk = clob_token_ids[dn_idx]
                            
                            # Warm the WebSocket cache!
                            from core.engine.extraterrestrial_ws_gateway import polymarket_l2_gateway
                            if not polymarket_l2_gateway.is_active:
                                polymarket_l2_gateway.start_gateway()
                            polymarket_l2_gateway.subscribe(up_tk)
                            polymarket_l2_gateway.subscribe(dn_tk)
                            
                            is_new = next_boundary not in self._prefetched_markets
                            self._prefetched_markets[next_boundary] = {
                                "event_id": ev.get("id", ""),
                                "event_title": ev.get("title", ""),
                                "expiry_ts": next_boundary + (dur_min * 60),
                                "duration_min": dur_min,
                                "liquidity": float(ev.get("liquidity", 0) or 1000.0),
                                "up_market": {"id": up_tk},
                                "dn_market": {"id": dn_tk},
                                "slug": slug,
                            }
                            # Prune cache to keep only recent entries (older than 1 hour)
                            now_ts = int(time.time())
                            self._prefetched_markets = {
                                k: v for k, v in self._prefetched_markets.items()
                                if k > now_ts - 3600
                            }
                            if is_new:
                                log.debug(
                                    "[ENGINE] %s/%s: Upcoming market pre-fetched & WS subscribed! Yes=%s No=%s",
                                    self.asset, self.timeframe, up_tk[:10], dn_tk[:10]
                                )
                            return
        except Exception as e:
            log.warning("[ENGINE] Failed to pre-fetch upcoming market %s: %s", slug, e)

    async def _get_oracle_fallback_prices(self, up_tk: str, dn_tk: str) -> Optional[tuple[float, float, float]]:
        """
        Integrate Chainlink (Primary) and Binance Spot (Secondary) oracle fallback.
        If L2 order book sync fails, return fallback taker prices.
        """
        # Primary: Chainlink
        try:
            from core.engine.polymarket_rtds_ingest import get_chainlink_price
            cl_details = await get_chainlink_price(self.asset)
            if cl_details:
                spot, ts = cl_details
                if time.time() - ts <= 10.0:
                    log.info("[ORACLE-FALLBACK] %s: Using Chainlink price %.2f", self.asset, spot)
                    return 0.50, 0.50, 0.05
        except Exception as e:
            log.warning("[ORACLE-FALLBACK] Chainlink lookup failed: %s", e)
        
        log.info("[ORACLE-FALLBACK] %s: No live Chainlink oracle found, skipping fallback", self.asset)
        return None

    async def _fetch_market(self, session: aiohttp.ClientSession, is_latency_scan: bool = False) -> Optional[dict]:
        """Fetch active Up/Down market with verified L2/REST pricing and oracle fallback, retry for 5 seconds."""
        coin_lower = self.asset.lower()
        dur_min = 60 if self.timeframe == "1h" else (5 if self.timeframe == "5m" else 15)
        now_ts = int(time.time())
        interval = dur_min * 60
        boundary = ((now_ts + interval) // interval) * interval
        start_ts = boundary - interval
        offsets = [0, -1, 1]

        # Wait up to 3 seconds (3 poll attempts) for the new market to be created / resolved
        for poll_attempt in range(3):
            # Check pre-fetched first
            if start_ts in self._prefetched_markets:
                cached_market = self._prefetched_markets[start_ts]
                up_tk = cached_market["up_market"]["id"]
                dn_tk = cached_market["dn_market"]["id"]
                resolved = await self._resolve_l2_prices(session, up_tk, dn_tk, is_latency_scan=is_latency_scan)
                if resolved:
                    up_price, dn_price, spread = resolved
                    market = dict(cached_market)
                    market["up_price"] = up_price
                    market["dn_price"] = dn_price
                    market["spread"] = spread
                    log.debug(
                        "[ENGINE] %s/%s: [PRE-FETCH HIT] %s up=%.4f dn=%.4f spread=%.4f (poll=%d)",
                        self.asset, self.timeframe, market["slug"],
                        up_price, dn_price, spread, poll_attempt
                    )
                    return market
                else:
                    if poll_attempt == 2:
                        # Register this asset/timeframe as illiquid for this poll attempt/candle
                        _illiquid_key = (start_ts, poll_attempt)
                        if _illiquid_key not in _ILLIQUID_BOOKS_ASSETS:
                            _ILLIQUID_BOOKS_ASSETS[_illiquid_key] = []
                        _ILLIQUID_BOOKS_ASSETS[_illiquid_key].append(f"{self.asset}/{self.timeframe}")
                        
                        # Wait a short stagger (50ms) for other concurrent engine instances to register
                        await asyncio.sleep(0.05)
                        
                        # Only the first engine registration will print the aggregated warning log
                        if _illiquid_key in _ILLIQUID_BOOKS_ASSETS and f"{self.asset}/{self.timeframe}" == _ILLIQUID_BOOKS_ASSETS[_illiquid_key][0]:
                            if _illiquid_key not in _ILLIQUID_BOOKS_LOGGED:
                                _ILLIQUID_BOOKS_LOGGED.add(_illiquid_key)
                                _assets_str = ", ".join(_ILLIQUID_BOOKS_ASSETS[_illiquid_key])
                                log.warning("[ENGINE] L2 book is illiquid, empty, or not yet initialized (spread > 15c) for: %s — skipping trade", _assets_str)

                        # Periodic cleanup to prevent growth
                        if len(_ILLIQUID_BOOKS_ASSETS) > 50:
                            for k in list(_ILLIQUID_BOOKS_ASSETS.keys())[:-10]:
                                _ILLIQUID_BOOKS_ASSETS.pop(k, None)
                                _ILLIQUID_BOOKS_LOGGED.discard(k)

                        return None
                    else:
                        await asyncio.sleep(1.0)
                        continue

            gamma_url = "https://gamma-api.polymarket.com/events"

            try:
                for offset in offsets:
                    offset_ts = start_ts + (offset * interval)
                    expiry_ts = offset_ts + interval
                    if expiry_ts <= now_ts:
                        continue
                    if self.timeframe == "1h":
                        slug = self._get_hourly_slug(offset_ts)
                    else:
                        slug = f"{coin_lower}-updown-{dur_min}m-{offset_ts}"

                    async with session.get(gamma_url, params={"slug": slug}, timeout=5) as r:
                        if r.status != 200:
                            continue
                        raw = await r.json()
                        evs = []
                        if isinstance(raw, dict) and "id" in raw:
                            evs = [raw]
                        elif isinstance(raw, list):
                            evs = raw
                        else:
                            evs = raw.get("data", raw.get("events", []))

                        for ev in evs:
                            if ev.get("slug") != slug:
                                continue
                            for mkt in ev.get("markets", []):
                                import json as _json
                                outcomes = mkt.get("outcomes", [])
                                if isinstance(outcomes, str):
                                    try: outcomes = _json.loads(outcomes)
                                    except Exception: outcomes = []
                                clob_token_ids = mkt.get("clobTokenIds", [])
                                if isinstance(clob_token_ids, str):
                                    try: clob_token_ids = _json.loads(clob_token_ids)
                                    except Exception: clob_token_ids = []

                                if len(outcomes) < 2 or len(clob_token_ids) < 2:
                                    continue

                                up_idx, dn_idx = -1, -1
                                for i, o in enumerate(outcomes):
                                    o_lower = str(o).lower()
                                    if o_lower in ("yes", "up"): up_idx = i
                                    elif o_lower in ("no", "down"): dn_idx = i

                                if up_idx == -1 or dn_idx == -1:
                                    continue

                                up_tk = clob_token_ids[up_idx]
                                dn_tk = clob_token_ids[dn_idx]
                                resolved = await self._resolve_l2_prices(session, up_tk, dn_tk, is_latency_scan=is_latency_scan)
                                if not resolved and False:
                                    # Fallback 1: Try Gamma API outcomePrices
                                    outcome_prices = mkt.get("outcomePrices", [])
                                    if isinstance(outcome_prices, str):
                                        try: outcome_prices = _json.loads(outcome_prices)
                                        except Exception: outcome_prices = []
                                    if len(outcome_prices) > max(up_idx, dn_idx):
                                        try:
                                            up_p = float(outcome_prices[up_idx])
                                            dn_p = float(outcome_prices[dn_idx])
                                            if 0.01 <= up_p <= 0.99 and 0.01 <= dn_p <= 0.99:
                                                resolved = (up_p, dn_p, 0.02)
                                                log.info(
                                                    "[ENGINE] %s/%s: L2 book fetch failed, fell back to Gamma API outcomePrices (up=%.4f, dn=%.4f)",
                                                    self.asset, self.timeframe, up_p, dn_p
                                                )
                                        except Exception as gamma_err:
                                            log.debug("[ENGINE] Failed to parse Gamma outcomePrices: %s", gamma_err)
                                if resolved:
                                    up_price, dn_price, spread = resolved
                                    log.debug(
                                        "[ENGINE] %s/%s: %s up=%.4f dn=%.4f spread=%.4f (poll=%d)",
                                        self.asset, self.timeframe, slug,
                                        up_price, dn_price, spread, poll_attempt
                                    )
                                    return {
                                        "event_id": ev.get("id", ""),
                                        "event_title": ev.get("title", ""),
                                        "expiry_ts": offset_ts + interval,
                                        "duration_min": dur_min,
                                        "up_price": up_price,
                                        "dn_price": dn_price,
                                        "spread": spread,
                                        "up_market": {"id": up_tk},
                                        "dn_market": {"id": dn_tk},
                                    }
            except Exception as exc:
                log.warning("[ENGINE] CLOB L2 market fetch error: %s", exc)

            # Register this asset/timeframe as waiting for this poll attempt
            _poll_key = (start_ts, poll_attempt)
            if _poll_key not in _WAITING_POLLS_ASSETS:
                _WAITING_POLLS_ASSETS[_poll_key] = []
            _WAITING_POLLS_ASSETS[_poll_key].append(f"{self.asset}/{self.timeframe}")
            
            # Wait a short stagger (50ms) for other concurrent engine instances to register
            await asyncio.sleep(0.05)
            
            # Only the first engine registration will print the aggregated log
            if _poll_key in _WAITING_POLLS_ASSETS and f"{self.asset}/{self.timeframe}" == _WAITING_POLLS_ASSETS[_poll_key][0]:
                if _poll_key not in _WAITING_POLLS_LOGGED:
                    _WAITING_POLLS_LOGGED.add(_poll_key)
                    _assets_str = ", ".join(_WAITING_POLLS_ASSETS[_poll_key])
                    log.info("[ENGINE] No active Polymarket contract found for: %s (attempt %d/2)", _assets_str, poll_attempt+1)

            # Periodic cleanup to prevent growth
            if len(_WAITING_POLLS_ASSETS) > 50:
                for k in list(_WAITING_POLLS_ASSETS.keys())[:-10]:
                    _WAITING_POLLS_ASSETS.pop(k, None)
                    _WAITING_POLLS_LOGGED.discard(k)

            await asyncio.sleep(0.10)

        return None


    # ── Sizing ────────────────────────────────────────────────────────────────

    def compute_size(self, score: float, price: float, balance: float, confidence: float = None) -> float:
        """Return USD amount to bet, sized by directional CONFIDENCE (Dynamic Kelly) scaled by regime and asset weight."""
        # Determine the balance to size against (Sprint 12 user-controlled baseline setting)
        # Cap at SIZING_BALANCE if defined to prevent over-sizing, but support smaller balances in tests
        sizing_balance = min(balance, SIZING_BALANCE) if SIZING_BALANCE is not None else balance

        # ── Edge Architecture Adaptive Kelly Sizer (Advancement D) ──
        if getattr(self, "last_edge_context", None):
            try:
                from core.risk.position_sizer import PositionSizer
                sizer = PositionSizer(account_balance=sizing_balance, max_cycle_capital=sizing_balance)
                
                sig_dict = {
                    "signal_type": "TYPE_A_HIGH" if (score >= 0.75) else "TYPE_A_LOW",
                    "score": score,
                    "affected_cryptos": [self.asset],
                    "entry_price": price,
                }
                mkt_dict = {
                    "market_type": "UP_DOWN",
                }
                
                ctx = self.last_edge_context
                # ── Confidence-tiered sizing (REBUILD): size by CONVICTION, not by price ──
                # Mentors bet big on a strong read regardless of entry price (PBot-6 $194@54c,
                # Rith $2,295@46c). confidence = FV directional confidence; falls back to score.
                conf = confidence if confidence is not None else score
                if conf >= 0.80:
                    _bk_frac = 0.25
                elif conf >= 0.70:
                    _bk_frac = 0.18
                elif conf >= 0.62:
                    _bk_frac = 0.10
                else:
                    _bk_frac = 0.05
                # Cheap longshots (<35c) hit ~40% — cap unless conviction is high (Rith only
                # sizes these big with a strong read); otherwise keep them small.
                if price < 0.35 and conf < 0.75:
                    _bk_frac = min(_bk_frac, 0.05)
                # Scale unified max cap dynamically with balance growth factor
                growth_factor = max(1.0, sizing_balance / 120.0)
                unified_max_cap = max(5.00 * growth_factor, min(40.00 * growth_factor, (5.00 + (conf - 0.50) * 80.0) * growth_factor))
                usd_size = sizer.calculate_adaptive(
                    signal=sig_dict,
                    market=mkt_dict,
                    regime_kelly=ctx.get("regime_kelly", 1.0),
                    confluence_boost=ctx.get("confluence_boost", 0.0),
                    antifragile_mult=ctx.get("antifragile_mult", 1.0),
                    heat_mult=ctx.get("heat_mult", 1.0),
                    sentiment_modifier=ctx.get("sentiment_modifier", 0.0),
                    whale_mult=ctx.get("whale_mult", 1.0),
                    category_weight=1.0,
                    min_position_usd=MIN_USD,
                    max_position_usd=unified_max_cap,
                    max_bankroll_fraction=_bk_frac,
                )
                
                # Retrieve and apply session sizing multiplier (Sprint 11)
                session_sizing_mult = 1.0
                try:
                    from core.shared.session_manager import TradingSessionManager
                    session_params = TradingSessionManager.get_active_session_params()
                    session_sizing_mult = session_params.get("sizing_mult", 1.0)
                    usd_size *= session_sizing_mult
                    log.debug("[SIZE] Adaptive Kelly scaled by session multiplier %.2fx -> $%.2f", session_sizing_mult, usd_size)
                except Exception as e:
                    log.warning("[SIZE] Failed to scale by session multiplier: %s", e)

                # Price-Scaled Risk Sizer calibration to bypass 70¢ trap and extreme pricing risk
                price_scalar = 1.0
                if price > 0.65 and price <= 0.78:
                    price_scalar = 0.70  # REBUILD: softened 0.40->0.70 (confidence gate handles the 70c trap)
                    log.debug("[SIZE] Price %.4f in 70c zone -> x0.70 scaling", price)
                elif price > 0.78:
                    price_scalar = 0.50  # REBUILD: softened 0.25->0.50 — mentors size near-certainty up
                    log.debug("[SIZE] Price %.4f expensive -> x0.50 scaling", price)
                usd_size *= price_scalar

                # REBUILD: removed the blanket 50-65c x0.65 haircut — confidence-tiered _bk_frac
                # above already sizes ATM by conviction (mentors bet ATM big on a strong read).

                # Consecutive Loss Streak Brake
                consecutive_losses = self._recent_closed_loss_streak()
                if consecutive_losses >= 2:
                    usd_size *= 0.5
                    log.warning(
                        "[SIZE] %s/%s loss streak brake active (%d losses) -> halving size in adaptive Kelly",
                        self.asset, self.timeframe, consecutive_losses,
                    )

                # REBUILD: BTC > ETH asset weighting — set all to 1.0 (100%) as requested
                from core.risk.position_sizer import get_tiered_sizing_caps
                min_cap, max_cap = get_tiered_sizing_caps(balance)
                usd_size = max(min_cap, min(max_cap, usd_size))

                log.debug("[SIZE] Adaptive Kelly cost $%.2f (conf=%.2f, tiered_caps: $%.2f - $%.2f)", usd_size, conf, min_cap, max_cap)
                return usd_size
            except Exception as e:
                log.warning("[SIZE] Failed to compute adaptive Kelly size, falling back: %s", e)

        # ── Legacy Sizer Fallback ──
        # Base multiplier from 1.0% to 5.0% depending on score
        if score >= 0.90:
            kelly_pct = 0.05
        elif score >= 0.80:
            kelly_pct = 0.03
        elif score >= 0.65:
            kelly_pct = 0.015
        else:
            kelly_pct = 0.01

        # Get regime multiplier from regime_status.json
        regime_mult = 1.0
        try:
            import json
            from pathlib import Path
            regime_path = Path(__file__).parent.parent.parent / "data" / "regime_status.json"
            if regime_path.exists():
                data = json.loads(regime_path.read_text(encoding="utf-8"))
                # Canonical regimes from RegimeDetector + legacy aliases for
                # backward compat with any stale regime_status.json on disk.
                REGIME_SIZE_MULT = {
                    "TRENDING":      1.30,  # directional momentum → size up
                    "COMPRESSION":   1.10,  # low-vol squeeze → slight size up
                    "MEAN_REVERTING": 0.85, # chop → size down
                    "VOLATILE_CHAOS": 0.30, # unpredictable → size way down
                    # legacy aliases
                    "RANGE":   1.30,
                    "NORMAL":  1.00,
                    "VOLATILE": 0.60,
                    "SHOCK":   0.20,
                }
                regime = str(data.get("regime", "COMPRESSION")).upper()
                regime_mult = REGIME_SIZE_MULT.get(regime, 1.0)
                log.info("[SIZE] Active regime is %s -> applying multiplier %.2fx", regime, regime_mult)
        except Exception as e:
            log.warning("[SIZE] Failed to read regime multiplier: %s", e)

        # Price-Scaled Risk Sizer calibration to bypass 70¢ trap and extreme pricing risk
        price_scalar = 1.0
        if price > 0.65 and price <= 0.78:
            price_scalar = 0.40  # 60% reduction
            log.info("[SIZE] Price %.4f in 70¢ trap -> applying 60%% scaling (x0.40)", price)
        elif price > 0.78:
            price_scalar = 0.25  # 75% reduction
            log.info("[SIZE] Price %.4f extremely expensive -> applying 75%% scaling (x0.25)", price)

        # Dynamic max cap based on AI confidence scaled with growth_factor
        growth_factor = max(1.0, sizing_balance / 120.0)
        max_usd_cap = min(20.00 * growth_factor, (5.00 + (score - 0.50) * 40.0) * growth_factor)
        max_usd_cap = max(5.00 * growth_factor, max_usd_cap)

        raw_usd = kelly_pct * sizing_balance * regime_mult * price_scalar

        # Retrieve and apply session sizing multiplier (Sprint 11)
        session_sizing_mult = 1.0
        try:
            from core.shared.session_manager import TradingSessionManager
            session_params = TradingSessionManager.get_active_session_params()
            session_sizing_mult = session_params.get("sizing_mult", 1.0)
            raw_usd *= session_sizing_mult
            log.info("[SIZE] Fallback Kelly scaled by session multiplier %.2fx -> $%.2f", session_sizing_mult, raw_usd)
        except Exception as e:
            log.warning("[SIZE] Failed to scale by session multiplier: %s", e)

        usd = max(MIN_USD, min(raw_usd, max_usd_cap))

        consecutive_losses = self._recent_closed_loss_streak()
        if consecutive_losses >= 2:
            usd *= 0.5
            log.warning(
                "[SIZE] %s/%s loss streak brake active (%d losses) -> halving size",
                self.asset, self.timeframe, consecutive_losses,
            )

        from core.risk.position_sizer import get_tiered_sizing_caps
        min_cap, max_cap = get_tiered_sizing_caps(balance)
        usd = max(min_cap, min(max_cap, usd))

        shares = round(usd / price)
        return shares * price  # actual cost from shares-first rounding

    def _recent_same_direction_streak(self, direction: str, n: int = 6) -> int:
        """Count consecutive recent closed trades in the same direction as signal."""
        try:
            import json
            from pathlib import Path
            path = Path(__file__).parent.parent.parent / "data" / "positions_state.json"
            if not path.exists():
                return 0
            data = json.loads(path.read_text(encoding="utf-8"))
            # ── PER-ASSET STREAK FIX (Bonereaper-mode) ──────────────────────────────────
            # Filter closed trades to THIS asset only before computing the streak.
            # Previously the streak was global across all assets — meaning 5 BTC DOWN wins
            # would block XRP/ETH/SOL DOWN signals even though they are independent markets.
            # Bonereaper enters each asset fresh on each candle with no cross-asset bias.
            all_closed = data.get("closed", [])
            asset_closed = [t for t in all_closed if t.get("asset", "").upper() == self.asset.upper()]
            closed = asset_closed[-n:][::-1]  # most recent n trades for THIS asset, newest first
        except Exception:
            return 0
        signal_up = direction == "UP"
        streak = 0
        for trade in closed:
            trade_dir = trade.get("direction", "")
            trade_is_up = trade_dir in ("YES", "UP")
            if trade_is_up == signal_up:
                streak += 1
            else:
                break
        return streak

    def _recent_full_loss_count(self, lookback_minutes: int = 20) -> int:
        """Count trades that settled near zero (≤10¢) within the last N minutes (cross-asset)."""
        try:
            import json, time as _time
            from pathlib import Path
            path = Path(__file__).parent.parent.parent / "data" / "positions_state.json"
            if not path.exists():
                return 0
            data = json.loads(path.read_text(encoding="utf-8"))
            cutoff = _time.time() - lookback_minutes * 60
            count = 0
            for trade in data.get("closed", []):
                exit_iso = trade.get("exit_time") or trade.get("closed_at") or ""
                try:
                    exit_ts = datetime.fromisoformat(exit_iso).timestamp() if exit_iso else 0.0
                except Exception:
                    exit_ts = float(exit_iso) if exit_iso else 0.0
                exit_price = float(trade.get("exit_price", 1.0) or 1.0)
                if exit_ts >= cutoff and exit_price <= 0.10:
                    count += 1
            return count
        except Exception:
            return 0

    def _is_dir_cooldown_active(self, direction: str, cooldown_minutes: int = 15) -> bool:
        """Return True if a trade on this asset+direction closed within the last N minutes."""
        try:
            import json, time as _time
            from datetime import datetime, timezone
            from pathlib import Path
            path = Path(__file__).parent.parent.parent / "data" / "positions_state.json"
            if not path.exists():
                return False
            data = json.loads(path.read_text(encoding="utf-8"))
            cutoff = _time.time() - cooldown_minutes * 60
            signal_up = direction == "UP"
            asset_tag = f"[{self.asset}]"
            for trade in data.get("closed", []):
                if asset_tag not in (trade.get("event_title") or ""):
                    continue
                trade_dir = trade.get("direction", "")
                trade_is_up = trade_dir in ("YES", "UP")
                if trade_is_up != signal_up:
                    continue
                raw_ts = trade.get("exit_time") or trade.get("closed_at")
                if not raw_ts:
                    continue
                try:
                    if isinstance(raw_ts, str):
                        exit_ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).timestamp()
                    else:
                        exit_ts = float(raw_ts)
                    if exit_ts >= cutoff:
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _recent_closed_loss_streak(self, n: int = 3) -> int:
        """Return consecutive recent closed losses from positions_state.json."""
        try:
            closed = self.state_mgr.get_closed_positions(limit=n)
        except AttributeError:
            closed = []
            try:
                import json
                from pathlib import Path
                path = Path(__file__).parent.parent.parent / "data" / "positions_state.json"
                if path.exists():
                    data = json.loads(path.read_text(encoding="utf-8"))
                    closed = data.get("closed", [])[:n]
            except Exception:
                return 0
        except Exception:
            return 0

        streak = 0
        for trade in closed[:n]:
            pnl = float(trade.get("realized_pnl", trade.get("profit", 0)) or 0)
            if pnl < 0:
                streak += 1
            else:
                break
        return streak

    # ── Dual-entry ────────────────────────────────────────────────────────────

    @staticmethod
    def should_dual_enter(up_price: float, dn_price: float) -> bool:
        from config import DUAL_ENTRY_MAX_COMBINED
        return (up_price + dn_price) < DUAL_ENTRY_MAX_COMBINED

    def compute_dual_sizes(self, score: float, main_price: float, hedge_price: float, balance: float):
        main_usd  = self.compute_size(score, main_price, balance)
        hedge_usd = round(0.25 * main_usd, 2)
        return main_usd, hedge_usd

    async def check_potential_trade(self, session: aiohttp.ClientSession) -> None:
        """Run a pre-flight check at T-45s to see if a trade is close to triggering."""
        try:
            klines = await _fetch_klines_async(session, self.asset, self.timeframe, 30)
            if not klines or len(klines) < 14:
                self._update_potential_trade_file(False)
                return
            
            closes = [float(k[4]) for k in klines]
            rsi = _compute_rsi(closes)
            mom = _compute_momentum(closes)
            
            if rsi is None:
                self._update_potential_trade_file(False)
                return
                
            from core.engine.spot_websocket_ingest import get_current_ofi
            ofi = await get_current_ofi(self.asset)
            
            from core.engine.regime_filter import get_regime_mode
            regime = get_regime_mode(self.timeframe)
            
            trend_up_agreement = False
            trend_dn_agreement = False
            
            from core.engine.signal_core import decide_signal
            dec = decide_signal(
                rsi,
                mom,
                ofi,
                self.timeframe,
                regime=regime,
                trend_up_agreement=trend_up_agreement,
                trend_dn_agreement=trend_dn_agreement,
                use_session_scaling=True,
            )
            
            is_potential = False
            if dec["direction"] is not None and not dec["blocked"]:
                is_potential = True
            else:
                from core.engine.signal_core import REGIME_RSI_PARAMS, DEFAULT_SIGNAL_PARAMS
                regime_upper = regime.upper()
                if regime_upper in REGIME_RSI_PARAMS:
                    p = REGIME_RSI_PARAMS[regime_upper]
                else:
                    p = DEFAULT_SIGNAL_PARAMS
                
                # Check if RSI is close to trigger bands (within 3.5 points)
                if rsi < p["reversal_lo"] + 3.5 or rsi > p["reversal_hi"] - 3.5:
                    is_potential = True
                elif rsi > p["rsi_up"] - 3.5 or rsi < p["rsi_dn"] + 3.5:
                    is_potential = True
            
            self._update_potential_trade_file(is_potential)
        except Exception as e:
            log.warning("[PRE-FLIGHT] Failed check for %s/%s: %s", self.asset, self.timeframe, e)
            self._update_potential_trade_file(False)

    def _update_potential_trade_file(self, value: bool) -> None:
        try:
            import json as _json
            from pathlib import Path as _Path
            path = _Path(__file__).parent.parent.parent / "data" / "potential_trades.json"
            
            data = {}
            if path.exists():
                try:
                    data = _json.loads(path.read_text(encoding="utf-8"))
                except Exception:
                    data = {}
            
            key = f"{self.asset}/{self.timeframe}"
            data[key] = value
            
            path.write_text(_json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            log.warning("[PRE-FLIGHT] Failed to update potential_trades.json: %s", e)
