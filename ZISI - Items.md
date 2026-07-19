# ZISI — Items
**Last Updated:** 2026-07-19 11:55 SAST
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
**Type:** Coding | **Priority:** CRITICAL 🔥 | **Status:** PENDING OWNER CREDENTIALS 🔑

We have been approved for sponsored Chainlink Data Streams access on the VPS. 
We need to:
1. Store the credentials (endpoint URL, client ID, client secret, HMAC keys) securely.
2. Implement the HMAC-based signature generation client and WebSocket listener for live price feeds (BTC, ETH, SOL, XRP, DOGE).
3. Integrate parsing, data pipelines, and a seamless fallback layer to Polymarket's RTDS / Tier 2/3 REST polling.

**Progress Update (Pre-Integration Complete):**
- Fixed HYPE connection status. Created a custom pipeline for HYPE (since it is not listed on spot markets) by connecting to the Binance Futures `bookTicker` stream in the terminal (`zisi_terminal.py`) and polling the Binance Futures REST API in `polymarket_rtds_ingest.py`. HYPE price is now fully active across the spot matrix, the Chainlink column cache, and backends on the VPS.

**Done when:** Chainlink streams are successfully integrated, active, and feeding live price data to the trading engines in real-time.

---

## 🟡 ITEM 28 — System-Wide Execution and Price Latency Optimizations
**Type:** Optimization | **Priority:** HIGH | **Status:** IN PROGRESS ⚡

To ensure sub-millisecond execution and instant updates across all metrics:
1. **[DONE] Remove Forced Price Resolving Lag:** Modified `_resolve_l2_prices` inside `updown_engine.py` to check the `polymarket_l2_gateway` cache immediately on attempt 0 instead of sleeping for 1.0s. This cuts lookup latency for standard signals from 1.0s to 0ms when prices are cached.
2. **[DONE] Optimize Terminal Refresh and I/O:** Increased console rendering and file synchronization frequency from 3Hz (333ms) to 10Hz (100ms) for an instant visual refresh, while gating markdown report generation to prevent redundant disk I/O.
3. **[DONE] Sizing Balance Configuration:** Added `SIZING_BALANCE: float = 1200.0` to `config.py` and updated `UpDownEngine.compute_size` to cap sizing at `$1,200` account balance, preventing exponential scaling during compounding growth while keeping tests 100% green.
4. **[PENDING] Streamlined Cline Fetches:** Cache Binance klines or stream them via WebSocket to avoid HTTP GET REST API calls (~40-100ms lag) at trade boundaries.
5. **[PENDING] Pyth Hermes Integration:** Activate the dormant Pyth Hermes Real-Time SSE price service to achieve sub-0.1ms oracle spot price updates.

**Done when:** All local price lookups and pipeline latency benchmarks check out at sub-10ms.

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*
