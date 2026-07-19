# ZISI — Items
**Last Updated:** 2026-07-19 09:15 SAST
**Maintained by:** All agents (Antigravity + Coding Tool) + Owner

> **How this document works:**
> - Every actionable item lives here while it is open
> - When an item is completed: **remove it from this list**, add a summary to **ZISI - Journal.md** Session Entries as permanent history
> - **Read ZISI - Journal.md first** before working on any item
> - Items added when Antigravity, Coding Tool, or Owner identifies something to achieve

---

## 🟡 ITEM 24 — Win Rate Stability Floor (82% Minimum)
**Type:** Monitoring | **Priority:** High | **Status:** MONITORING ACTIVE ✅

Owner requirement: WR must stay above **82%** at all times.

**Live data (as of 2026-07-18 23:25 SAST):**
| Asset | Trades | WR | Status |
|---|---|---|---|
| DOGE | 222+ | 86.3% | ✅ |
| SOL | 201+ | 85.6% | ✅ |
| XRP | 238+ | 84.8% | ✅ |
| ETH | 213+ | 84.2% | ✅ |
| BTC | 186+ | 82.6% | ✅ |
| **BNB** | **35** | **75.0%** | 📈 Calibrating fast (24 wins, 8 losses / 75% WR) |
| **HYPE** | **22** | **63.6%** | 📈 Calibrating slowly (14 wins, 8 losses / 63.6% WR) |
| **OVERALL** | **~1,200** | **~83%** | ✅ Above floor |

**Key fix deployed (Session 12):** BNB and HYPE now have full confluence engine filtering (CVD/OBI/NIC). Previously running with zero confluence = coin-flip entries. WR for these two assets has improved significantly and is moving toward the 82% floor.

**Done when:** BNB and HYPE each reach 50+ trades with WR ≥ 82%.

---

## 🔴 ITEM 26 — Sunday Morning Loss Pattern (Regime, Leader Guard & Price Caps)
**Type:** Coding | **Priority:** High | **Status:** PENDING OWNER APPROVAL ⏳

Forensic autopsy of Sunday morning losses (wiped July 19) identified three gaps:
1. **Hardlocked Regime**: Regime detector is hardlocked to `MEAN_REVERTING` in `regime_detector.py`, making the bot blind to strong trends and causing it to fade momentum waterfalls.
2. **Disabled Leader Guard**: The Altcoin Market Leader Corroboration Guard in `app/main.py` is commented out, allowing the bot to enter multiple concurrent altcoin trades against the BTC/ETH macro trend.
3. **High Entry Prices**: No maximum entry price ceiling for standard trades, allowing the bot to buy YES contracts at >0.80 where risk/reward is highly unfavorable and Tranche B targets are mathematically impossible.

**Actions proposed:**
- Re-enable Leader Corroboration Guard in `app/main.py` (uncomment lines 390-396).
- Implement max entry price cap of `0.80` for standard single entries in `_validate_trade_slot` (in `app/main.py`).
- Unlock the regime detector by reverting line 204 in `core/engine/regime_detector.py` to `self._current_regime = best_regime`.

**Done when:** Code changes are implemented, unit tested, verified on VPS, and the bot runs dynamically without taking correlated basket losses against macro trends.

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*
