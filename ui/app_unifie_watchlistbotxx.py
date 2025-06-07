import os
import sys
import subprocess
import sqlite3
import math
from datetime import datetime

import pandas as pd
import streamlit as st

# ─── Configuration de la page ───────────────────────────────────────────────────
st.set_page_config(page_title="WatchlistBot V7", layout="wide")

# ─── Définition des chemins ─────────────────────────────────────────────────────
ROOT_UI = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(ROOT_UI, ".."))
SCRIPTS = os.path.join(ROOT_DIR, "scripts")
UTILS = os.path.join(ROOT_DIR, "utils")
SIMULATION = os.path.join(ROOT_DIR, "simulation")

# ─── Ajout des chemins au système ───────────────────────────────────────────────
for path in (ROOT_DIR, SCRIPTS, ROOT_UI, UTILS, SIMULATION):
    if path not in sys.path:
        sys.path.insert(0, path)

# ─── Imports locaux ─────────────────────────────────────────────────────────────
from roadmap_ui import roadmap_interface, roadmap_productivity_block, personal_interface
from query_entreprise_db import get_portfolio_modules, get_use_cases, get_revenue_sources, get_kpi_targets
from pages.cloture_journee import cloturer_journee
from utils_affichage_ticker import afficher_ticker_panel

# ─── Définition chemin base SQLite ──────────────────────────────────────────────
DB_PATH = os.path.join(ROOT_DIR, "data", "trades.db")

# ─── Menu latéral ──────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🚀 Navigation")
page = st.sidebar.radio("Menu principal", [
    "📊 Watchlist", 
    "📋 Roadmap", 
    "🏢 Entreprise", 
    "🧘 Personal", 
    "📦 Clôture", 
    "📄 Trades simulés"
], index=0)

# ─── Pages secondaires ─────────────────────────────────────────────────────────
if page == "📋 Roadmap":
    roadmap_interface()
    roadmap_productivity_block()
    st.stop()

if page == "🏢 Entreprise":
    st.title("🏢 Entreprise IA & Solutions d’Architecture")
    st.dataframe(get_portfolio_modules(), use_container_width=True)
    st.stop()

if page == "🧘 Personal":
    personal_interface()
    st.stop()

if page == "📦 Clôture":
    cloturer_journee()
    st.stop()

# ─── Page : Trades simulés ─────────────────────────────────────────────────────
if page == "📄 Trades simulés":
    st.title("📄 Historique des trades simulés")
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM trades_simules ORDER BY date_achat DESC", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur chargement trades : {e}")
    st.stop()

# ─── Watchlist ─────────────────────────────────────────────────────────────────
st.title("📊 WatchlistBot – Version V7")

def count_watchlist_tickers():
    conn = sqlite3.connect(DB_PATH)
    cnt = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    conn.close()
    return cnt

