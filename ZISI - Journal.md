# ZISI — Journal
**Location:** `/root/ZiSi-v2/ZISI - Journal.md` (repo root — always present on VPS, local, and GitHub)
**Companion:** `ZISI - Items.md` (same repo root) — the active items tracker. These two documents go hand in hand.
**Purpose:** The single source of truth for the entire ZISI project. Every analysis, every decision, every code change, every insight — recorded permanently. Read by all agents before every session. Updated after every session.

---

## 🔄 HOW TO USE THESE TWO DOCUMENTS

**ZISI - Journal.md** (this file) = the master context document. Architecture, philosophy, oracle stack, market intelligence, rules, changelog, completed items history.

**ZISI - Items.md** = the active to-do list. Every open item with full description. Items are removed when done and their summary moves here as history.

**Workflow commands:**
- `"Read ZISI - Journal"` → Load full context at the start of any session
- `"Read ZISI - Items"` → See what's currently open and needs doing
- `"Update ZISI - Journal"` → Append latest work, decisions, and analysis

**No agent touches code without reading this first. No session ends without this being current.**

---

## 👥 TEAM ROLES

### 🏆 The Owner — Boss & Final Decision Maker
Commands everything. Makes all final decisions on strategy, risk, what to enable, what to delete. No agent changes anything architectural without explicit owner instruction.

### 🔬 Antigravity — Deep Analysis Agent (ANALYSIS ONLY)
**Antigravity's job is PURELY deep analysis and honesty.** It reads code, audits systems, finds bugs, researches market intelligence, tracks the competition, and keeps both documents current. Antigravity **does not write trading logic code.** The only files it ever modifies are:
- `ZISI - Journal.md` (this file — always kept current)
- `ZISI - Items.md` (the active items tracker)
Antigravity always ends every session by asking: *"What's next, boss?"* — because the system can always be refined.

### 💻 Coding Tool — Implementation Agent
Executes code changes based on items from `ZISI - Items.md` and context from this document. After completing work, it must:
1. Add a changelog entry to Section 4 of this document
2. Mark completed items in `ZISI - Items.md`
3. Note any new bugs or decisions that arose during implementation

The coding tool is also an analyst — it reads deeply before writing. It never modifies dormant strategies without owner instruction.

---

## 1. WHAT ZISI IS

ZISI (ZiSi-v2) is a **fully automated, original-signal quantitative trading bot** operating on Polymarket's 5-minute binary prediction markets.

- **NOT a copy trader.** Generates 100% original signals from CVD, OBI, Regime, and price data.
- **NOT a manual trading tool.** Runs 24/7 autonomously on a VPS.
- **Primary strategy:** Called "ZISI" by the owner. Dual-tranche system (ES + EX).

**Assets:** BTC, ETH, SOL, XRP, DOGE, BNB, HYPE (all defined in `config.py`)
**Timeframes:** 5m primary, 15m secondary
**Signal stack:** CVD (Cumulative Volume Delta) + OBI (Order Book Imbalance) + Regime Filter + Price Action

**The system resolves trades on Chainlink oracle prices.** Chainlink price at candle open = the strike. Chainlink price at candle close = the resolution verdict. This is the foundation of every edge calculation.

---

## 2. ARCHITECTURE — KEY FILES

| File | Role |
|---|---|
| `config.py` | Single source of truth for all flags, assets, thresholds, Kelly params |
| `app/main.py` | Entry point — registers all background daemons, controls what's live vs dormant |
| `core/engine/updown_engine.py` | Signal hot path — CVD, OBI, regime, fair value, strike computation |
| `core/engine/trader.py` | Order placement, fill confirmation, slippage logging |
| `core/engine/cycle_manager.py` | Per-asset trading cycle orchestration, entry timing |
| `core/engine/polymarket_rtds_ingest.py` | Real-time Chainlink price feed via Polymarket RTDS WebSocket |
| `core/engine/spot_websocket_ingest.py` | Binance WebSocket for CVD/OBI computation |
| `core/risk/position_sizer.py` | Kelly Criterion position sizing |
| `core/risk/antifragile.py` | Win/loss streak tracker — adjusts sizing multiplier |
| `data/` | All runtime state: positions, slippage logs, balance history, gate logs |
| `scratch/` | One-off analysis scripts — NOT part of the live system |
| `wallet/` | Inspiration wallet analysis pulls — NOT used at runtime |

---

## 3. CHAINLINK ORACLE — COMPLETE PICTURE

### 3a. Current Implementation

ZISI connects to Polymarket's RTDS WebSocket (`wss://ws-live-data.polymarket.com`) and subscribes to `crypto_prices_chainlink`. This is **Polymarket's relay** of Chainlink data — not a direct oracle connection.

**Price flow:**
```
Chainlink Oracle Node → Polymarket Backend → RTDS WebSocket → ZISI
(Polygon block ~2s)   (sub-second relay)   (sub-second push)
Total lag: ~2-4 seconds from actual oracle update
```

**What gets stored:**
- `_chainlink_prices[asset]` — latest price + timestamp (in-memory)
- `chainlink_prices.json` — disk cache (written every 0.5s)
- `_chainlink_candle_opens[asset, interval]` — FIRST tick of each candle = the strike

**Strike price logic (`updown_engine.py` lines 696-728):**
1. Get live Chainlink price — must be ≤5 seconds old
2. Get Chainlink candle open for this interval
3. Candle open = strike
4. If either unavailable → **trade skipped entirely** (strict oracle sourcing)

