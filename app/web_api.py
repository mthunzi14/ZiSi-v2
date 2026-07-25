#!/usr/bin/env python3
"""
app/web_api.py — ZiSi-v2 Read-Only Dashboard Telemetry API
Runs isolated on Port 9000. Provides 100% read-only data streams for the React Web Terminal.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("zisi_web_api")

app = FastAPI(title="ZiSi-v2 Telemetry API", version="2.0.0")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_DIR = PROJECT_ROOT / "data"
ACCOUNT_STATE_FILE = DATA_DIR / "account_state.json"
POSITIONS_STATE_FILE = DATA_DIR / "positions_state.json"
LOG_FILE = PROJECT_ROOT / "zisi_bot_console.log"


@app.get("/")
def read_root():
    return {"status": "ONLINE", "engine": "ZiSi-v2 Telemetry Stream", "port": 9000}


@app.get("/api/telemetry")
def get_telemetry():
    """Read-only account state & balance telemetry."""
    if not ACCOUNT_STATE_FILE.exists():
        return JSONResponse(content={"error": "account_state.json not found"}, status_code=404)
    try:
        with open(ACCOUNT_STATE_FILE, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/positions")
def get_positions():
    """Read-only active and closed trade positions state."""
    if not POSITIONS_STATE_FILE.exists():
        return JSONResponse(content={"active": [], "closed": [], "summary": {}}, status_code=200)
    try:
        with open(POSITIONS_STATE_FILE, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/logs")
def get_logs(limit: int = 100):
    """Read-only recent log lines from zisi_bot_console.log."""
    if not LOG_FILE.exists():
        return {"logs": []}
    try:
        with open(LOG_FILE, "r", errors="replace") as f:
            lines = f.readlines()
        return {"logs": [line.strip() for line in lines[-limit:]]}
    except Exception as e:
        return {"error": str(e), "logs": []}


if __name__ == "__main__":
    import uvicorn
    log.info("Starting ZiSi-v2 Read-Only Telemetry API on Port 9000...")
    uvicorn.run(app, host="0.0.0.0", port=9000)
