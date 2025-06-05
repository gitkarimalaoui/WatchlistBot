# scripts/init_qlib_check.py
import qlib
from qlib.data import D
from qlib.config import REG_US
import pandas as pd
import sys

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")

# ✅ Initialize Qlib with local US data
qlib.init(provider_uri="./qlib_data", region=REG_US)

# ✅ Try to load features for a sample ticker (e.g. AAPL)
try:
    df = D.features(["AAPL"], ["$close", "$volume"], start_time="2023-01-01", end_time="2023-01-10")
    print("\n📊 Sample data from Qlib (AAPL):")
    print(df.head())
    print("\n✅ Qlib is working correctly with local US stock data.")
except Exception as e:
    print("❌ Error loading data:", e)
