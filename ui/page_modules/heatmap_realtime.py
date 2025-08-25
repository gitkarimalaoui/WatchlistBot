import sqlite3
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from streamlit_autorefresh import st_autorefresh
from core.db import DB_PATH

from data.stream_data_manager import set_watchlist, get_latest_data
from intelligence.ai_scorer import compute_global_score

st.set_page_config(page_title="Heatmap IA", layout="wide")
st.title("🔥 Heatmap IA temps réel")

if st_autorefresh:
    st_autorefresh(interval=10 * 1000)


@st.cache_data
def load_scores() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT w.ticker, COALESCE(w.score,0) AS score_ai,
               COALESCE(ns.score,0) AS score_gpt,
               COALESCE(w.float_shares,0) AS float_shares,
               COALESCE(ns.sentiment,'NA') AS sentiment
        FROM watchlist w
        LEFT JOIN news_score ns ON w.ticker = ns.symbol
        """,
        conn,
    )
    conn.close()
    return df

def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    df["global_score"] = df.apply(
        lambda r: compute_global_score(
            r["score_ai"],
            r["score_gpt"],
            0,
            0,
            r["float_shares"],
            r["sentiment"],
        ),
        axis=1,
    )
    return df[["ticker", "global_score"]]

df = load_scores().drop_duplicates(subset="ticker")
tickers: List[str] = df["ticker"].tolist()
set_watchlist(tickers)

scores = compute_scores(df)
heatmap_data = scores.set_index("ticker").T
fig = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdYlGn",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Dernières variations > 1.5%")
for tic in tickers:
    data = get_latest_data(tic)
    pct = data.get("pump_pct_60s", 0)
    if pct > 1.5:
        color = "🟢" if pct > 2.5 else "🟠"
        st.write(f"{color} {tic} +{pct:.2f}% (60s)")

st.markdown("### Dernières données")
for tic in tickers:
    data = get_latest_data(tic)
    st.write(tic, data)
