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

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*
