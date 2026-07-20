"""
signal_core.py — the pure ZiSi entry-signal cascade.

Single source of truth for the RSI/momentum/OFI direction decision, shared by
the live engine (core/engine/updown_engine.py) and the historical backtester
(tools/backtest/simulator.py) so the two can never drift apart.

This captures ONLY the raw cascade: direction + base score + an OFI-divergence
`blocked` flag. The mom/OFI score boosts, dual-entry path, AI predictor, and
edge-orchestrator layers remain in generate_signal (they depend on live market
prices / external systems and are applied after this function returns).
"""
from typing import Optional

# Defaults == the constants currently hardcoded in generate_signal.
# Overriding these is how the backtester sweeps parameters.
DEFAULT_SIGNAL_PARAMS = {
    "rsi_up": 60.0, "mom_up": 0.02,
    "rsi_up_soft": 54.0, "mom_up_soft": 0.01, "ofi_confirm_up": 0.45,
    "rsi_dn": 40.0, "mom_dn": -0.02,
    "rsi_dn_soft": 46.0, "mom_dn_soft": -0.01, "ofi_confirm_dn": -0.45,
    "reversal_lo": 20.0, "reversal_hi": 80.0, "reversal_score": 0.70,
    # OFI-divergence block magnitudes (sign applied per-direction)
    "ofi_block_neutral": 0.35,  # used when 45 <= rsi <= 55
    "ofi_block_5m": 0.28,
    "ofi_block_15m": 0.20,
}

# Regime-specific RSI and momentum thresholds (Sprint 3 checklist)
REGIME_RSI_PARAMS = {
    "TRENDING": {
        "rsi_up": 60.0,
        "mom_up": 0.02,
        "rsi_up_soft": 54.0,
        "mom_up_soft": 0.01,
        "ofi_confirm_up": 0.45,
        "rsi_dn": 40.0,
        "mom_dn": -0.02,
        "rsi_dn_soft": 46.0,
        "mom_dn_soft": -0.01,
        "ofi_confirm_dn": -0.45,
        "reversal_lo": 20.0,
        "reversal_hi": 80.0,
        "reversal_score": 0.70,
        "ofi_block_neutral": 0.35,
        "ofi_block_5m": 0.28,
        "ofi_block_15m": 0.20,
    },
    "MEAN_REVERTING": {
        "rsi_up":      55.0,   # lowered from 60 — oscillation peaks hit earlier in ranging markets
        "mom_up":      0.015,
        "rsi_up_soft": 50.0,   # lowered from 54
        "mom_up_soft": 0.008,
        "ofi_confirm_up": 0.40,
        "rsi_dn":      45.0,   # raised from 40 — symmetric
        "mom_dn":      -0.015,
        "rsi_dn_soft": 50.0,   # raised from 46
        "mom_dn_soft": -0.008,
        "ofi_confirm_dn": -0.40,
        "reversal_lo": 20.0,
        "reversal_hi": 80.0,
        "reversal_score": 0.70,
        "ofi_block_neutral": 0.30,
        "ofi_block_5m": 0.25,
        "ofi_block_15m": 0.18,
    },
    "VOLATILE_CHAOS": {
        "rsi_up": 65.0, # tightened RSI triggers to reduce noise-signal entries in choppy markets
        "mom_up": 0.02,
        "rsi_up_soft": 65.0, # disabled soft triggers in chaos regime
        "mom_up_soft": 0.02,
        "ofi_confirm_up": 0.45,
        "rsi_dn": 35.0, # tightened RSI triggers to reduce noise-signal entries in choppy markets
        "mom_dn": -0.02,
        "rsi_dn_soft": 35.0, # disabled soft triggers in chaos regime
        "mom_dn_soft": -0.02,
        "ofi_confirm_dn": -0.45,
        "reversal_lo": 18.0,
        "reversal_hi": 82.0,
        "reversal_score": 0.70,
        "ofi_block_neutral": 0.35,
        "ofi_block_5m": 0.28,
        "ofi_block_15m": 0.20,
    },
    "COMPRESSION": {
        "rsi_up": 60.0,
        "mom_up": 0.02,
        "rsi_up_soft": 52.0, # loosened soft threshold to generate more breakout entries
        "mom_up_soft": 0.01,
        "ofi_confirm_up": 0.35, # loosened soft threshold to generate more breakout entries
        "rsi_dn": 40.0,
        "mom_dn": -0.02,
        "rsi_dn_soft": 48.0, # loosened soft threshold to generate more breakout entries
        "mom_dn_soft": -0.01,
        "ofi_confirm_dn": -0.35, # loosened soft threshold to generate more breakout entries
        "reversal_lo": 20.0,
        "reversal_hi": 80.0,
        "reversal_score": 0.70,
        "ofi_block_neutral": 0.35,
        "ofi_block_5m": 0.28,
        "ofi_block_15m": 0.20,
    },
}


