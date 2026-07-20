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

## 🟡 ITEM 28/31 — System-Wide Execution Speed & Zero-Lag Terminal UI Optimization
**Type:** Optimization | **Priority:** HIGH | **Status:** IN PROGRESS ⚡

To ensure sub-millisecond execution and silky-smooth visual performance:
1. **[DONE] Remove Forced Price Resolving Lag:** Modified `_resolve_l2_prices` inside `updown_engine.py` to check the `polymarket_l2_gateway` cache immediately on attempt 0 instead of sleeping for 1.0s (0ms lookup).
2. **[DONE] Sizing Balance Configuration:** Added `SIZING_BALANCE: float = 1200.0` to `config.py` and updated `UpDownEngine.compute_size` to cap sizing at `$1,200` account balance.
3. **[IN PROGRESS] Terminal UI mtime Gate & Buffering:** Update `zisi_terminal.py` file-polling logic to check file `mtime` before reading disk JSON files, buffering Rich console output to prevent SSH buffer delays when resizing or toggling full screen.
4. **[PENDING] Streamlined Kline Caching:** Cache Binance klines to eliminate HTTP GET REST latency (~40-100ms) at trade boundaries.
5. **[DELETED] Pyth Hermes:** Pyth abandoned due to systematic basis error (-3 to -5 bps); 3-tier oracle stack (Chainlink DS, Binance, Coinbase) is the single source of truth.

**Done when:** Terminal dashboard renders smooth at 10Hz with instant response and 0ms cached lookups.

---

## 🟡 ITEM 29 — Tiered Fixed-Tranche Compounding Position Sizer ($50 → $3,000)
**Type:** Coding | **Priority:** HIGH | **Status:** IN PROGRESS 📐

Implement Owner's approved Tiered Fixed-Tranche Compounding Sizing model:
- **Tier 1 (Balance $50 – $300):** Trade size = $5.00 – $15.00 (replicates the engine that drove the original $50 → $2.7k run).
- **Tier 2 (Balance $300 – $1,000):** Trade size = $20.00 – $40.00.
- **Tier 3 (Balance $1,000 – $3,000+):** Trade size = $50.00 flat cap per trade.

**Done when:** `position_sizer.py` and `updown_engine.py` scale position sizes according to balance tiers with unit test verification.

---

## 🟡 ITEM 30 — Restore 40¢ Max Slippage Gate for Peak Volume Execution
**Type:** Coding | **Priority:** HIGH | **Status:** IN PROGRESS ⚡

Revert `_max_slippage` in `app/main.py` back to `0.40` (40¢):
- Unlocks max trade frequency and eliminates 0-trade neutral market aborts.
- Paired with high-cent target equalization (Session 25): for any entry $\ge 0.80$, EX target equalizes to ES target (`entry + 0.12`), ensuring expensive contracts exit at scalp target instead of holding to expiry.

**Done when:** `_max_slippage = 0.40` is set in `app/main.py`, verified locally and deployed to VPS.

---

## 🟡 ITEM 32 — Git Branch Consolidation (`stable-june22` → `main`)
**Type:** DevOps | **Priority:** MEDIUM | **Status:** IN PROGRESS 🌿

Consolidate Git branch workflow:
- Merge remote branch `stable-june22` into `main` across local, GitHub, and VPS.
- Make `main` the single active tracking branch everywhere so there is zero branch ambiguity.

**Done when:** `git status` on local and VPS reports `On branch main` with 0 drift.

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*
repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*

