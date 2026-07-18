# ZISI — Items
**Last Updated:** 2026-07-18 15:32 SAST
**Maintained by:** All agents (Antigravity + Coding Tool) + Owner

> **How this document works:**
> - Every actionable item lives here while it is open
> - When an item is completed: **remove it from this list**, add a summary to **ZISI - Journal.md** Session Entries as permanent history
> - **Read ZISI - Journal.md first** before working on any item
> - Items added when Antigravity, Coding Tool, or Owner identifies something to achieve

---


---



## ✅ ITEM 19 — Build Full Oracle Stack
**Type:** Code | **Priority:** Critical | **Status:** COMPLETE (commit `56d8035`)

**Three-tier oracle stack is live in `core/engine/polymarket_rtds_ingest.py`:**

| Tier | Source | Method | Interval | Status |
|---|---|---|---|---|
| 1 — PRIMARY | Chainlink RTDS (Polymarket) | WebSocket | Real-time ticks | ✅ Live |
| 1 — UPGRADE | Chainlink Data Streams (HMAC) | WebSocket | Real-time | ⏳ Waiting on Item 22 credentials |
| 2 — SECONDARY | Binance REST | Poll every 30s | Fallback when T1 down | ✅ Live |
| 3 — TERTIARY | Coinbase REST | Poll every 45s | Only updates stale assets | ✅ Live (NEW) |

**Plug-and-play upgrade:** When HMAC credentials arrive, slot them into `_socket_loop()` — no other code changes needed.

---

## ⏸️ ITEM 20 — Gate HYPE in config.py
**Type:** Coding Tool | **Priority:** ⏸️ On Hold

Move HYPE from `ACTIVE_ASSETS` to `FUTURE_ASSETS`. Do NOT implement without owner re-authorization.

---

## ⏳ ITEM 22 — Chainlink Data Streams Credentials
**Type:** Owner Action | **Priority:** High | **Status:** AWAITING RESPONSE

All follow-up emails sent. Awaiting credential provisioning from Chainlink team.

**Status:**
- ✅ Email 1: gtm-inbound@smartcontract.com (July 4 — form submission)
- ✅ Email 2: Stephen Maceda (July 16 — first follow-up)
- ✅ Email 3: Stephen Maceda + CC gtm-inbound (July 18 — escalation)
- ✅ Discord: Owner joined Chainlink server, posted in #data-feeds, DM sent to real mod
- ⏳ Awaiting response

**🚨 SCAM WARNING:** Discord account `admin.livechainlink` / "CHAINLINK LIVE SUPPORT" is a SCAMMER. Owner is intentionally engaging to expose their playbook. Do NOT take any real wallet or link actions.

**Done when:** HMAC key + endpoint + asset IDs received → hand to coding tool for Item 19 Tier 1 upgrade.

---

## 🟡 ITEM 24 — Win Rate Stability Floor (82% Minimum)
**Type:** Monitoring | **Priority:** High | **Status:** MONITORING ACTIVE ✅

Owner requirement: WR must stay above **82%** at all times.

**Live data (1,130 trades as of 2026-07-18 15:27 SAST):**
| Asset | Trades | WR | Status |
|---|---|---|---|
| DOGE | 222+ | 86.3% | ✅ |
| SOL | 201+ | 85.6% | ✅ |
| XRP | 238+ | 84.8% | ✅ |
| ETH | 213+ | 84.2% | ✅ |
| BTC | 186+ | 82.6% | ✅ |
| **BNB** | **16+** | **60.0%** | ⚠️ Calibrating — now has full confluence (fix deployed) |
| **HYPE** | **12+** | **50.0%** | ⚠️ Calibrating — now has full confluence (fix deployed) |
| **OVERALL** | **1,130** | **~84%** | ✅ Above floor |

**Key fix deployed (Session 12):** BNB and HYPE now have full confluence engine filtering (CVD/OBI/NIC). Previously running with zero confluence = coin-flip entries. WR for these two assets expected to improve significantly over next 50 trades.

**Done when:** BNB and HYPE each reach 50+ trades with WR ≥ 82%.

---

