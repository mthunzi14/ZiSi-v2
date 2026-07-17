# ZiSi Core: High-Frequency Prediction Market Execution Framework

ZiSi (formerly ZC) is a high-performance, event-driven trading execution framework designed for binary prediction market contracts. It integrates ultra-low-latency real-time ingestion, dynamic regime filtering, and multi-tranche execution optimization.

---

## 1. System Architecture

The ZiSi framework is divided into four main layers:

```
+-------------------------------------------------------------+
|                      INGESTION LAYER                        |
|   - Real-Time Polymarket CLOB WebSocket Gateway             |
|   - Binance Tick & Spot Price Feeds                         |
|   - Chainlink Oracle Price Feeds                            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                        ENGINE LAYER                         |
|   - Dynamic Market Regime Classifier                        |
|   - Order Flow Imbalance (OFI) & Cumulative Volume Delta    |
|   - Real-Time Signal Inversion Module                       |
|   - Fractional Kelly Position Sizer                         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      EXECUTION LAYER                        |
|   - Multi-Tranche Scale Management (ES & EX Tranches)       |
|   - Breakeven Stop-Loss Lock-in                             |
|   - Adaptive Slippage Protection Gates                      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     PRESENTATION LAYER                      |
|   - Real-Time Rich Text Terminal Dashboard                  |
|   - Performance Analytics & Trajectory Tracker              |
|   - Multi-Asset Exposure Monitoring                         |
+-------------------------------------------------------------+
```

---

## 2. Core Execution Model

The system trades contract wiggles using a multi-tranche scale management model:

* **Tranche A (Early Scalping - ES)**: Designed to lock in quick profits. It exits half of the active position at a near-entry target.
* **Tranche B (Extended Execution - EX)**: Designed to let runners capture wider price wiggles. Once Tranche A exits, the stop-loss for Tranche B is automatically moved to the entry price (breakeven), protecting the trade from downside risk.

---

## 3. Installation & Setup

### Prerequisites
* Python 3.9+
* Node.js / PM2 (for process management)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ZiSi-v2.git
   cd ZiSi-v2
   ```
2. Set up the virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

### Running the System
To start the core execution engine:
```bash
pm2 start app/main.py --name "ZiSi-Core-Engine"
```

To run the terminal dashboard:
```bash
python zisi_terminal.py
```

---

## 4. Test Suite

The project includes a robust suite of unit tests to verify the integrity of the engine, filters, and execution logic.

To run the entire test suite:
```bash
python -m unittest discover -s test
```
