"""
auto_redeemer.py — Automatic On-Chain USDC Redemption for Polymarket

Invokes the Conditional Tokens Framework (CTF) contract on Polygon mainnet
to automatically burn winning outcome shares and claim USDC back to the wallet
without requiring manual clicks on the Polymarket Web UI.

CTF Contract (Polygon): 0x4D97DCd97eC945f40cF65F87097ACe5EA0476045
Collateral Token (USDC.e): 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, List

log = logging.getLogger("zisi.auto_redeemer")

# CTF & Polygon Constants
CTF_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
POLYGON_RPC_URLS = [
    "https://polygon-rpc.com",
    "https://rpc.ankr.com/polygon",
    "https://1rpc.io/matic"
]

# Standard CTF redeemPositions ABI
CTF_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "collateralToken", "type": "address"},
            {"name": "parentCollectionId", "type": "bytes32"},
            {"name": "conditionId", "type": "bytes32"},
            {"name": "indexSets", "type": "uint256[]"}
        ],
        "name": "redeemPositions",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def _get_web3():
    try:
        from web3 import Web3
        for rpc in POLYGON_RPC_URLS:
            try:
                w3 = Web3(Web3.HTTPProvider(rpc, timeout=10))
                if w3.is_connected():
                    return w3
            except Exception:
                continue
    except ImportError:
        log.warning("[REDEEMER] web3 package not installed")
    return None

def auto_redeem_condition(condition_id: str) -> bool:
    """
    Execute on-chain redeemPositions for a specific conditionId.
    Returns True if transaction submitted successfully.
    """
    if not condition_id:
        return False

    pk = os.getenv("POLYMARKET_PRIVATE_KEY") or os.getenv("PRIVATE_KEY") or os.getenv("PK")
    if not pk:
        log.debug("[REDEEMER] No private key found in .env for on-chain auto-redemption")
        return False

    if not pk.startswith("0x"):
        pk = "0x" + pk

    w3 = _get_web3()
    if not w3:
        log.warning("[REDEEMER] Could not connect to Polygon RPC for auto-redemption")
        return False

    try:
        from eth_account import Account
        account = Account.from_key(pk)
        sender_address = account.address

        # Ensure condition_id is bytes32 format
        cond_str = condition_id.strip()
        if cond_str.startswith("0x"):
            cond_bytes32 = bytes.fromhex(cond_str[2:])
        else:
            cond_bytes32 = bytes.fromhex(hex(int(cond_str))[2:].zfill(64))

        parent_collection_id = bytes(32)  # bytes32(0)
        index_sets = [1, 2]  # Binary outcome sets: [1, 2]

        ctf_contract = w3.eth.contract(
            address=w3.to_checksum_address(CTF_ADDRESS),
            abi=CTF_ABI
        )

        tx = ctf_contract.functions.redeemPositions(
            w3.to_checksum_address(USDC_ADDRESS),
            parent_collection_id,
            cond_bytes32,
            index_sets
        ).build_transaction({
            "from": sender_address,
            "nonce": w3.eth.get_transaction_count(sender_address),
            "gas": 150000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 137  # Polygon Mainnet
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = w3.to_hex(tx_hash)

        log.info("[REDEEMER] Auto-redeemed condition %s on-chain | Tx: %s", condition_id[:16], tx_hash_hex)
        return True

    except Exception as e:
        log.debug("[REDEEMER] Auto-redemption note for condition %s: %s", condition_id[:16], e)
        return False

def scan_and_auto_redeem() -> int:
    """
    Scan resolved trades in positions state and execute auto-redemption for any unredeemed conditions.
    """
    redeemed_count = 0
    try:
        from core.engine.state_manager import get_positions_file
        pos_file = get_positions_file()
        if not pos_file.exists():
            return 0

        data = json.loads(pos_file.read_text(encoding="utf-8"))
        closed_trades = data.get("closed", [])

        for trade in closed_trades:
            if trade.get("redeemed"):
                continue

            cond_id = trade.get("conditionId") or trade.get("market_id")
            pnl = float(trade.get("realized_pnl") or 0.0)

            # Auto-redeem winning trades
            if cond_id and pnl > 0:
                success = auto_redeem_condition(cond_id)
                if success:
                    trade["redeemed"] = True
                    redeemed_count += 1

    except Exception as e:
        log.debug("[REDEEMER] Error during scan_and_auto_redeem: %s", e)

    return redeemed_count
