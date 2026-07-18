# ZISI — Items
**Last Updated:** 2026-07-18 06:25 SAST
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

## 🔴🔥 ITEM 5a — Remove All Kalshi Code
**Type:** Coding Tool
**Priority:** 🔥 High

**What it is:**
Kalshi is a dead integration. `"kalshi_active": 0` in positions_state.json. Zero trades ever executed. Every cycle the Kalshi pipeline runs and produces nothing — pure dead weight.

**Where to clean:**
- `core/engine/cycle_manager.py` — lines 103-115 (Kalshi candidate pipeline), line 25 (`import kalshi_python`), lines 117-118 (Kalshi conflict detection)
- `app/main.py` — any Kalshi event fetching, `kalshi_events` parameter
- `core/engine/trader.py` — any Kalshi order placement branches
- `requirements.txt` / `pyproject.toml` — remove `kalshi-python` dependency
- `config.py` — remove any `KALSHI_*` config keys

**How to do it:**
1. `grep -ri "kalshi"` across entire repo
2. Delete every Kalshi-specific branch, import, and function
3. Remove `kalshi_events` parameter from all function signatures
4. Run the bot, verify no import errors
5. Confirm dashboard displays correctly with Polymarket-only data

**Done when:** Zero `kalshi` string references remain in the codebase.

---

## 🔴🔥 ITEM 9 — Label All Dormant Daemons in main.py
**Type:** Coding Tool
**Priority:** Medium

**What it is:**
`app/main.py` registers all background tasks. Some are V3-era experiments that are dormant but still registered. They need clear `[DORMANT — V3]` labels so any reader instantly knows not to touch them.

**How to do it:**
In `app/main.py`, for each dormant task registration, add a comment block:
```python
# [DORMANT — V3] ─────────────────────────────────────────
# This daemon was part of the V3 experimental branch.
# DO NOT enable without explicit owner instruction.
# ─────────────────────────────────────────────────────────
```
Identify dormant tasks by checking which ones have `enabled: false` in config or zero execution history in runtime_tracking.json.

**Done when:** All dormant daemons clearly labeled. No unlabeled "mystery" task registrations.

---

## 🔴🔥 ITEM 10 — Config.py Cleanup
**Type:** Coding Tool
**Priority:** High

**What it is:**
`config.py` has dead keys from Kalshi, Fair Value (FV) experiments, and Overlay C (never used).

**What to remove:**
- All `KALSHI_*` keys (Kalshi is dead — Item 5a handles the code, this handles the config)
- All `FV_*` / Fair Value experiment keys that are no longer referenced
- `OVERLAY_C_*` — Overlay C was never activated and is fully dead
- Clean up any commented-out blocks of dead config

**What to keep:**
- `OVERLAY_B_*` keys can be removed AFTER Item 11 completes (Overlay B engine code deleted first)
- All active strategy params, RTDS config, Kelly params — do not touch

**Done when:** Config is lean, every key is actually used somewhere in the live codebase.

---

## 🔴🔥 ITEM 11 — Delete Overlay B from updown_engine.py
**Type:** Coding Tool
**Priority:** 🔥 High

**What it is:**
`core/engine/updown_engine.py` lines ~1346-1395 contain the Overlay B hot-path block. Overlay B was a secondary signal overlay that was disabled. The code still sits in the hot path, executing conditional checks on every single cycle even though the overlay is off.

**How to do it:**
1. Open `updown_engine.py`
2. Find the Overlay B block (lines ~1346-1395 — verify exact lines first)
3. Delete the entire block
4. Verify the function still returns the same value without the block
5. Run the bot and confirm signal evaluation still works

**Done when:** No Overlay B code exists in updown_engine.py. Hot path is clean.

---

## 🔴🔥 ITEM 13 — Delete Non-User Wallet Data Files
**Type:** Coding Tool
**Priority:** Medium

**What it is:**
The `wallet/` directory in the repo contains `.json` files from wallets that do not belong to the owner. These were pulled as part of early analysis but should not persist in the repo. The owner's Polymarket handle is confirmed — anything else is clutter.

**How to do it:**
1. List all files in `wallet/`
2. Delete any file that does not correspond to the owner's wallet address
3. Commit the deletion

**Done when:** `wallet/` only contains owner-relevant files (or is empty if there are none).

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