def _block_magnitude(rsi: float, timeframe: str, p: dict) -> float:
    if 45.0 <= rsi <= 55.0:
        return p["ofi_block_neutral"]
    return p["ofi_block_5m"] if timeframe == "5m" else p["ofi_block_15m"]


def decide_signal(
    rsi,
    mom: float,
    ofi: float,
    timeframe: str,
    params: Optional[dict] = None,
    regime: Optional[str] = None,
    trend_up_agreement: bool = False,
    trend_dn_agreement: bool = False,
    use_session_scaling: bool = False,
    atr_percentile: Optional[float] = None,
    bbw_percentile: Optional[float] = None,
    fast_cvd: Optional[float] = None,
    binance_obi: Optional[float] = None,
) -> dict:
    """Return {"direction": "UP"|"DOWN"|None, "score": float, "is_reversal": bool, "blocked": bool}."""
    if params is None:
        if regime:
            regime_upper = regime.upper()
            if regime_upper == "TREND":
                regime_upper = "TRENDING"
            elif regime_upper == "MEAN_REVERSION":
                regime_upper = "MEAN_REVERTING"
            
            if regime_upper in REGIME_RSI_PARAMS:
                p = REGIME_RSI_PARAMS[regime_upper]
            else:
                p = DEFAULT_SIGNAL_PARAMS
        else:
            p = DEFAULT_SIGNAL_PARAMS
    else:
        p = params

    # Retrieve Dynamic Session Parameters (Sprint 11) - Only if explicitly enabled (live engine path)
    session_rsi_mult = 1.0
    if use_session_scaling:
        try:
            from core.shared.session_manager import TradingSessionManager
            session_params = TradingSessionManager.get_active_session_params()
            session_rsi_mult = session_params.get("rsi_band_multiplier", 1.0)
        except Exception:
            pass

    # Apply moderate loosening (0.90x of distance from 50.0 center) if there is a strong trend agreement
    up_mult = session_rsi_mult * 0.90 if trend_up_agreement else session_rsi_mult
    dn_mult = session_rsi_mult * 0.90 if trend_dn_agreement else session_rsi_mult

    # Mathematically scale the RSI trigger distances from the 50.0 baseline
    rsi_up_eff = 50.0 + (p["rsi_up"] - 50.0) * up_mult
    rsi_up_soft_eff = 50.0 + (p["rsi_up_soft"] - 50.0) * up_mult
    rsi_dn_eff = 50.0 + (p["rsi_dn"] - 50.0) * dn_mult
    rsi_dn_soft_eff = 50.0 + (p["rsi_dn_soft"] - 50.0) * dn_mult

    res = {"direction": None, "score": 0.0, "is_reversal": False, "blocked": False}
    if rsi is None:
        return res



    # 1. Pre-momentum reversal sniping is disabled for pure SIG isolation
    # if rsi < p["reversal_lo"]:
    #     res.update(direction="UP", score=p["reversal_score"], is_reversal=True)
    #     return res
    # elif rsi > p["reversal_hi"]:
    #     res.update(direction="DOWN", score=p["reversal_score"], is_reversal=True)
    #     return res



    up_trigger = (
        (rsi > rsi_up_eff and rsi <= p["reversal_hi"] and mom >= p["mom_up"])
        or (rsi > rsi_up_soft_eff and rsi <= p["reversal_hi"] and mom >= p["mom_up_soft"] and ofi > p["ofi_confirm_up"])
    )
    dn_trigger = (
        (rsi < rsi_dn_eff and rsi >= p["reversal_lo"] and mom <= p["mom_dn"])
        or (rsi < rsi_dn_soft_eff and rsi >= p["reversal_lo"] and mom <= p["mom_dn_soft"] and ofi < p["ofi_confirm_dn"])
    )

    if up_trigger:
        # Overextension block REMOVED — was blocking RSI 60-80 UP signals in MEAN_REVERTING
        # if (regime or "").upper() == "MEAN_REVERTING" and rsi > 60.0:
        #     res["blocked"] = True
        #     return res

        # Mandatory micro-OFI 5m UP gate REMOVED — was blocking 50%+ of 5m UP signals
        # if timeframe == "5m" and ofi <= 0.0:
        #     res["blocked"] = True
        #     return res

        if ofi < -_block_magnitude(rsi, timeframe, p):
            res["blocked"] = True
            res["reason"] = f"ofi_divergence (ofi={ofi:+.3f} < block={-_block_magnitude(rsi, timeframe, p):+.3f})"
            return res
        rsi_eff = max(rsi, rsi_up_eff)
        res["direction"] = "UP"
        res["score"] = min(0.85, 0.50 + (rsi_eff - rsi_up_eff) / max(1.0, 100.0 - rsi_up_eff) * 0.35)
        res["reason"] = "confirm"
        return res

    if dn_trigger:
        # Overextension block REMOVED — was blocking RSI 20-40 DOWN signals in MEAN_REVERTING
        # if (regime or "").upper() == "MEAN_REVERTING" and rsi < 40.0:
        #     res["blocked"] = True
        #     return res

        # Mandatory micro-OFI 5m DOWN gate REMOVED — was blocking 50%+ of 5m DOWN signals
        # if timeframe == "5m" and ofi >= 0.0:
        #     res["blocked"] = True
        #     return res

        if ofi > _block_magnitude(rsi, timeframe, p):
            res["blocked"] = True
            res["reason"] = f"ofi_divergence (ofi={ofi:+.3f} > block={_block_magnitude(rsi, timeframe, p):+.3f})"
            return res
        rsi_eff = min(rsi, rsi_dn_eff)
        res["direction"] = "DOWN"
        res["score"] = min(0.85, 0.50 + (rsi_dn_eff - rsi_eff) / max(1.0, rsi_dn_eff) * 0.35)
        res["reason"] = "confirm"
        return res

    res["reason"] = _get_skip_detail_reason(rsi, mom, ofi, rsi_up_eff, rsi_up_soft_eff, rsi_dn_eff, rsi_dn_soft_eff, p)
    return res


