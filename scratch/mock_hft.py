import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
os.makedirs(data_dir, exist_ok=True)
target = os.path.join(data_dir, "hft_metrics.json")

data = {
  "BTC": { "cvd_fast": 245.2, "obi": 0.12 },
  "ETH": { "cvd_fast": -15.0, "obi": -0.08 },
  "SOL": { "cvd_fast": 42.1, "obi": 0.07 },
  "XRP": { "cvd_fast": 0.0, "obi": 0.02 },
  "DOGE": { "cvd_fast": -124.5, "obi": -0.11 }
}

with open(target, "w") as f:
    json.dump(data, f, indent=4)
print("Wrote mock metrics successfully.")