## 🔴🔥 ITEM 16b — Add BNB to RTDS Subscription
**Type:** Coding Tool
**Priority:** 🔥 High

**What it is:**
`core/engine/polymarket_rtds_ingest.py` line ~138 has the list of assets subscribed to the Polymarket RTDS WebSocket (Chainlink price relay). BNB is currently NOT in this list — so BNB trades via Binance REST fallback (too slow, lower accuracy). Adding BNB to RTDS restores strict oracle sourcing for BNB candles.

**How to do it:**
Find the RTDS subscription asset list in `polymarket_rtds_ingest.py` around line 138. Add `"BNB"` to the list.

**Done when:** BNB receives Chainlink prices via RTDS WebSocket. Confirm by checking that `chainlink_prices.json` shows a BNB entry updating in real-time.

---

## 🔴 ITEM 18 — Remove Pyth Entirely
**Type:** Coding Tool
**Priority:** Medium

**What it is:**
Pyth was tried and abandoned (2026-06-10). It had a -3 to -5 basis point systematic bias vs Chainlink. Currently `pyth_prices.json` is written by `polymarket_rtds_ingest.py` lines 102-106 — but it's just a **carbon copy of chainlink_prices.json** (Pyth data is never actually ingested). The terminal shows a Pyth column that also displays Chainlink data. All Pyth references are cosmetic lies.

**How to do it:**
1. Delete `pyth_prices.json` generation code from `polymarket_rtds_ingest.py` (lines 102-106)
2. Remove Pyth column from `zisi_terminal.py` pricing display
3. Fix `_get_oracle_fallback_prices` docstring — remove "Pyth (Tertiary)" mention
4. Delete `data/pyth_prices.json` from disk on VPS and locally
5. Commit

**Done when:** Zero Pyth references remain. No pyth_prices.json written. Terminal is honest.

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

## 🔴🔥 ITEM 23 — Fix HYPE and BNB Delayed Trades / Slippage Gate
**Type:** Coding Tool
**Priority:** 🔥 High

**What it is:**
As of 2026-07-18 early morning SAST, HYPE and BNB trades are experiencing issues (delays, slippage gate triggering excessively).
* **Investigation Findings:** Antigravity ran websocket test scripts and confirmed that Polymarket RTDS emits active Chainlink feeds for BOTH `bnb/usd` and `hype/usd`. However, neither asset is subscribed to in the RTDS connection loop in `polymarket_rtds_ingest.py`, causing the engine to fall back to slow REST calls or stall.
* **The Fix:** Subscribing to `"BNB"` and `"HYPE"` in `polymarket_rtds_ingest.py` (Item 16b) will resolve the latency, matching strike validation times, and silencing the gate issues.

**Done when:** BNB and HYPE cycle cleanly without excessive gate fires.

---

## 🔴 ITEM 24 — Timezone Location String Polish
**Type:** Coding Tool
**Priority:** Low

**What it is:**
In the topmost dashboard header, the location is written as `Johannesburg/SAST`. The owner requested removing the `/SAST` suffix, displaying only `(Johannesburg)`.

**Where to change:**
* `zisi_terminal.py` line 600: Change `location_str = "Johannesburg/SAST"` to `location_str = "Johannesburg"`.

---

## 🔴 ITEM 25 — Consolidate L2 Book Polling Logs
**Type:** Coding Tool
**Priority:** Medium

**What it is:**
At candle boundaries, when the L2 markets are not yet created or are resolving, each of the active assets prints a warning or info log (e.g. `[ENGINE] BNB/5m: Waiting for market creation/resolution, poll attempt 1/15...`). When multiple assets are polling simultaneously, this prints 5–7 consecutive lines of identical status updates.
The owner requested that we consolidate these logs into a single neater line (e.g. `[ENGINE] Waiting for 5m market creation/resolution for: BTC, ETH, SOL, XRP, DOGE, BNB, HYPE (attempt 1/15)...`).

**How to do it:**
* Implement a simple asynchronous coordination helper in `UpDownEngine` or `polymarket_rtds_ingest.py` (using a shared dictionary and lock) to collect registering assets at each poll timestamp and print a single consolidated list.

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
*Items 1-17 (history) archived in ZISI - Journal.md Section 4*