def _get_skip_detail_reason(rsi, mom, ofi, rsi_up_eff, rsi_up_soft_eff, rsi_dn_eff, rsi_dn_soft_eff, p) -> str:
    if rsi > 50.0:
        if rsi <= rsi_up_soft_eff:
            return f"RSI={rsi:.1f} <= soft_trigger={rsi_up_soft_eff:.1f}"
        if mom < p["mom_up_soft"]:
            return f"RSI={rsi:.1f}, but Mom={mom:.4f} < soft_trigger={p['mom_up_soft']:.4f}"
        if ofi <= p["ofi_confirm_up"]:
            return f"RSI={rsi:.1f}, but OFI={ofi:+.2f} <= trigger={p['ofi_confirm_up']:+.2f}"
        if mom < p["mom_up"]:
            return f"RSI={rsi:.1f} > trigger={rsi_up_eff:.1f}, but Mom={mom:.4f} < trigger={p['mom_up']:.4f}"
        return f"RSI={rsi:.1f} (neutral/no trigger)"
    else:
        if rsi >= rsi_dn_soft_eff:
            return f"RSI={rsi:.1f} >= soft_trigger={rsi_dn_soft_eff:.1f}"
        if mom > p["mom_dn_soft"]:
            return f"RSI={rsi:.1f}, but Mom={mom:.4f} > soft_trigger={p['mom_dn_soft']:.4f}"
        if ofi >= p["ofi_confirm_dn"]:
            return f"RSI={rsi:.1f}, but OFI={ofi:+.2f} >= trigger={p['ofi_confirm_dn']:+.2f}"
        if mom > p["mom_dn"]:
            return f"RSI={rsi:.1f} < trigger={rsi_dn_eff:.1f}, but Mom={mom:.4f} > trigger={p['mom_dn']:.4f}"
        return f"RSI={rsi:.1f} (neutral/no trigger)"

