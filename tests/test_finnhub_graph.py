
import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt

# === Paramètres ===
FINNHUB_API_KEY = "cvs634hr01qvc2mv1e00cvs634hr01qvc2mv1e0g"
symbol = st.text_input("Entrez un ticker (ex: TSLA)", "TSLA")

# === Récupération des données Finnhub (bougies 1 minute) ===
now = datetime.datetime.utcnow()
from_time = int((now - datetime.timedelta(hours=6)).timestamp())
to_time = int(now.timestamp())

url = "https://finnhub.io/api/v1/stock/candle"
params = {
    "symbol": symbol,
    "resolution": "1",
    "from": from_time,
    "to": to_time,
    "token": FINNHUB_API_KEY
}

resp = requests.get(url, params=params)
data = resp.json()

st.subheader("📊 Données brutes reçues")
st.json(data)

if data.get("s") == "ok" and data.get("c"):
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(data["t"], unit="s"),
        "close": data["c"]
    }).set_index("timestamp")

    st.subheader("📈 Graphique")
    fig, ax = plt.subplots()
    ax.plot(df.index, df["close"], label="Clôture 1min")
    ax.set_title(f"{symbol} – Données 1min")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("❌ Aucune donnée graphique disponible ou format invalide.")