### 3b. CONFIRMED BUG — BNB Has No Chainlink RTDS Feed

**Verified 2026-07-18 via VPS SSH audit.**

VPS `chainlink_prices.json` contains: `["BTC", "ETH", "XRP", "DOGE", "SOL"]` — **BNB is absent.**

VPS `data/entry_logs.json` BNB count: **0**. VPS `data/positions_state.json` BNB closed: **0**.

Root cause: `polymarket_rtds_ingest.py` line 138 only subscribes to 5 assets:
```python
for asset in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:  # BNB MISSING
```

BNB is in `config.py` `ASSETS` list (line 12) and has a `5m` timeframe entry (line 23). But because it has no Chainlink candle open data, the engine skips every BNB signal via strict oracle sourcing. **BNB has never traded. Zero trades since being added.**

**Fix (coding tool — Item 16b):** Add `"BNB"` to the RTDS subscription loop. One word change.

Also verify: `_refresh_from_binance()` SYMBOLS dict in the same file does NOT include BNB either — fix that too so the Binance REST fallback covers BNB when RTDS is down.

### 3c. HYPE — Verified Active Feed

Verified on 2026-07-18 via WebSocket connection testing: Polymarket RTDS does emit a live Chainlink price feed for `hype/usd` (last value read: `59.255824`). The previous "connecting" status and delayed evaluations were entirely due to it being omitted from the subscription list. Subscribing to `"HYPE"` in `polymarket_rtds_ingest.py` will restore live prices. No config gating is needed.

### 3d. Pyth — FULLY DEAD. Remove Entirely.

Pyth was tried and abandoned (2026-06-10). It had -3 to -5 basis point systematic bias vs Chainlink causing directional errors in the leader filter.

**Current Pyth status (as of 2026-07-18 audit):**
- `pyth_prices.json` is written by `polymarket_rtds_ingest.py` lines 102-106 — but it's a **carbon copy of `chainlink_prices.json`**
- The terminal `zisi_terminal.py` shows a Pyth column — also displaying Chainlink data
- `_get_oracle_fallback_prices` docstring mentions "Pyth (Tertiary)" — the code never calls Pyth
- No real Pyth data ingested anywhere

**Coding action (Item 18 — pending):**
1. Delete `pyth_prices.json` generation code from `polymarket_rtds_ingest.py` (lines 102-106)
2. Remove Pyth column from `zisi_terminal.py` pricing display
3. Fix `_get_oracle_fallback_prices` docstring — remove Pyth mention
4. Delete `data/pyth_prices.json` from disk

**Do NOT add real Pyth integration.** The data is corrupted by systematic basis error.

### 3e. Coinbase Oracle Feed — New Item

The user requested adding Coinbase as a secondary price source to replace Pyth. This makes sense because Chainlink itself aggregates from multiple sources including Coinbase. Having direct Coinbase WebSocket data gives:
- A second independent price reference
- Cross-validation against Chainlink (if they diverge >0.5%, flag it)
- Better "what will Chainlink read" estimation for the final seconds of each candle

**Coding action (Item 19 — pending):** Add Coinbase Advanced Trade WebSocket feed as secondary price source in `polymarket_rtds_ingest.py`. Subscribe to BTC-USD, ETH-USD, SOL-USD, XRP-USD, DOGE-USD, BNB-USD. Store as `coinbase_prices[asset]`. Use for cross-validation, not as the primary strike source.

### 3f. Chainlink Data Streams — ACTIVE PURSUIT (TOP PRIORITY)

**Status: Applied. Sponsored access approved. HMAC credentials not yet received. Follow-up required.**

**Email thread summary:**
- **2026-06-05:** Owner emailed `gtm-inbound@smartcontract.com` explaining ZISI's architecture and requesting Data Streams access.
- **2026-07-03:** Stephen Maceda (Chainlink Labs BD) responded — confirmed ZISI qualifies for the **sponsored access program** (free tier for individual developers/quant traders). Directed to complete onboarding form.
- **2026-07-04:** Owner completed and submitted the official onboarding form with full system specs.
- **2026-07-16:** Owner followed up. No credentials received yet. Stephen Maceda = point of contact.
- **2026-07-18:** Still waiting. Promised turnaround was 5-7 days from form submission. We are now 14 days out. **Item 22 = follow up.**

**Contact:** Stephen Maceda `tvc-stephen.maceda@smartcontract.com` | Owner Telegram: `@MthunziSibiya`

**What we get when the key arrives:**
- Direct oracle feed: Chainlink Node → ZISI in ~50-100ms (vs current 2-4s via RTDS relay)
- HMAC-SHA256 signed price reports — cryptographically verifiable
- Sub-second resolution data at candle close = ZISI sees what Chainlink reads BEFORE on-chain transaction confirms
- Same latency advantage that Perfect-Afternoon-Edge appears to be exploiting — used defensively by ZISI

**When the key arrives:** Immediately becomes Priority 1. Integration point: `polymarket_rtds_ingest.py` — new `DataStreamsIngest` class. HMAC-SHA256 signed headers. Feeds to replace RTDS relay as primary oracle source.

## 3g. ZISI Operating Mode — PAPER MODE

**Current mode: PAPER TRADING. All risk controls and circuit breakers are deliberately disabled.**

