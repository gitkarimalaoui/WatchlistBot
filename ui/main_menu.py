import streamlit as st
from pathlib import Path
import sqlite3
import pandas as pd

st.set_page_config(page_title="WatchlistBot - Menu", layout="centered")

st.title("🗂️ Menu principal")


@st.cache_data(ttl=15)
def read_top_scores(limit: int = 10) -> pd.DataFrame:
    db = Path(__file__).resolve().parents[1] / "data" / "trades.db"
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(
        "SELECT symbol, score FROM scores ORDER BY score DESC LIMIT ?",
        conn,
        params=(limit,),
    )
    conn.close()
    return df

st.sidebar.dataframe(read_top_scores())

PAGES = [
    ("dashboard/dashboard.py", "📊 Dashboard"),
    ("app_unifie_watchlistbot.py", "📈 WatchlistBot V7"),
    ("journal.py", "📓 Journal"),
    ("trading_manuel.py", "🛠️ Trading manuel"),
    ("simulation_achat.py", "🟢 Simulation achat"),
    ("simulation_vente.py", "🔴 Simulation vente"),
    ("control_center/ia_control_center.py", "🧠 IA Control Center"),
    ("backtest_ui/ai_backtest.py", "🤖 AI Backtest"),
    ("formation_ai.py", "🎓 Formation IA"),
    ("menu_strategie_personnelle.py", "📌 Plan Stratège Visionnaire"),
]

for script, label in PAGES:
    path = Path(__file__).parent / script
    if path.exists():
        st.page_link(str(path), label=label)
    else:
        st.markdown(f"`{label}` introuvable : {path}")
