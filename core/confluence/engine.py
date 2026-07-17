import logging
from typing import Dict, Any

log = logging.getLogger("zisi.confluence")

class RSIAnalyst:
    def analyze(self, rsi: float, mom: float) -> str:
        if rsi > 60 and mom > 0.05:
            return "UP"
        elif rsi < 40 and mom < -0.05:
            return "DOWN"
        return "NEUTRAL"

class CVDAnalyst:
    def analyze(self, fast_cvd: float, slow_cvd: float) -> float:
        if abs(slow_cvd) < 1e-4:
            return 0.0
        ratio = fast_cvd / abs(slow_cvd)
        return max(-1.0, min(1.0, ratio))

class OBIAnalyst:
    def analyze(self, binance_obi: float) -> float:
        return max(-1.0, min(1.0, binance_obi))

class NICAnalyst:
    def analyze(self, price_velocity: float) -> float:
        # Price velocity = % change in spot price over sub-second interval.
        # Extreme price velocity indicates a liquidation cascade (NIC).
        if abs(price_velocity) > 0.005:  # 0.5% move in sub-seconds
            return 1.0 if price_velocity > 0 else -1.0
        return 0.0

class RiskManager:
    def __init__(self):
        self.rsi_analyst = RSIAnalyst()
        self.cvd_analyst = CVDAnalyst()
        self.obi_analyst = OBIAnalyst()
        self.nic_analyst = NICAnalyst()

    def evaluate(
        self,
        rsi: float,
        mom: float,
        fast_cvd: float,
        slow_cvd: float,
        binance_obi: float,
        price_velocity: float,
        regime: str,
        is_weekend: bool = False
    ) -> Dict[str, Any]:
        base_dir = self.rsi_analyst.analyze(rsi, mom)
        cvd_score = self.cvd_analyst.analyze(fast_cvd, slow_cvd)
        obi_score = self.obi_analyst.analyze(binance_obi)
        nic_score = self.nic_analyst.analyze(price_velocity)
        
        # Order flow pressure is composite of CVD, OBI, NIC
        flow_pressure = (cvd_score * 0.4) + (obi_score * 0.4) + (nic_score * 0.2)
        
        decision = "NEUTRAL"
        decision_path = "NO_SIGNAL"
        direction = "NEUTRAL"

        if regime == "MEAN_REVERTING":
            # In Mean Reversion, we ONLY trade counter-trend (fading extremes).
            # Overbought (RSI > 60) -> Fade to DOWN
            # Oversold (RSI < 40) -> Fade to UP
            fade_dir = "NEUTRAL"
            if rsi > 60:
                fade_dir = "DOWN"
            elif rsi < 40:
                fade_dir = "UP"
                
            if fade_dir != "NEUTRAL":
                # Check if order flow is heavily fighting the fade
                if fade_dir == "DOWN" and flow_pressure > 0.25:
                    # Fighting strong buying flow: skip!
                    direction = "NEUTRAL"
                    decision = "SKIP"
                    decision_path = f"FADE_DOWN_BLOCKED_BY_BUY_FLOW(pressure={flow_pressure:.2f})"
                elif fade_dir == "UP" and flow_pressure < -0.25:
                    # Fighting strong selling flow: skip!
                    direction = "NEUTRAL"
                    decision = "SKIP"
                    decision_path = f"FADE_UP_BLOCKED_BY_SELL_FLOW(pressure={flow_pressure:.2f})"
                else:
                    direction = fade_dir
                    decision = "FADE"
                    decision_path = f"FADE_CONFIRMED_BY_FLOW(rsi={rsi:.1f}, pressure={flow_pressure:.2f})"
        else:
            # TRENDING regime: Follow the trend and flow
            if base_dir != "NEUTRAL":
                if base_dir == "UP":
                    if flow_pressure < -0.25:
                        direction = "DOWN"
                        decision = "INVERT"
                        decision_path = f"UP_INVERTED_TO_DOWN_BY_FLOW(pressure={flow_pressure:.2f})"
                    else:
                        direction = "UP"
                        decision = "CONFIRM"
                        decision_path = f"UP_CONFIRMED_BY_FLOW(pressure={flow_pressure:.2f})"
                elif base_dir == "DOWN":
                    if flow_pressure > 0.25:
                        direction = "UP"
                        decision = "INVERT"
                        decision_path = f"DOWN_INVERTED_TO_UP_BY_FLOW(pressure={flow_pressure:.2f})"
                    else:
                        direction = "DOWN"
                        decision = "CONFIRM"
                        decision_path = f"DOWN_CONFIRMED_BY_FLOW(pressure={flow_pressure:.2f})"

        return {
            "direction": direction,
            "decision": decision,
            "decision_path": decision_path,
            "flow_pressure": flow_pressure,
            "cvd_score": cvd_score,
            "obi_score": obi_score,
            "nic_score": nic_score
        }

# Global singleton instance
confluence_risk_manager = RiskManager()