@st.cache_data
def load_watchlist():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT
            w.ticker,
            w.source,
            w.date,
            w.description,
            COALESCE(w.score, 0) AS score,
            COALESCE(ns.score, 0) AS score_gpt,
            COALESCE(ns.sentiment, 'NA') AS sentiment,
            i.price,
            i.volume,
            i.change_percent AS percent_gain
        FROM watchlist w
        LEFT JOIN news_score ns ON w.ticker = ns.symbol
        LEFT JOIN (
            SELECT s.ticker, s.price, s.volume, s.change_percent, s.timestamp
            FROM intraday_smart s
            JOIN (
                SELECT ticker, MAX(timestamp) AS max_ts
                FROM intraday_smart
                GROUP BY ticker
            ) m ON s.ticker = m.ticker AND s.timestamp = m.max_ts
        ) i ON w.ticker = i.ticker
        """,
        conn,
    )
    conn.close()
    return df.to_dict(orient='records')

# ➕ Ajout manuel
st.markdown("### ➕ Ajouter un ticker manuellement")
with st.expander("Saisie manuelle"):
    new_tic = st.text_input("Ticker", key="manual_ticker")
    new_desc = st.text_area("Description", key="manual_desc")
    if st.button("Ajouter", key="manual_add"):
        if new_tic and new_desc:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT OR REPLACE INTO watchlist (ticker, source, date, description, updated_at) VALUES (?, 'Manual', ?, ?, CURRENT_TIMESTAMP)",
                (new_tic.upper(), datetime.now().isoformat(), new_desc)
            )
            conn.commit()
            conn.close()
            st.success(f"{new_tic.upper()} ajouté !")
            st.experimental_rerun()
        else:
            st.warning("Veuillez renseigner ticker et description.")

# 🤖 Analyse GPT
col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("### 🤖 Analyse batch ChatGPT")
    auto_batch = st.checkbox("Activer analyse batch automatique", key="auto_batch")

    def run_and_show():
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "run_chatgpt_batch.py")], capture_output=True, text=True)
        if proc.returncode != 0:
            st.error(f"Batch failed:\n{proc.stderr}")
            return
        st.success("✅ Analyse GPT terminée.")
        conn = sqlite3.connect(DB_PATH)
        df_scores = pd.read_sql_query("SELECT * FROM news_score", conn)
        conn.close()
        st.dataframe(df_scores)

    if st.button("🚀 Lancer analyse GPT", key="btn_batch") or auto_batch:
        run_and_show()

# 📥 Scraping Jaguar
with st.expander("📥 Scraper Jaguar et Injecter"):
    if st.button("🔄 Scraper depuis Moomoo"):
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "scraper_jaguar.py")])
        try:
            path = os.path.join(ROOT_DIR, "data", "watchlist_jaguar.txt")
            with open(path, "r", encoding="utf-8") as f:
                lst = [l.strip() for l in f if l.strip()]
            st.success(f"✅ Scraping terminé. {len(lst)} tickers extraits.")
        except FileNotFoundError:
            st.warning("⚠️ Fichier Jaguar introuvable.")

    if st.button("📩 Injecter dans la base"):
        before = count_watchlist_tickers()
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "load_watchlist.py")])
        after = count_watchlist_tickers()
        st.success(f"✅ {after - before} tickers injectés dans la base.")
    if st.button("🔁 Rafraîchir la watchlist"):
         st.rerun()


with st.expander("📥 Données marché – Historique et Intraday"):
    st.markdown("Génère les données depuis l’API Yahoo Finance pour tous les tickers de la base (7d/1min + 2y/daily).")
    if st.button("🟢 Lancer collecte et enregistrement DB"):
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "collect_historical_batch_to_db.py")],
            capture_output=True, text=True
        )
        if proc.returncode == 0:
            st.success("✅ Collecte et insertion en base terminées avec succès.")
            st.code(proc.stdout)
        else:
            st.error("❌ Échec pendant la collecte.")
            st.code(proc.stderr)

# 💼 Affichage dynamique paginé
watchlist = load_watchlist()
score_min = st.sidebar.slider("🎯 Score IA minimum", 0, 10, 0)
filtered_watchlist = [w for w in watchlist if w.get("score", 0) >= score_min]

page_size = 10
total = len(filtered_watchlist)
page_num = st.sidebar.number_input("Page", min_value=1, max_value=(total // page_size + 1), value=1)
start = (page_num - 1) * page_size
end = start + page_size
paginated_watchlist = filtered_watchlist[start:end]

st.caption(f"{total} tickers chargés | Page {page_num}/{(total // page_size + 1)}")

for i, stock in enumerate(paginated_watchlist):
    ticker = stock.get('ticker')
    if ticker:
        afficher_ticker_panel(ticker, stock, i)

st.markdown("---")
st.markdown(f"© WatchlistBot V7 – {datetime.now().year}")


from postmarket_scanner import scan_postmarket_watchlist
from ai_scorer import score_ai
from order_executor import executer_order_simule
from telegram_alert import send_telegram_alert



with st.expander("📈 Scanner Pre/Post-Market"):
    if st.button("Lancer le scan Pre/Post-Market"):
        results = scan_postmarket_watchlist()
        st.write(results)

with st.expander("🤖 Score IA Pondéré"):
    dummy_data = {"percent_change": 12, "volume": 1500000, "float": 48000000}
    score = score_ai(dummy_data)
    st.success(f"Score IA pour ticker fictif : {score}/10")

with st.expander("💰 Exécuter un ordre simulé"):
    ticker = st.text_input("Ticker", "")
    prix = st.number_input("Prix d'achat", min_value=0.0, value=1.0)
    quantite = st.number_input("Quantité", min_value=1, value=100)
    if st.button("Exécuter l'ordre simulé"):
        res = executer_order_simule(ticker, prix, quantite)
        st.success(f"Ordre simulé exécuté : {res}")

with st.expander("📢 Alerte Telegram"):
    message = st.text_area("Message à envoyer")
    if st.button("Envoyer l'alerte Telegram"):
        if send_telegram_alert(message):
            st.success("✅ Alerte envoyée.")
        else:
            st.error("❌ Échec de l'envoi.")
