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
        is_weekend: bool
    ) -> Dict[str, Any]:
        base_dir = self.rsi_analyst.analyze(rsi, mom)
        cvd_score = self.cvd_analyst.analyze(fast_cvd, slow_cvd)
        obi_score = self.obi_analyst.analyze(binance_obi)
        nic_score = self.nic_analyst.analyze(price_velocity)
        
        # Order flow pressure is composite of CVD, OBI, NIC
        flow_pressure = (cvd_score * 0.4) + (obi_score * 0.4) + (nic_score * 0.2)
        
        # If we are in a mean-reverting regime, fade the base direction!
        if regime == "MEAN_REVERTING" and base_dir != "NEUTRAL":
            base_dir = "DOWN" if base_dir == "UP" else "UP"
            
        direction = base_dir
        decision = "NEUTRAL"
        decision_path = "NO_SIGNAL"

        if base_dir != "NEUTRAL":
            if base_dir == "UP":
                if flow_pressure < -0.25:
                    direction = "DOWN"
                    decision = "INVERT"
                    decision_path = f"UP_INVERTED_TO_DOWN_BY_FLOW(pressure={flow_pressure:.2f})"
                else:
                    decision = "CONFIRM"
                    decision_path = f"UP_CONFIRMED_BY_FLOW(pressure={flow_pressure:.2f})"
            elif base_dir == "DOWN":
                if flow_pressure > 0.25:
                    direction = "UP"
                    decision = "INVERT"
                    decision_path = f"DOWN_INVERTED_TO_UP_BY_FLOW(pressure={flow_pressure:.2f})"
                else:
                    decision = "CONFIRM"
                    decision_path = f"DOWN_CONFIRMED_BY_FLOW(pressure={flow_pressure:.2f})"
        else:
            if regime == "MEAN_REVERTING" or is_weekend:
                if rsi > 60 and flow_pressure < -0.15:
                    direction = "DOWN"
                    decision = "FADE"
                    decision_path = f"FADE_UP_BOUNDARY_TO_DOWN(rsi={rsi:.1f}, pressure={flow_pressure:.2f})"
                elif rsi < 40 and flow_pressure > 0.15:
                    direction = "UP"
                    decision = "FADE"
                    decision_path = f"FADE_DOWN_BOUNDARY_TO_UP(rsi={rsi:.1f}, pressure={flow_pressure:.2f})"

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