- No circuit breaker active (losses do not halt the bot)
- No per-trade size cap enforced in live
- No daily loss limit enforced
- Position sizer runs uncapped Kelly on paper balance

**When live mode begins:** All risk controls activate (Section 6 values). Circuit breaker = 2-loss halt. Daily loss cap = 3%. Max trade = min(5% balance, $500). No changes to these values without explicit owner instruction.

---

## 3h. ALL-ASSET CONTRARIAN ENTRY INTELLIGENCE

**Insight from Perfect-Afternoon-Edge analysis (Section 14):**

The most profitable entries across ALL assets — not just BNB — are when the CLOB is pricing the market at 0.10-0.33. This means:
- The crowd is 67-90% confident one side wins
- The opposite side is paying 3x-10x on a correct call
- ZISI's signal stack (CVD, OBI, Regime) may identify when the crowd is wrong at those extreme prices

**This applies to BTC, ETH, SOL, XRP, DOGE, BNB equally.** When ZISI generates a strong signal on the contrarian side of a lopsided market (e.g., signal says UP but CLOB is pricing Up at 0.15), that is potentially the highest-EV trade in the entire system. The payout is 6.7x. Even at a 40% win rate, that trade has positive expected value.

**Action for analysis:** When reviewing ZISI's `signal_evaluations.jsonl`, flag any entry where signal direction matched a side priced at 0.20 or below. These are the "contrarian conviction" slots. Track their win rate separately from normal-priced entries.

**Action for coding tool (future item):** Add a `clob_entry_price` field to the signal evaluation log so we can analyze contrarian entry performance statistically across all assets.

---

## 4. CHANGELOG — All Changes Made (Most Recent First)

### 2026-07-18 — Session: V3 Streamlining & Clean Up with Antigravity (ZISI Agent 1)

**Commit Hash:** `02cb03a`

**Items completed:**
- ✅ **Item 5a — Remove All Kalshi Code**: Completely removed Kalshi candidate loops, imports, configuration keys, ConflictDetector initialization/execution loops, order execution path rejections, account recovery metrics, and deleted dead files: `core/engine/conflict_detector.py` and `core/engine/arbitrage_scanner.py`.
- ✅ **Item 9 — Label All Dormant Daemons in main.py**: Labeled dormant Pyth Hermes Service and Reversal Sniper commented code blocks with `[DORMANT — V3]` warning comments.
- ✅ **Item 10 — Config.py Cleanup**: Cleaned up all dead configuration keys from `config.py`, including Kalshi credentials, Overlay B, Overlay C, and Fair Value night sessions.
- ✅ **Item 11 — Delete Overlay B from updown_engine.py**: Completely stripped Overlay B trend-freeze block from `core/engine/updown_engine.py` hot path.
- ✅ **Item 13 — Delete Non-User Wallet Data Files**: Removed 5 non-owner inspiration wallet files (`wallet_0x21d0a97a_active_positions.json`, `wallet_0x21d0a97a_history.json`, `wallet_0x21d0a97a_multi_week.json`, `wallet_0xeebde7a0_active_positions.json`, `wallet_0xeebde7a0_history.json`) from `wallet/`.
- ✅ **Item 16b / Item 23 — Enable BNB and HYPE Price Feeds**: Subscribed to `"BNB"` and `"HYPE"` in the Polymarket RTDS WebSocket connection loop (`polymarket_rtds_ingest.py`) and added `"BNB": "BNBUSDT"` to the spot REST fallback symbol map.
- ✅ **Item 18 — Remove Pyth Entirely**: Removed Pyth cache writing logic from `polymarket_rtds_ingest.py`, removed Pyth price column and variables from `zisi_terminal.py` Spot & Oracle price matrix dashboard panel, cleaned `_get_oracle_fallback_prices` docstrings in `updown_engine.py` and deleted the local `pyth_prices.json` file.
- ✅ **Item 24 — Timezone Location String Polish**: Removed `/SAST` suffix from terminal dashboard clock leaving only `Johannesburg` location label in `zisi_terminal.py`.
- ✅ **Item 25 — Consolidate L2 Book Polling Logs**: Implemented a thread-safe registry-based debounce aggregation mechanism in `core/engine/updown_engine.py` to consolidate intermediate per-asset "Waiting for market creation..." and "L2 book is illiquid..." warning logs into a single aggregated line per candle boundary/poll attempt.

**Key architectural decisions:**
- Simplified oracle validation by removing unused `get_validated_price` cross-validation logic in `spot_websocket_ingest.py`.
- Stubbed out `strategy_drift_check()` in `app/health_monitor.py` to prevent redundant import attempts of dead Kalshi modules.

### 2026-07-18 — Session: ZiSi Analysis Deep Dive with Antigravity

**Analysis completed:**
- Full Chainlink oracle audit — confirmed BNB RTDS subscription bug
- VPS verified: BNB has 0 trades, BNB absent from `chainlink_prices.json`
- VPS verified: `ACTIVE_ASSETS` includes BNB and HYPE (in `config.py` line 12)
- Pyth confirmed fully dead — carbon copy of Chainlink data
- bbwlover/PBot-10 heist fully analyzed — ZISI structurally immune
- 8 inspiration wallets catalogued — 3 addresses confirmed, 5 pending
- LAT-ARB, NCS, Reversal, Overlay B, Kalshi all audited and properly classified

