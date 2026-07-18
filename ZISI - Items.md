# ZISI — Items
**Last Updated:** 2026-07-18 20:38 SAST
**Maintained by:** All agents (Antigravity + Coding Tool) + Owner

> **How this document works:**
> - Every actionable item lives here while it is open
> - When an item is completed: **remove it from this list**, add a summary to **ZISI - Journal.md** Session Entries as permanent history
> - **Read ZISI - Journal.md first** before working on any item
> - Items added when Antigravity, Coding Tool, or Owner identifies something to achieve

---

## ❌ ITEM 22 — Chainlink Data Streams Credentials (ABANDONED)
**Type:** Owner Action | **Priority:** Low | **Status:** CANCELLED / ABANDONED

Owner engaged with Chainlink support. Chainlink is deprecating sponsored feeds on September 1, 2026, and redirected to their paid self-serve portal. Given the friction and lack of support, we are abandoning the integration of Chainlink RTDS HMAC feeds. Tier 1 primary feeds will remain on public Polymarket CLOB WebSocket Gateway.

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

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*
