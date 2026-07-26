# 📘 Complete Polymarket Bot Architecture, Diagnostic & Fix Blueprint

> **Target Repository:** [ZiSi-v2](https://github.com/mthunzi14/ZiSi-v2)  
> **Primary Purpose:** Comprehensive diagnostic report for the user and external coding tools to resolve zero-balance web UI issues, paper-trading fallbacks, and live execution setup.  
> **Verification Method:** Direct Polygon Mainnet RPC On-Chain Call + Codebase Inspection of `config.py`.

---

## 🎯 1. Verified Wallet & Account Architecture

| Wallet Type | Ethereum / Polygon Address | On-Chain Token Balance | Function & Web UI Behavior |
| :--- | :--- | :--- | :--- |
| **API Wallet (EOA / Signer)** | `0xC91627Ee52494F2D2276aD13Dae06151E28DaCCC` | **32.774702 USDC.e**<br>0.000000 POL | Holds current funds.<br>Polymarket Web UI ignores this address (shows Cash $0.00). |
| **Proxy Vault (Gnosis Safe)** | `0x93B0658176Cb44e8B9FBc3256266f9D66053596F` | **0.000000 USDC.e** | Main Polymarket Account.<br>Polymarket Web UI header reads Cash balance directly from here. |

### Key On-Chain Facts:
1. **Funds are 100% Intact:** Your **$32.77** is safely sitting on-chain in `0xC91627Ee52494F2D2276aD13Dae06151E28DaCCC`.
2. **Correct Token Contract:** The token is **Bridged `USDC.e`** (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`). **No token swap/conversion is needed.**
3. **Proxy Address Confirmed:** Address `0x93B0658176Cb44e8B9FBc3256266f9D66053596F` is confirmed in your UI screenshot and in `ZiSi-v2/config.py` line 144 as your official **Proxy Vault**.

---

## 💡 2. Resolution of Core Concepts & Misconceptions

### A. Why Does Polymarket Web UI Display `Cash = $0.00`?
* The Polymarket Web Header (`Portfolio $0.00 | Cash $0.00`) is hardcoded to query **only your Proxy Vault (`0x93B0...`)**.
* Because the $32.77 was deposited into your **API Wallet (`0xC91627...`)**, the website displays $0.00.
* The system warning under your API key in settings (*"Do not send funds to this address. For API use only"*) is put there by Polymarket specifically to prevent users from getting confused when the website header displays $0.00. **Your funds are not lost or burned.**

### B. Do You Need POL Tokens for Trading?
* **For Trading on Polymarket (Option B - Industry Standard):** **NO.** Polymarket utilizes a **Gasless Relayer** for Gnosis Safe Proxy Vault accounts. Polymarket pays 100% of the Polygon gas fees for your trade orders automatically.
* **For the One-Time Transfer:** To execute the single transaction moving $32.77 `USDC.e` out of your API wallet (`0xC91627...`) into your Proxy Vault (`0x93B0...`), Polygon requires a tiny fraction of **POL** (**~0.02 POL, which is under $0.002**) to pay the network transaction fee.
* **Current Waiting Status:** You are currently waiting for your POL withdrawal to arrive on Monday (due to VALR 2FA security unlock). Once POL arrives in `0xC91627...`, you can execute the one-time transfer immediately.

### C. Why Option B (Proxy Vault) is the Industry Standard for Bots:
1. **Live Web Dashboard:** Polymarket Web UI displays your real-time Cash balance ($32.77), open orders, active positions, and closed trade history.
2. **Zero Gas Fees:** The bot trades using Polymarket’s Gasless Relayer, eliminating the need to manage POL gas balances for trades.
3. **Native Support in `ZiSi-v2`:** The codebase is pre-configured for this via `POLYMARKET_PROXY_ADDRESS`.

---

## 🛠️ 3. Step-by-Step Fix Instructions for External Coding Tools

When your POL arrives on Monday, follow these exact 2 steps to activate live trading:

### Step 1: Execute 1-Time Transfer (API Wallet -> Proxy Vault)

Run this Python script on your local machine or VPS to transfer the $32.77 `USDC.e` to your Proxy Vault:

```python
"""
transfer_to_proxy_vault.py
Transfers USDC.e from API Wallet (0xC91627...) to Proxy Vault (0x93B0...)
"""
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://polygon-bor-rpc.publicnode.com"))

API_PRIVATE_KEY = "YOUR_API_WALLET_PRIVATE_KEY"
API_WALLET = "0xC91627Ee52494F2D2276aD13Dae06151E28DaCCC"
PROXY_VAULT = "0x93B0658176Cb44e8B9FBc3256266f9D66053596F"
USDC_E_CONTRACT = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

abi = [{
    "constant": False,
    "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
    "name": "transfer",
    "outputs": [{"name": "", "type": "bool"}],
    "type": "function"
}]

contract = w3.eth.contract(address=w3.to_checksum_address(USDC_E_CONTRACT), abi=abi)
amount_units = 32774702  # 32.774702 USDC.e (6 decimals)

tx = contract.functions.transfer(
    w3.to_checksum_address(PROXY_VAULT), 
    amount_units
).build_transaction({
    'from': w3.to_checksum_address(API_WALLET),
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(API_WALLET)),
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
    'chainId': 137
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key=API_PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("✅ Transfer Submitted! Transaction Hash:", w3.to_hex(tx_hash))
```

---

### Step 2: Configure `.env` on VPS (`ZiSi-v2`)

Update `.env` in your `ZiSi-v2` root directory on your VPS:

```env
# ── Polymarket API Endpoints ──────────────────────────────────────────────────
POLYMARKET_GAMMA_API_URL=https://gamma-api.polymarket.com
POLYMARKET_DATA_API_URL=https://data-api.polymarket.com
POLYMARKET_CLOB_API_URL=https://clob.polymarket.com

# ── Wallet & Proxy Credentials ───────────────────────────────────────────────
POLYMARKET_PRIVATE_KEY=YOUR_API_PRIVATE_KEY_HERE
POLYMARKET_PROXY_ADDRESS=0x93B0658176Cb44e8B9FBc3256266f9D66053596F

# ── Mode Selection ───────────────────────────────────────────────────────────
BOT_MODE=live_trading
IS_LIVE=true
```

---

## 🏁 Summary Checklist for the Next Session

- [x] **Verified Funds:** $32.77 `USDC.e` safe on Polygon Mainnet.
- [x] **Verified Proxy Vault:** Address `0x93B0658176Cb44e8B9FBc3256266f9D66053596F` confirmed.
- [x] **Verified Token:** Bridged `USDC.e` confirmed. No token swap required.
- [ ] **Awaiting POL (Monday):** Need ~0.05 POL in `0xC91627...` to trigger the 1-time transfer.
- [ ] **Execute Transfer:** Run `transfer_to_proxy_vault.py`.
- [ ] **Enable Live Trading:** Set `BOT_MODE=live_trading` in `.env` on VPS.