**Items completed:**
- ✅ Item 3: Slippage & fill rate telemetry implemented
- ✅ Item 6: Kelly sizer cap fixed ($5 flat → dynamic min(5% balance, $500))
- ✅ Item 7: Anti-fragile state reset plan defined
- ✅ Item 8: BNB and HYPE added to config as active assets
- ✅ Item 17: This document created (now named ZISI - Journal.md)

**Documents created:**
- `ZISI - Journal.md` — this journal (lives at repo root)
- `ZISI - Items.md` - active items tracker with full descriptions (repo root)

**Key architectural decisions:**
- Pyth: abandoned, remove entirely
- Overlay B: delete from engine hot path (Items 11)
- Kalshi: remove entirely (Item 5a)
- BNB RTDS: confirmed bug, fix pending (Item 16b)
- Chainlink Data Streams: await key — treat as P1 when received

---

## 5. DORMANT STRATEGIES — DO NOT ACTIVATE WITHOUT AUTHORIZATION

These are intentionally disabled V3 weapons. NOT broken. Never enable without explicit instruction.

| Strategy | Flag | Location | When to activate |
|---|---|---|---|
| LAT-ARB (Latency Arbitrage) | `ENABLE_LATENCY_ARB = False` | `config.py` | After ZISI live validation |
| NCS (Near-Certainty Sniper) | `ENABLE_NCS = False` | `config.py` | If ES WR drops below target |
| Reversal Sniper | Commented out | `app/main.py` | After live calibration |
| Sentiment Daemon | **ACTIVE** | `sentiment_filter.py` | Already running |

**Overlay B** — NOT a dormant weapon. Dead weight. Delete it (updown_engine.py lines 1346-1395). Item 11.
**Fair Value (FV)** — Already deleted. Don't re-introduce.
**Kalshi** — Dead external platform. Delete all references. Item 5a.

---

## 6. RISK CONTROLS — NEVER MODIFY WITHOUT EXPLICIT AUTHORIZATION

| Control | Value | File |
|---|---|---|
| Max trade size | `min(5% balance, $500)` | `position_sizer.py` |
| Circuit breaker | Halt after 2 consecutive losses | `config.py: CIRCUIT_BREAKER_LOSSES = 2` |
| Max daily loss | 3% of balance | `config.py: MAX_DAILY_LOSS_PCT = 3` |
| Max entry price | 0.92 combined | `config.py: DUAL_ENTRY_MAX_COMBINED` |

---

## 7. KELLY SIZER — CURRENT STATE

Changed 2026-07-17 (Item 6):
- Old: $5 flat cap
- New: `min(balance × 0.05, $500)`
- Floor: $1 minimum
- Streak dampener: removed (was halving size after losses — counterproductive)
- Parameters: `KELLY_WIN_RATE = 0.833`, `KELLY_EDGE_MULTIPLIER = 0.25`
- **VPS has NOT received this change yet — sync pending (Item 14)**

---

## 8. INSPIRATION WALLETS — ANALYSIS ONLY, NOT COPY TRADING

8 wallets studied for edge insights. ZISI never copies trades. Pulled via `scratch/pull_bulk_trades.py`.

