# ZISI — Items
**Last Updated:** 2026-07-18 14:25 SAST
**Maintained by:** All agents (Antigravity + Coding Tool) + Owner

> **How this document works:**
> - Every actionable item lives here while it is open
> - When an item is completed: **remove it from this list**, add a summary to **ZISI - Journal.md** Session Entries as permanent history
> - **Read ZISI - Journal.md first** before working on any item
> - Items added when Antigravity, Coding Tool, or Owner identifies something to achieve

---


---



## 🔴 ITEM 19 — Build Full Oracle Stack
**Type:** Coding Tool | **Priority:** Medium (blocked on Item 22)

**Priority order:**
1. Chainlink Data Streams (PRIMARY — waiting on Item 22 credentials)
2. Binance WebSocket (SECONDARY — partially live)
3. Coinbase WebSocket (TERTIARY — cross-validation only)

**Done when:** Three-tier oracle stack running with clean fallback in startup logs.

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

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*