## 🔴 ITEM 25 — Fix Large Losses from MEAN_REVERTING Expired Markets
**Type:** Code | **Priority:** High | **Status:** PENDING OWNER APPROVAL

**Root cause identified (Session 11):**
All losses >$3.50 share one pattern: `market expired, loss` — bot entered a direction, market resolved against it, position dropped to $0.01.
- In MEAN_REVERTING regime, bot bets on price reversal
- These markets resolved in continuation direction before reversal could occur
- Problem is **time horizon**, not signal quality — 5-min binary too short when strong trend underway

**Proposed fixes (owner must choose one or more):**
1. ⚠️ **HFT Momentum Gate:** If Binance futures momentum is strongly trending at entry, skip MEAN_REVERTING reversal entries
2. ⚠️ **Raise threshold:** Increase confluence score requirement for MEAN_REVERTING entries (e.g., from current to 0.75+)
3. ⚠️ **Expiry proximity block:** Block new entries within last 2 candle windows before market expiry

**Owner must approve which fix(es) to implement before any code is written.**

---

## 🔴 ITEM 25 — Fix Wrong Direction on MEAN_REVERTING Entries (BTC Leadership)
**Type:** Code | **Priority:** High | **Status:** ANALYSIS — Developing approach

**Root cause confirmed (Sessions 11–13):**
- All major losses share one pattern: bot entered a direction, ALL assets moved the opposite way simultaneously
- **Confirmed live event at 15:25:10 SAST (Jul 18):** ETH/SOL/XRP/DOGE all entered UP → ALL expired DOWN. -$37.70 in 1 second.
- **Owner's theory (confirmed correct):** BTC is the market leader. When BTC shoots in a direction, every other asset follows it. If BTC had been read correctly as DOWN at that moment, the bot would have entered DOWN on all assets and banked +$37.70 instead of losing it.
- **The real problem: the bot is picking the WRONG DIRECTION — not how much it bets.**

**⛔ PERMANENTLY REJECTED APPROACHES (do NOT reopen these):**
> The following were proposed and **permanently rejected by owner:**
> - ❌ Gates that skip or block MEAN_REVERTING trades (kills volume)
> - ❌ Confluence score thresholds that filter entries
> - ❌ 0.5× position size multiplier for MEAN_REVERTING (ALL entries are MEAN_REVERTING — this changes everything)
> - ❌ Any mechanism that reduces trade frequency or alters sizing
> - **The bot must NOT be changed in ways that affect its overall behaviour. Fix the direction. Nothing else.**

**✅ CORRECT APPROACH — BTC Market Leadership Signal:**
The fix is **directional intelligence**, not filtering:
1. Read BTC's real-time momentum at every signal evaluation (already available via HFT WebSocket `get_cvd_metrics("BTC")`)
2. When BTC has strong directional momentum (CVD fast significantly positive or negative), use BTC's direction as an **override anchor** for all other assets
3. If asset signal conflicts with BTC momentum → **flip to match BTC** (direction correction, not skip)
4. If BTC has no clear momentum → leave asset signal unchanged
5. Trade still fires every time. Volume unchanged. Only the direction is corrected by BTC leadership.

**Why this works:**
- BTC leads → all others follow (confirmed by owner's market analysis)
- We already have BTC CVD/OBI/momentum in real-time from the HFT WS
- Confluence already runs for BTC — we just need to propagate BTC's directional verdict to sibling assets when it's decisive
- This turns the 10-loss scenario into a 10-WIN scenario

**Implementation plan (pending owner approval to code):**
- In `updown_engine.py`, after confluence runs for an asset, if `asset != "BTC"`: fetch BTC's current CVD fast/slow from `_market_books`
- If BTC CVD fast > threshold AND asset direction = "DOWN" → flip to "UP"
- If BTC CVD fast < -threshold AND asset direction = "UP" → flip to "DOWN"
- Threshold = tunable parameter (start at 50.0 USDT CVD delta)
- Log `[BTC-ANCHOR] {asset}: flipped direction {old} → {new} (BTC CVD={btc_cvd:.0f})`

**Pending owner final approval to implement.**

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*