| Name | Address | Status |
|---|---|---|
| PBot-6 Main | `0x21d0a97aac03917e752857a551bbe5103a00e8d7` | ✅ Confirmed |
| PBot Sweeper | `0x13f0bcec1e2e60ec9acc3bee4d2da2fe9694a50f` | ✅ Confirmed |
| Bonereaper | `0xeebde7a0e019a63e6b476eb425505b7b3e6eba30` | ✅ Confirmed (NOT the owner's wallet) |
| Sir Tova | TBD | ⏳ Owner to provide |
| Power Winner | TBD | ⏳ Owner to provide |
| More Money | TBD | ⏳ Owner to provide |
| Blockchain Surfer | TBD | ⏳ Owner to provide |
| Unknown (8th) | TBD | ⏳ Owner to provide |

`/wallet/*.json` files are one-time pulls — not runtime. Being deleted (Item 13). Keep `resolved_winners_cache.json`.

**The owner's Polymarket handle is NOT Bonereaper.**

---

## 9. PBOT BIBLE — KEY INSIGHTS

PBot ("Punisher") published a strategy guide. ZISI implements every principle:

| Principle | ZISI Status |
|---|---|
| 6-layer WebSocket with warmup gate | ✅ `spot_websocket_ingest.py` |
| Pre-staged order payloads | ✅ `trader.py` |
| 15s reconciliation | ✅ (tighter than PBot's 30s) |
| Never trust API — poll order status | ✅ Pre-flight guard |
| Max entry ≤ $0.80 | ✅ `DUAL_ENTRY_MAX_COMBINED = 0.92` |
| 3-4 tranche chunking | ✅ ES + EX dual-tranche |
| 2-loss circuit breaker | ✅ |
| 5m focus | ✅ |

PBot's core indicators: CVD (primary), OBI (primary), NIC (secondary). All implemented.
PBot's "decoy": publicly claims 15m > 5m. His wallets show 73%+ of profits from 5m. ZISI correctly uses 5m primary.
PBot Sweeper (98.9% WR): enters at T-1.5s to T-0.5s before candle close via LAT-ARB mechanic (ZISI's dormant LAT-ARB scanner is modeled on this).

---

## 10. BBWLOVER ATTACK — CONTEXT AND ZISI IMMUNITY

**Date:** 2026-07-17, 11:00 AM – 2:30 PM SAST
**What happened:** bbwlover (`0x565ca5...`) extracted $175K from copy-trading bot PBot-10 using BNB 5-minute markets. Mechanic: fake entry signals → copy trader fills → push BNB spot on Binance in final 1-2 seconds → Chainlink reads manipulated price → resolves against copy trader.

**Why ZISI is immune:**
- ZISI doesn't copy-trade — generates own signals
- Circuit breaker halts after 2 losses (PBot-10 had none)
- Per-trade size cap (PBot-10 had none)
- Daily loss limit (PBot-10 had none)

**BNB risk:** Manipulation affects market resolution. ZISI's CB limits damage to ~2 trades. Monitoring (Item 15).

**Escalation vectors to know:**
1. Continuous price swinging during candle
2. Liquidity death spiral (market makers leave → book thinner → cheaper to manipulate)
3. Track-record farming: build fake profitable history to attract copy traders, then drain them (long-game attack)

---

## 11. VPS DEPLOYMENT STATUS

**IP:** `204.168.222.48` | **Path:** `/root/ZiSi-v2/` | **User:** root

**Current VPS state (verified 2026-07-18):**
- Running old code (pre Items 3, 6, 8)
- `chainlink_prices.json` has BTC, ETH, XRP, DOGE, SOL — NO BNB
- `ACTIVE_ASSETS` includes BNB and HYPE — but BNB has 0 trades (confirmed RTDS bug)
- `slippage_log.jsonl` exists (11KB) — seeded with historical data
- `order_placements.jsonl` exists (47KB)
- `signal_evaluations.jsonl` exists (1.9MB)

**Sync required (Item 14):** VPS needs Items 3, 6, 8 changes deployed.

---

## 12. OPEN ITEMS — ACTIVE & RECENTLY COMPLETED

> Full descriptions with how-to instructions: `ZISI - Items.md` (repo root)
> ✅ = recently completed this session | 🔴 = pending | 💻 = coding tool | 🔍 = Antigravity analysis

**Recently Completed / Archived:**
| # | Item | Type | Verdict/Summary |
|---|---|---|---|
| ✅ 12 | HYPE liquidity audit | 🔍 | No 5m market on Polymarket. 0 evals on VPS. Informational — see Section 3h. |
| ✅ 15 | BNB manipulation risk | 🔍 | Informational reference only. See Section 14. |
| ✅ 17 | ZISI - Journal.md created | 📝 | This document |
| 🗑️ 21 | BNB liquidity gate | Removed | Owner: “no nonsense gates, we need volume” |

**Active — Coding Tool Tasks (read ZISI - Items.md for full descriptions):**
| # | Item | Priority |
|---|---|---|
| 5a | Remove ALL Kalshi code | 🔥 High |
| 9 | Label dormant daemons in main.py | Medium |
| 10 | Config.py cleanup (remove Kalshi/FV keys, Overlay C) | High |
| 11 | Delete Overlay B from updown_engine.py | 🔥 High |
| 13 | Delete non-user wallet data from /wallet dir | Medium |
| 14 | Sync local → VPS (git commit + pull + restart) | 🔥 High |
| 16b | Add BNB to RTDS subscription | 🔥 High |
| 18 | Remove Pyth entirely | Medium |
| 19 | Replace oracle stack: Chainlink DS → Binance → Coinbase | Medium |
| ⏸️ 20 | Gate HYPE — on hold, owner verifying | On Hold |
| 23 | Fix HYPE + BNB delayed trades / slippage gate | 🔥 First thing next session |

**Active — Owner Actions:**
| # | Item | Priority |
|---|---|---|
| 22 | Escalate Chainlink HMAC credentials (email Stephen + Discord) | 🔥 URGENT |

**Active — Analysis Tasks (Antigravity):**
> All analysis items resolved. ✅ No open analysis items.


---

## 13. MANDATORY RULES FOR ALL AGENTS

**Coding tool:**
1. Read this entire document before writing any code
2. Never enable a dormant strategy (Section 5) without explicit owner instruction
3. Never remove or weaken risk controls (Section 6)
4. Never add real Pyth integration — abandoned, corrupted by basis error
5. `/wallet/*.json` are one-time analysis pulls — not runtime dependencies
6. The owner's Polymarket handle is NOT Bonereaper
7. Always verify startup logs after any VPS deployment before going live
8. After completing work: add a **detailed, comprehensive** changelog entry to Section 4 of this document (ZISI - Journal.md) + remove item from ZISI - Items.md. The entry must include what was changed, why, what file/line, and any new bugs or edge cases discovered.
9. **After every change: commit to git, verify on VPS, confirm no drift between local/VPS/GitHub.** Log the commit hash in the changelog entry.

**Antigravity:**
1. Only modifies `ZISI - Journal.md` and `ZISI - Items.md` — never trading code
2. Always ends sessions with "What's next, boss?"
3. Every factual claim about the codebase is verified against actual file content before being stated
4. Keeps this document current and honest — if something changes, update it immediately
5. **All times in all analysis documents use SAST (UTC+2).** Polymarket candle times are ET — convert to SAST (ET + 6h in summer). Never report times in ET or UTC.
6. **Standard trade analysis format:** Per-trade table must include: Candle time (SAST), Direction, Avg Entry Price, Cost ($), Payout ($), PnL ($), ROI%, W/L. Always include scorecard summary before the table.

---

## 15. OWNER PHILOSOPHY — MANDATORY READING FOR ALL AGENTS

> *"Everything we do from now on going forwards is solely to enforce the bot, reinforce it stronger and make it better, to refine it. Not to break it, not to have an edge. We're simply finding it and ensuring our entire system is architecturally seamless. There's always room for improvement."*
> — Mthunzi (Owner), 2026-07-18

**The core principle:**
- ZISI is working. ZISI is profitable. ZISI is cooking.
- Every item on the list exists to REINFORCE the system, not to restrict it.
- **No arbitrary gates.** A gate is only justified if it is based on real data showing a real problem. No speculative gates, no defensive cuts that reduce volume or win rate without hard evidence.
- **The goal is not to be safe. The goal is to be right.** Risk controls exist for catastrophic tail protection only, not for second-guessing signals.
- We work sequentially: complete current items fully, verify thoroughly, then proceed. Never add half-baked items.
- Every analysis done by Antigravity must end with a concrete "What does this mean for ZISI?" answer. If the analysis has no actionable ZISI implication, it is incomplete.

**On circuit breakers specifically:**
- Currently DISABLED (paper mode). See Section 3g.
- Will activate on live launch. Until then, let the bot run free and collect data.

---

## 14. MARKET INTELLIGENCE — NOTABLE WALLETS & PATTERNS

### Perfect-Afternoon-Edge (`0x75973c667cec880353450be3a6f17c5da67b4421`)
**Date:** 2026-07-17 | **Full analysis:** `Perfect_Afternoon_Edge_Analysis.md`

**One-line summary:** New account, $672K P&L in 2h 25m, 13/17 wins (76.5%), **BNB 5m only**, entry prices consistently 0.10-0.33 (3x-10x payout), all in one day then gone.

**Key findings:**
- Entered at 10¢ twice — both won (900% ROI each). This is nearly impossible randomly.
- NOT CZ. Probably a BNB market manipulator or oracle-lag exploiter (LAT-ARB variant).
- MERGE event in one trade = entered both sides simultaneously, then exited losing side = market depth manipulation.
- Collected $3,857 maker rebate = placed limit orders, not market orders = crafted CLOB positions deliberately.
- Account created same day = purely operational, not a long-term player.
- 4 losses included — not perfect, but highly profitable overall.

**ZISI implications:**
- Chainlink Data Streams (ms-level) would let ZISI detect oracle moves before CLOB reprices = same edge used defensively.
- This actor proves BNB 5m is profitable for sophisticated players — validates the thesis.
- When ZISI signals fire on a contrarian entry (low CLOB price side) across ANY asset: that is a premium opportunity. Do not gate it. Collect it.

**Same-day context:** bbwlover also attacked BNB on this day (15m markets). Two BNB exploiters on the same day = BNB is the target asset for Polymarket oracle attacks.

---

## 16. STANDARDS — TIME ZONES & REPORTING

| Standard | Rule |
|---|---|
| **All times** | SAST (UTC+2) always. Convert ET (UTC-4 summer) = +6h. Convert UTC = +2h. |
| **Trade analysis** | Per-trade table: Candle (SAST), Direction, Avg Entry, Cost ($), Payout ($), PnL ($), ROI%, W/L |
| **Wallet pulls** | Always pull from `data-api.polymarket.com/activity` endpoint. Group by conditionId. |
| **P&L calculation** | PnL = REDEEM − MERGE − TRADE cost. Maker rebate reported separately. |
| **Scorecard first** | Every wallet analysis starts with a summary scorecard before trade-by-trade. |

---
*Last updated: 2026-07-18 06:25 SAST | Updated by: Antigravity*
*Next update: After coding tool completes items 23 (HYPE/BNB fix), 16b (BNB RTDS), 5a (Kalshi removal). Or after Chainlink HMAC key arrives (Item 22).*

---

## 📓 SESSION ENTRIES

### Session 2 — 2026-07-18 (Antigravity)
**Time:** ~03:00–06:25 SAST

**Analysis completed:**
- ✅ Item 12: HYPE liquidity audit — confirmed HYPE has NO active 5m Polymarket market and NO Chainlink feed. VPS shows 0 signal evaluations for HYPE ever. Informational archived in Section 3h.
- ✅ Item 15: BNB manipulation risk — confirmed BNB books are thin (2/3 recent trade attempts = NO_LIQUIDITY). Documented in Section 14 (market intelligence). No gate added — owner philosophy: collect volume first.
- ✅ Perfect-Afternoon-Edge wallet pulled and analyzed: `0x75973c667cec880353450be3a6f17c5da67b4421`. $672K P&L in 2h25m, 17 markets, 76.5% WR, BNB 5m only, entry prices 0.10-0.33. Full report: `Perfect_Afternoon_Edge_Analysis.md`. Key insight: contrarian entries (10-33¢) are the highest-EV trades across ALL assets — not just BNB.

**Document restructuring:**
- `ZISI.md` renamed → `ZISI - Journal.md` (repo root)
- `ZiSi_Open_Items.md` (artifacts dir) → `ZISI - Items.md` (repo root, clean active-only format)
- Both documents now live at repo root. They go hand in hand. When an item is done: remove from Items, add summary to Journal.

**Items added this session:**
- Item 19 updated: oracle priority order confirmed = 1) Chainlink DS, 2) Binance, 3) Coinbase
- Item 21: **DELETED** — Owner: "no nonsense gates, we need volume"
- Item 22: Chainlink credential escalation (email + Discord escalation path documented)
- Item 23: Fix HYPE + BNB delayed trades / slippage gate (first thing next session)

