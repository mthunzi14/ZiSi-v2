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

## 🔴 ITEM 25 — Fix Large Losses from MEAN_REVERTING Expired Markets
**Type:** Code | **Priority:** High | **Status:** IN DISCUSSION — Awaiting final approach decision

**Root cause confirmed (Sessions 11–12):**
- All losses >$3.50 = `market expired, loss` — bot entered a direction, market resolved against it → position drops to $0.01
- **Confirmed live event at 15:25:10 SAST (Jul 18):** ETH/SOL/XRP/DOGE all expired simultaneously → **-$37.70 in 1 second** (4 trades × ~$9.40 EX+ES combined). Bot then immediately won 6 consecutive trades recovering +$20.
- Problem is **time horizon mismatch**, NOT signal quality: MEAN_REVERTING correctly detects a deviation, but the 5-min market resolves before reversal plays out.

**⛔ OWNER DIRECTION — NO BLOCKING GATES:**
> Owner explicitly does NOT want:
> - Gates that skip or block trades (kills volume)
> - Confluence score thresholds that filter entries  
> - Any mechanism that reduces trade frequency

**✅ Proposed approach — Reduced sizing for MEAN_REVERTING entries only:**
- Trade still fires → **volume is fully preserved** ✅
- For MEAN_REVERTING regime entries only: apply **0.5× position size multiplier**
- WIN: smaller profit (acceptable, still profitable)
- LOSS/Expired: maximum loss halved → **-$2.50 instead of -$5.00 per expired trade**
- Simultaneous 4-asset expiry disaster: **-$18 instead of -$37.70** ✅
- Sizing reverts to 1.0× automatically when regime = TRENDING

**Pending owner final approval of this approach before implementation.**

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*



