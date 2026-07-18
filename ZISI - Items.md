# ZISI — Items
**Last Updated:** 2026-07-18 10:15 SAST
**Maintained by:** All agents (Antigravity + Coding Tool) + Owner

> **How this document works:**
> - Every actionable item lives here while it is open
> - Items are described in full so they can be given directly to the coding tool
> - When an item is completed: remove it from this list, add a summary to **ZISI - Journal.md** (Section 4 — Changelog) as history/reference
> - **Read ZISI - Journal.md first** before working on any item — it has full context, architecture, rules, and philosophy
> - Items are added here when Antigravity or the Owner identifies something that must be achieved (coding, analysis, or owner action)

---

## 🟡 ITEM STATUS KEY
| Symbol | Meaning |
|---|---|
| 🔴 | Not started — active, ready to work |
| 🔥 | High priority — do this soon |
| ⏸️ | On hold — owner must re-authorize before touching |
| ✅ | Done — move summary to Journal, delete item |

---

## 🔴🔥 ITEM 14 — Sync Local Changes to VPS
**Type:** Coding Tool + Owner
**Priority:** 🔥 High

**What it is:**
Every code change made locally must be pushed to GitHub and then pulled on the VPS. Currently there may be drift between local, GitHub, and VPS. This is the deployment/sync step that closes every coding session.

**Process:**
1. `git add -A && git commit -m "[description of changes]"` on local
2. `git push origin main`
3. SSH into VPS: `git pull origin main`
4. Restart the bot process
5. Check startup logs for errors
6. Log the commit hash in ZISI - Journal.md Section 4

**Done when:** VPS is running the same commit as local and GitHub. No drift. Startup logs clean.

---

## 🔴 ITEM 19 — Replace Pyth with Proper Oracle Stack
**Type:** Coding Tool
**Priority:** Medium (blocked on Item 22 — Chainlink key)

**What it is:**
Once Pyth is removed (Item 18), the oracle stack needs a proper hierarchy. The current stack is just Chainlink via RTDS relay. The goal is a multi-layered fallback that is fast, accurate, and resilient.

**Target oracle priority order:**
1. **Chainlink Data Streams** (PRIMARY) — direct HMAC pull, ~50-100ms latency. Waiting for credentials (Item 22).
2. **Binance WebSocket** (SECONDARY) — already partially implemented, fast, reliable for BTC/ETH/SOL/XRP/DOGE/BNB
3. **Coinbase WebSocket** (TERTIARY) — to be added, cross-validates Binance/Chainlink divergence

**How to do it:**
- Once Chainlink HMAC key received: implement `DataStreamsIngest` class in `polymarket_rtds_ingest.py`
- Add Coinbase Advanced Trade WebSocket feed: subscribe to BTC-USD, ETH-USD, SOL-USD, XRP-USD, DOGE-USD, BNB-USD. Store as `coinbase_prices[asset]`. Use for cross-validation only — not as primary strike source.
- Ensure clear fallback logic: Chainlink DS → Binance WS → Coinbase WS → error

**Done when:** Three-tier oracle stack live and logging. No Pyth. Clean fallback hierarchy confirmed in startup logs.

---

## 🔴🔥 ITEM 22 — Escalate Chainlink Data Streams Credentials
**Type:** Owner Action
**Priority:** 🔥 URGENT

**What it is:**
Chainlink Data Streams HMAC credentials were approved (sponsored access program) but not delivered. Form submitted 2026-07-04. Two follow-up emails already sent. 14+ days waiting. Need to escalate beyond Stephen Maceda.

**Escalation email draft:**

---
**To:** `tvc-stephen.maceda@smartcontract.com`
**CC:** `gtm-inbound@smartcontract.com`
**Subject:** Re: Chainlink Data Streams — Polymarket Binary Trading Engine [ESCALATION]

Hi Stephen,

I'm following up for the third time regarding the HMAC API credentials for the Chainlink Data Streams sponsored access program.

To recap the timeline:
- July 3: You confirmed my project qualifies for sponsored access and directed me to complete the onboarding form
- July 4: I completed and submitted the onboarding form in full
- July 16: I sent a follow-up — no response
- Today (July 18): Still no credentials received, 14 days after form submission

This is a time-sensitive integration for a live trading engine. I'm respectful of your team's workload, but I'd appreciate either:
1. The HMAC credentials, or
2. A direct escalation to whoever is provisioning them, or
3. A realistic timeline so I can plan accordingly

I'm also happy to jump on a call this week if that moves things faster. Available any time.

Best regards,
Mthunzi Sibiya
mthunzi.sibiya2005@gmail.com | Telegram: @MthunziSibiya

---

**Also consider:** Post in the official Chainlink Discord (#data-streams channel) tagging the developer relations team. Sometimes BD threads get lost but Discord is monitored daily. Chainlink Discord: https://discord.gg/chainlink

**Done when:** HMAC key + REST/WebSocket endpoint + asset IDs received. Immediately hand to coding tool for Item 19 integration.

---

*ZISI - Items.md | Companion to ZISI - Journal.md | Both live at repo root: `C:\Users\mthun\Downloads\ZiSi-v2\`*
*Items 1-17, 18, 23, 24, 25 (history) archived in ZISI - Journal.md Section 4*