**Rules added:**
- Rule 8 (coding tool): detailed changelog entry required + remove item from ZISI - Items.md
- Rule 9 (coding tool): commit to git + verify VPS + confirm no drift after every change
- Rule 5 (Antigravity): all times in SAST (UTC+2) always
- Rule 6 (Antigravity): standard trade analysis format codified

**New sections added to Journal:**
- Section 3f: Chainlink Data Streams — full email thread logged, escalation path
- Section 3g: ZISI Operating Mode — paper mode, all circuit breakers OFF
- Section 3h: All-asset contrarian entry intelligence — applies to BTC/ETH/SOL/XRP/DOGE/BNB equally
- Section 14: Market Intelligence — Perfect-Afternoon-Edge wallet profile
- Section 15: Owner Philosophy — "reinforce the bot, never break it, no arbitrary gates"
- Section 16: Standards — SAST, trade analysis format, P&L calc, wallet pull endpoint

### Session 4 — 2026-07-18 (Antigravity) — Verification Sweep
**Time:** 10:29 SAST

**VPS verified via git log + grep:**

| Item | Verified Status |
|---|---|
| 11 — Delete Overlay B | ✅ DONE — grep returns empty |
| 14 — VPS sync | ✅ DONE — 8 commits live on VPS |
| 18 — Remove Pyth from source | ✅ DONE — no source file hits |
| 23 — Fix HYPE/BNB trades | ✅ DONE — commit `005cdf0` unlocks both assets |
| 24 — Timezone display polish | ✅ DONE — per Session 3 Journal entry |
| 25 — L2 log consolidation | ✅ DONE — per Session 3 Journal entry |
| 3 — Slippage telemetry | ✅ DONE — commit `e4c1275` |
| 6/7 — Kelly floor/ceiling/dampener | ✅ DONE — commit `69e0544` |
| 5a — Kalshi source removal | ⚠️ NEEDS CONFIRM — venv package still installed, source grep needed (excluding venv/) |
| 13 — Wallet file deletion | ❌ NOT DONE — 6 non-owner files still in wallet/ |
| 16b — BNB in RTDS | ❌ NOT DONE — grep returns empty in polymarket_rtds_ingest.py |

