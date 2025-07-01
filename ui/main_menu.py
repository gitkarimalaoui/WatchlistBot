import streamlit as st
from pathlib import Path

st.set_page_config(page_title="WatchlistBot - Menu", layout="centered")

st.title("🗂️ Menu principal")

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
]

for script, label in PAGES:
    path = Path(__file__).parent / script
    if path.exists():
        st.page_link(str(path), label=label)
    else:
        st.markdown(f"`{label}` introuvable : {path}")
