# ZISI — Items
**Last Updated:** 2026-07-20 17:25 SAST
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

**Live data (as of 2026-07-19 20:25 SAST - After Cutoff B Scrub):**
| Asset | Trades | WR | Status |
|---|---|---|---|
| DOGE | 255 | 86.5% | ✅ (218 wins, 34 losses, 3 BE) |
| ETH | 235 | 84.0% | ✅ (194 wins, 37 losses, 4 BE) |
| SOL | 243 | 82.6% | ✅ (195 wins, 41 losses, 7 BE) |
| XRP | 269 | 82.4% | ✅ (216 wins, 46 losses, 7 BE) |
| BTC | 213 | 81.9% | 📈 Calibrating (172 wins, 38 losses, 3 BE) |
| **BNB** | **55** | **71.2%** | 📈 Calibrating (37 wins, 15 losses, 3 BE) |
| **HYPE** | **42** | **69.0%** | 📈 Calibrating (29 wins, 13 losses) |
| **OVERALL** | **1,311** | **82.6%** | ✅ Above floor (including BE trades as push) |

**Key fix deployed (Session 12):** BNB and HYPE now have full confluence engine filtering (CVD/OBI/NIC). Previously running with zero confluence = coin-flip entries. WR for these two assets has improved significantly and is moving toward the 82% floor.

**Done when:** BNB and HYPE each reach 50+ trades with WR ≥ 82%.

---

## 🔴 ITEM 27 — Chainlink Data Streams Feed Integration
**Type:** Coding | **Priority:** CRITICAL 🔥 | **Status:** CREDENTIALS RECEIVED (READY FOR CODING PHASE) 🔑

Owner has received the Chainlink Data Streams HMAC credentials (received 2026-07-19).
We need to:
1. Store the credentials (endpoint URL, client ID, client secret, HMAC keys) securely in `.env`.
2. Implement the HMAC-SHA256 signature generation client and WebSocket listener for live price feeds (BTC, ETH, SOL, XRP, DOGE).
3. Integrate parsing, data pipelines, and a seamless fallback layer to Polymarket's RTDS / Tier 2/3 REST polling.

**Progress Update (Pre-Integration Complete):**
- Fixed HYPE connection status. Created a custom pipeline for HYPE (since it is not listed on spot markets) by connecting to the Binance Futures `bookTicker` stream in the terminal (`zisi_terminal.py`) and polling the Binance Futures REST API in `polymarket_rtds_ingest.py`. HYPE price is now fully active across the spot matrix, the Chainlink column cache, and backends on the VPS.
- Credentials officially received by Owner on 2026-07-19. Ready for implementation.

**Done when:** Chainlink streams are successfully integrated, active, and feeding live price data to trading engines.

---

## 🟢 ITEM 33 — 80/20 ES/EX Tranche Ratio & 24¢ EX Target Refinement
**Type:** Coding | **Priority:** HIGH | **Status:** APPROVED & QUEUED 🎯

Implement Owner's approved Tranche System Optimization:
- **Tranche Allocation:** 80% ES (Early Scalp) / 20% EX (Extended Execution).
- **ES Target:** `entry_price + 0.12` (+12¢ target exit, 95.3% WR capital floor engine).
- **EX Target:** `entry_price + 0.24` (+24¢ target exit, double ES scalp target!).
- **High-Cent Target Rule:** For entries $\ge 0.80$, both ES and EX targets equalize to `entry_price + 0.12`.

**Done when:** `trader.py` and `updown_engine.py` process 80/20 tranche split and +24¢ EX target with unit test verification.

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*
