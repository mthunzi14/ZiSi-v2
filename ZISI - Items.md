# ZISI — Items
**Last Updated:** 2026-07-18 12:55 SAST
**Maintained by:** All agents (Antigravity + Coding Tool) + Owner

> **How this document works:**
> - Every actionable item lives here while it is open
> - When an item is completed: **remove it from this list**, add a summary to **ZISI - Journal.md** Session Entries as permanent history
> - **Read ZISI - Journal.md first** before working on any item
> - Items added when Antigravity, Coding Tool, or Owner identifies something to achieve

---

## 🔴🔥 ITEM 5a — Remove All Kalshi Code from Source
**Type:** Coding Tool | **Priority:** High

Kalshi pip package still in venv. Source files need verification.

**Steps:**
1. `grep -ri "kalshi" --include="*.py"` in repo (excluding venv/) — confirm zero hits
2. Delete any remaining Kalshi branches/imports in source
3. `pip uninstall kalshi-python` in venv
4. Remove from `requirements.txt` / `pyproject.toml`
5. Run bot — confirm no import errors

**Done when:** Zero Kalshi references in source. Package uninstalled from venv.

---

## 🔴 ITEM 13 — Delete Non-Owner Wallet Files
**Type:** Coding Tool | **Priority:** Medium

`wallet/` on VPS contains non-owner files (verified 2026-07-18):
- `wallet_0x21d0a97a_active_positions.json`, `_history.json`, `_multi_week.json`
- `wallet_0xeebde7a0_active_positions.json`, `_history.json`
- `wallet_active_positions.json`
- `resolved_winners_cache.json`

**Steps:** Confirm owner wallet, delete all non-owner files, commit.

**Done when:** `wallet/` only contains owner files or is empty.

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

## 🔴🔥 ITEM 22 — Escalate Chainlink Data Streams Credentials
**Type:** Owner Action | **Priority:** 🔥 URGENT

Form submitted 2026-07-04. 14+ days. Third follow-up needed.

**Send to:** tvc-stephen.maceda@smartcontract.com | **CC:** gtm-inbound@smartcontract.com
**Subject:** Re: Chainlink Data Streams — Polymarket Binary Trading Engine [ESCALATION]

> Hi Stephen, following up for the third time on the HMAC API credentials for the sponsored Data Streams access program.
>
> Timeline: Approved July 3 → Form submitted July 4 → Follow-up July 16 → No response as of July 18 (14 days waiting).
>
> We are live on paper with real infrastructure waiting for this key. If there is a delay or an additional step needed, just let me know — otherwise I would appreciate either the credentials or a direct escalation to whoever provisions them.
>
> Happy to jump on a call any time this week.
>
> Mthunzi Sibiya | mthunzi.sibiya2005@gmail.com | @MthunziSibiya

**Also:** Chainlink Discord `#data-streams` — tag @ChainlinkDevRel. Link: https://discord.gg/chainlink

**Done when:** HMAC key + endpoint + asset IDs received → hand to coding tool for Item 19.

---

*Companion to ZISI - Journal.md | Both live at repo root: C:\Users\mthun\Downloads\ZiSi-v2\*
*Completed items archived in Journal Session Entries*

