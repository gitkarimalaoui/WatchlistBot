import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from pathlib import Path

# 1️⃣ Config
ROOT_DIR = Path(__file__).resolve().parent.parent
HIST_DIR = ROOT_DIR / "scripts" / "data" / "historical"
MODEL_OUT = ROOT_DIR / "models" / "modele_ia.pkl"

# 2️⃣ Charger tous les CSV daily 2y nettoyés
csv_files = sorted(HIST_DIR.glob("*_2y_daily.csv"))
tickers = [f.stem.replace("_2y_daily", "") for f in csv_files]

# Stocker les arrays
data_arrays = []
close_arrays = []
for f in csv_files:
    df = pd.read_csv(f, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    # Features: Open, High, Low, Close, Adj Close, Volume
    data_arrays.append(df[["Open","High","Low","Close","Adj Close","Volume"]].values)
    close_arrays.append(df["Close"].values)

# 3️⃣ Empiler
# data_arrays: list of (T,6) arrays → shape (T,6,N)
X3 = np.stack(data_arrays, axis=2)
# close_arrays: list of (T,) → shape (T,N)
C3 = np.stack(close_arrays, axis=1)

# 4️⃣ Préparer X_train et y_train
# Drop last row for features
X = X3[:-1].reshape(X3.shape[0]-1, -1)       # (T-1, 6*N)
# Target: next-day close > current-close
y = (C3[1:] > C3[:-1]).astype(int).ravel()   # ( (T-1)*N, )

print(f"Prepared X shape: {X.shape}, y length: {len(y)}")

# 5️⃣ Entraînement
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X, y)
print("Model training completed.")

# 6️⃣ Sauvegarde
MODEL_OUT.parent.mkdir(exist_ok=True)
joblib.dump(model, str(MODEL_OUT))
print(f"✔ Saved model to {MODEL_OUT}")