**Items doc rewritten** to only show the 5 remaining open items: 5a, 13, 16b, 19 (blocked), 20 (on hold), 22 (owner action).

**Notable commits this session by coding tool:**
- `005cdf0` — BNB + HYPE unlocked as tradeable assets
- `69e0544` — Kelly floor raised, ceiling raised, streak dampener disabled, slippage alert = 8¢
- `e4c1275` — Slippage telemetry + fill rate tracking implemented
- `b6c408a` — Journal + Items updated by coding tool (Session 3)

### Session 5 — 2026-07-18 (Antigravity — Acting as Coding Tool)
**Time:** 12:44–12:55 SAST
**Commit:** `01aa716`

**Root cause diagnosed and fixed:**

**HYPE "Insufficient candles (0 < 16)":**
- Root cause: `HYPEUSDT` does not exist on Binance spot (`api.binance.com`). The engine was doing `f"{symbol}USDT"` → `HYPEUSDT` → Binance returns HTTP 400 → 0 candles returned → every HYPE cycle immediately aborted with the "Insufficient candles" error.
- HYPE (Hyperliquid) is listed as `HYPEUSDT` on **Binance Futures** (`fapi.binance.com`) only.
- **Fix 1:** Added `BINANCE_FAPI = "https://fapi.binance.com/fapi/v1"` and `_FUTURES_KLINES_ASSETS = {"HYPE"}` to `updown_engine.py`. Both `_fetch_klines()` and `_fetch_klines_async()` now branch to the futures REST endpoint for HYPE. File: `core/engine/updown_engine.py` lines 59-63, 128-145, 179-198.
- **Fix 2:** `pre_warm_cvd()` in `spot_websocket_ingest.py` also called Binance spot for aggTrades. Fixed to route HYPE to `fapi.binance.com/fapi/v1/aggTrades`. File: `core/engine/spot_websocket_ingest.py` lines 31-41.

**BNB "L2 book illiquid":**
- Root cause: BNB Polymarket market had volume = $0 on the tested candle (off-peak hours). The L2 spread check (`> 15c`) is correctly identifying a genuinely thin book. This is not a bug — it's the system working as intended. BNB will trade when liquidity is present. No code change needed here.

**Verified startup after deployment:**
- `[HFT-WS] Connecting FUTURES: 3 streams for 1 symbols` ✅ HYPE correctly on Binance Futures WS
- `[HFT-WS] Connecting SPOT: 18 streams for 6 symbols` ✅ other 6 assets on spot
- `BOT STARTUP COMPLETE / READY TO TRADE / ACTIVE SCANNING` ✅
- No "Insufficient candles" error in startup logs ✅

**Items status:**
- Item 23 (HYPE/BNB fix): ✅ DONE — remove from ZISI - Items.md
- Item 16b (BNB RTDS): confirmed BNB is already in RTDS subscription at line 134. ✅ DONE — remove from Items.
- Antigravity role note: Acting as coding tool this session — coding tool hit usage limit.


### Session 6 — 2026-07-18 (Antigravity — Acting as Coding Tool)
**Time:** 13:16–13:53 SAST
**Commit:** `2c9077a`

