# ZISI — Items
**Last Updated:** 2026-07-18 15:05 SAST
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

## 🔴🔥 ITEM 22 — Chainlink Data Streams Credentials
**Type:** Owner Action | **Priority:** 🔥 URGENT

Form submitted 2026-07-04. **15 days.** Three contacts made, zero credentials received.

**Status:**
- ✅ Email 1: gtm-inbound@smartcontract.com (July 4 — form submission)
- ✅ Email 2: Stephen Maceda (July 16 — first follow-up)
- ✅ Email 3: Stephen Maceda + CC gtm-inbound (July 18 14:21 SAST — escalation sent)
- Discord `#data-feeds` is read-only. Owner DM'd a fake account (scammer) — ignore that.

**🚨 SCAM WARNING:** A Discord account `admin.livechainlink` calling itself "CHAINLINK LIVE SUPPORT" contacted the owner. This is a SCAMMER. Do NOT respond. Block and report.

**Next action — NEW EMAIL CHANNEL:**
- **To:** `devrel@smartcontract.com` (Chainlink DevRel direct email — confirmed active for Data Streams)
- **CC:** `gtm-inbound@smartcontract.com`
- **Subject:** `Chainlink Data Streams — Sponsored Access Credentials [15 Days Pending]`

> Hi Chainlink DevRel team, I am following up on a sponsored Data Streams access request that was approved on July 3 and submitted via form on July 4. It has now been 15 days with no credentials or response. I have also copied Stephen Maceda (tvc-stephen.maceda@smartcontract.com) on previous follow-ups.
>
> Project: Polymarket binary prediction market trading engine (paper trading, building toward live).
> Infrastructure: Live on VPS, HMAC-authenticated requests coded and ready, awaiting only the endpoint + credentials.
>
> Could someone from the provisioning team action this? I am happy to jump on a call or provide any additional info.
>
> Mthunzi Sibiya | mthunzi.sibiya2005@gmail.com

**Also:** Official form: https://chain.link/contact ("Talk to an Expert")

**Done when:** HMAC key + endpoint + asset IDs received → hand to coding tool for Item 19.

---

## 🔴 ITEM 24 — Win Rate Stability Floor (82% Minimum)
**Type:** Monitoring + Coding Tool | **Priority:** High

Owner requirement: WR must stay above **82%** at all times.

**Live data (1,082 trades as of 2026-07-18):**
| Asset | Trades | WR | Status |
|---|---|---|---|
| DOGE | 222 | 86.3% | ✅ |
| SOL | 201 | 85.6% | ✅ |
| XRP | 238 | 84.8% | ✅ |
| ETH | 213 | 84.2% | ✅ |
| BTC | 186 | 82.6% | ✅ |
| **BNB** | **16** | **60.0%** | ⚠️ Too few trades |
| **HYPE** | **6** | **50.0%** | ⚠️ Too few trades |
| **OVERALL** | **1,082** | **84.2%** | ✅ Above floor |

**Root cause of WR drag:** BNB and HYPE are new assets with insufficient history. Engine's rolling outcomes window is nearly empty — not yet calibrated. As trade count grows, WR should self-correct toward the 84–86% range seen in established assets.

**Monitoring:** Watch asset breakdown in terminal. Alert if any established asset (100+ trades) drops below 82%.

**Done when:** BNB and HYPE each reach 50+ trades with WR ≥ 82%, confirming calibration.

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