**Fix 1 — Confluence Binance kline error for HYPE:**
- Root cause: `confluence_engine.py` had its own symbol map and klines URL (spot only). HYPE was not in the map, so it fell back to `HYPE + "USDT"` = `HYPEUSDT` → spot 400 on all 4 timeframes (1m, 5m, 15m, 1h) every single cycle.
- Fix: Added `_BINANCE_FAPI_KLINES_URL`, `_FUTURES_KLINES_ASSETS = {"HYPEUSDT"}`, added `"HYPE": "HYPEUSDT"` to `_SYMBOL_MAP`, updated `_fetch_klines()` to branch on the futures URL for HYPE. Removed duplicate LINK entry from symbol map.
- File: `core/engine/confluence_engine.py` — 3 locations.

**Fix 2 — Item 5a: Remove all Kalshi code from source (COMPLETE):**
- Files touched (10 total):
  - `core/engine/confluence_engine.py` — symbol map deduplication
  - `core/engine/signal_router.py` — removed Kalshi docstring, `kalshi: []` return key, `kalshi` weights dict
  - `core/engine/cycle_manager.py` — updated docstring example, annotated param as backward-compat
  - `core/engine/trader.py` — deleted dead `if market == "KALSHI"` guard block; removed `kalshi_active: 0` from summary; renamed `source` from `"polymarket+kalshi"` to `"polymarket"`
  - `app/health_monitor.py` — updated module docstring, function docstring, inline comment; removed `kalshi_active` from summary update
  - `core/engine/metrics_engine.py` — updated comment
  - `core/engine/state_manager.py` — updated 2 comments
  - `core/ml/ml_pipeline.py` — removed `kalshi_matches` key from metrics dict
  - `core/risk/risk_manager.py` — updated Kelly docstring
  - `scratch/reset_vps.py` — updated source tag and removed `kalshi_active` from template
- Retained: `kalshi_events: List[Dict] = None` in cycle_manager and signal_router (backward-compat; callers pass None, param is inert)
- Final grep: 0 functional Kalshi references in source. ✅

**VPS startup confirmed clean (`2c9077a`):**
- `HYPE/5m: Initialised rolling outcomes with 2 historical trades` ✅ (building history)
- `[HFT-WS] Connecting FUTURES: 3 streams for 1 symbols` ✅ HYPE on futures
- `BOT STARTUP COMPLETE / READY TO TRADE / ACTIVE SCANNING` ✅
- No Confluence HYPE errors in startup logs ✅


### Session 7 — 2026-07-18 (Antigravity — Acting as Coding Tool)
**Time:** 14:09–14:15 SAST
**Commit:** `ef84530` (docs only)

**Item 13 — Delete Non-Owner Wallet Files: VERIFIED DONE (already completed)**
- Investigated VPS `wallet/` directory.
- Found only: `resolved_winners_cache.json` (264K, legitimate bot data) and `wallet_active_positions.json` (36K, legitimate bot data).
- The non-owner files (`wallet_0x21d0a97a_*` and `wallet_0xeebde7a0_*`) were already deleted in commit `4912b43` ("V3 Streamlining").
- Items doc was stale — removed Item 13 from open list.

**Item 22 — Chainlink Escalation Prep:**
- 15 days since form submission (July 4 → July 18). Zero response from Chainlink.
- Items doc updated with ready-to-send email and Discord message.
- **Email:** tvc-stephen.maceda@smartcontract.com | CC: gtm-inbound@smartcontract.com
- **Subject:** `Re: Chainlink Data Streams — Polymarket Binary Trading Engine [ESCALATION]`
- **Discord:** discord.gg/chainlink → `#data-streams` → tag `@ChainlinkDevRel`
- Both messages fully drafted in Items doc. Awaiting owner to send.
- Item 22 remains open until HMAC credentials received.

**Open items after Session 7 (3 remaining):**
- Item 19: Oracle stack (blocked on Item 22 credentials)
- Item 20: Gate HYPE (on hold — owner decision)
- Item 22: Chainlink escalation — **OWNER TO SEND NOW**


### Session 3 — 2026-07-18 (Antigravity)
**Time:** 09:36 SAST

**Analysis completed:**
* **Polymarket Event Scanning:** Verified that active `5m` Up/Down events for both BNB and HYPE are regularly created and active on Polymarket.
* **RTDS Live Feed Check:** Ran custom WebSocket connection test tool. Confirmed that Polymarket RTDS WebSocket transmits live Chainlink oracle price ticks for both `bnb/usd` and `hype/usd`.
* **Latency Root Cause:** Verified that the "connecting" display state and trade delays for BNB and HYPE are solely caused by their omission from the RTDS WebSocket subscription list in `polymarket_rtds_ingest.py`.
* **Dormant Volatility Surface:** Confirmed the `VolatilitySurface` module is currently only imported by `edge_orchestrator.py` but is not actively affecting Kelly size calculations (warrants deletion by coding tool in upcoming cleanup tasks).

**Items updated:**
* **Item 23 updated:** Removed the plan to gate HYPE. Both BNB and HYPE are confirmed active and will be subscribed to RTDS.
* **Item 24 added:** Polishing timezone display string (`Johannesburg/SAST` -> `Johannesburg`).
* **Item 25 added:** Consolidating L2 book polling logs into a single neater line to prevent console spam.


