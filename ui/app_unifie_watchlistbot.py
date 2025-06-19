import os
import sys
import subprocess
import sqlite3
import math
import json
from datetime import datetime
import threading
import time

import pandas as pd
import streamlit as st
import requests

# ─── Configuration de la page ───
st.set_page_config(page_title="WatchlistBot V7", layout="wide")


# ─── Gestion URL ticker ───
params = st.query_params
if "ticker" in params:
    st.session_state["ticker_focus"] = params.get_all("ticker")[0]

# ─── Définition des chemins ───
ROOT_UI = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(ROOT_UI, ".."))
SCRIPTS = os.path.join(ROOT_DIR, "scripts")
UTILS = os.path.join(ROOT_DIR, "utils")
SIMULATION = os.path.join(ROOT_DIR, "simulation")
TASKS_JSON_PATH = os.path.join(ROOT_DIR, "refactor_tasks.json")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ─── Ajout des chemins au système ───
for path in (ROOT_DIR, SCRIPTS, ROOT_UI, UTILS, SIMULATION):
    if path not in sys.path:
        sys.path.insert(0, path)

# ─── Imports locaux ───
from notifications.proactive_voice import ProactiveVoiceNotifier
from monitoring.watchdog_conditions import start_watchdog_thread

# ─── Notifications vocales ───
notifier = ProactiveVoiceNotifier()


def loop_notifications() -> None:
    while True:
        notifier.run_pending()
        time.sleep(5)

# ─── Gestion des tâches de refactor ───
def load_refactor_tasks(path: str = TASKS_JSON_PATH):
    """Load refactor tasks from ``path`` if the file exists."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_refactor_tasks(tasks, path: str = TASKS_JSON_PATH) -> None:
    """Save ``tasks`` list of dicts to ``path`` in JSON format."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

# ─── Imports locaux ───
from roadmap_ui import (
    roadmap_interface,
    roadmap_productivity_block,
    personal_interface,
    watchlist_kpi_dashboard,
)
from query_entreprise_db import get_portfolio_modules, get_use_cases, get_revenue_sources, get_kpi_targets
from pages.cloture_journee import cloturer_journee
from utils_affichage_ticker import (
    afficher_ticker_panel,
    _ia_score,
    afficher_bloc_ticker,
)
from utils.execution_reelle import executer_ordre_reel
from execution.strategie_scalping import executer_strategie_scalping
from intelligence.ai_scorer import compute_global_score
from utils.progress_tracker import load_progress
from utils.fda_fetcher import fetch_fda_data, enrichir_watchlist_avec_fda
from utils.utils_news import fetch_news_finnhub
from intelligence.local_llm import (
    run_local_llm,
    chunk_and_query_local_llm,
    run_local_ticker_by_ticker,
    save_scores_from_objects,
)

# ─── Progression Capital / Milestones ───
try:
    from progress_tracker import (
        get_latest_progress,
        update_roadmap_from_progress,
        MILESTONES,
    )
    progress_data = get_latest_progress()
    update_roadmap_from_progress()

    if progress_data:
        _, capital, pnl, milestone = progress_data
        pct = min(capital / MILESTONES[-1], 1.0)
        st.progress(pct, text=f"Capital ${capital:.2f} | PnL {pnl:+.2f}")
        st.markdown("#### Milestones")
        for m in MILESTONES:
            icon = "✅" if capital >= m else "❌"
            st.write(f"{icon} ${m}")

except ImportError:
    try:
        from utils.progress_tracker import load_progress
        data = load_progress()
        last_capital = data[-1][1] if data else 3000
        progress = min(last_capital / 100000, 1.0)
        st.progress(progress, text=f"Capital actuel : {last_capital}$")
    except Exception:
        st.progress(0.0, text="Capital actuel : inconnue")

# ─── Définition chemin base SQLite ───
DB_PATH = os.path.join(ROOT_DIR, "data", "trades.db")

# ─── Menu latéral ───
st.sidebar.markdown("## 🚀 Navigation")
page = st.sidebar.radio("Menu principal", [
    "📊 Watchlist",
    "📋 Roadmap",
    "📋 Refactor Tasks",
    "🏢 Entreprise",
    "🧘 Personal",
    "📦 Clôture",
    "📄 Trades simulés"
], index=0)

# Activation IA locale
use_local_llm = st.sidebar.checkbox("Activer IA locale (Mistral-7B)", key="local_llm")

if "voice_thread" not in st.session_state:
    st.session_state.voice_thread = None
if "watchdog_thread" not in st.session_state:
    st.session_state.watchdog_thread = None

if st.sidebar.button("🎤 Activer notifications vocales") and st.session_state.voice_thread is None:
    thread = threading.Thread(target=loop_notifications, daemon=True)
    thread.start()
    st.session_state.voice_thread = thread
    st.success("Notifications vocales activées")

if st.sidebar.button("🛡️ Activer surveillance IA"):
    start_watchdog_thread()
    st.sidebar.success("Surveillance IA activée")

# ─── Pages secondaires ───
if page == "📋 Roadmap":
    roadmap_interface()
    roadmap_productivity_block()
    st.stop()

if page == "📋 Refactor Tasks":
    st.title("📋 Refactor Tracker")
    if "refactor_tasks" not in st.session_state:
        st.session_state["refactor_tasks"] = load_refactor_tasks()

    df = pd.DataFrame(st.session_state["refactor_tasks"])

    status_options = ["Todo", "In Progress", "Done", "Blocked"]

    priorities = sorted(df["priority"].unique()) if not df.empty else []
    selected_status = st.multiselect("Filtrer par statut", status_options, default=status_options)
    selected_priority = st.multiselect("Filtrer par priorité", priorities, default=priorities)

    filtered_df = df[df["status"].isin(selected_status) & df["priority"].isin(selected_priority)] if not df.empty else df

    def _save_tasks():
        st.session_state["refactor_tasks"] = st.session_state["task_editor"]
        save_refactor_tasks(st.session_state["refactor_tasks"])
        st.toast("Sauvegardé", icon="💾")

    st.data_editor(
        filtered_df,
        key="task_editor",
        num_rows="dynamic",
        on_change=_save_tasks,
        disabled=False,
        use_container_width=True,
    )
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

# ─── Page : Trades simulés ───
if page == "📄 Trades simulés":
    st.title("📄 Historique des trades simulés")
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM trades_simules ORDER BY datetime DESC", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur chargement trades : {e}")
    st.stop()

# ─── Watchlist ───
st.title("📊 WatchlistBot – Version V7")

# ─── Progression vers l'objectif 100k$ ────────────────────────────────────────
try:
    data = load_progress()
    last_capital = data[-1][1] if data else 3000
    progress = min(last_capital / 100000, 1.0)
    st.progress(progress, text=f"Capital actuel : {last_capital}$")
    daily_gain = st.number_input("Gain moyen par jour ($)", value=0.0, key="gain_journalier")
    if daily_gain > 0:
        from utils.progress_tracker import project_target_date
        target_date = project_target_date(last_capital, daily_gain)
        if target_date:
            days = (target_date - datetime.now().date()).days
            st.write(f"Objectif 100k estimé dans ~{days} jours (le {target_date})")
except Exception:
    st.progress(0.0, text="Capital actuel : inconnue")

watchlist_kpi_dashboard()

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
            COALESCE(w.has_fda, 0) AS has_fda,
            w.float AS float,
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
    df['global_score'] = df.apply(
        lambda r: compute_global_score(
            r.get('score'),
            r.get('score_gpt'),
            r.get('percent_gain'),
            r.get('volume'),
            r.get('float'),
            r.get('sentiment'),
        ),
        axis=1,
    )
    return df.to_dict(orient='records')

def fetch_live_watchlist():
    try:
        resp = requests.get(f"{API_URL}/watchlist/live", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        st.warning(f"Erreur chargement live: {e}")
    return load_watchlist()


def safe_fetch_live_watchlist():
    """Return watchlist and possible error message."""
    try:
        resp = requests.get(f"{API_URL}/watchlist/live", timeout=10)
        if resp.status_code == 200:
            return resp.json(), None
        return [], f"HTTP {resp.status_code}"
    except Exception as e:
        return [], str(e)

def load_watchlist_full():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT ticker, description FROM watchlist WHERE description IS NOT NULL"
    ).fetchall()
    conn.close()

    unique = {}
    for ticker, desc in rows:
        text = desc.strip().replace("\n", " ")
        if ticker not in unique and text:
            unique[ticker] = text
    return [{"symbol": t, "desc": d} for t, d in unique.items()]


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
            st.rerun()
        else:
            st.warning("Veuillez renseigner ticker et description.")

# 🤖 Analyse GPT
col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("### 🤖 Analyse batch ChatGPT")
    auto_batch = st.checkbox("Activer analyse batch automatique", key="auto_batch")

    def run_local_batch():
        try:
            entries = load_watchlist_full()
            if not entries:
                st.warning("Aucun ticker à scorer.")
                return

            progress_bar = st.progress(0.0, text=f"0/{len(entries)}")

            def cb(i, total):
                progress_bar.progress(i / total, text=f"{i}/{total}")

            results = run_local_ticker_by_ticker(entries, progress_callback=cb)
            save_scores_from_objects(results)

            returned = {r.get("symbol") for r in results}
            for item in entries:
                if item.get("symbol") not in returned:
                    st.warning(f"⚠️ Échec analyse {item.get('symbol')}")

            st.success("✅ Analyse locale terminée.")
            conn = sqlite3.connect(DB_PATH)
            df_scores = pd.read_sql_query("SELECT * FROM news_score", conn)
            conn.close()
            st.dataframe(df_scores)
        except Exception as e:
            st.error(f"Erreur IA locale: {e}")

    def run_and_show():
        if use_local_llm:
            run_local_batch()
            return
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

    if st.button("🔬 Récupérer approbations FDA récentes"):
        with st.spinner("Chargement des approbations…"):
            inserted = fetch_fda_data(limit=100, verbose=True, db_path=DB_PATH)
        st.success(f"✅ {inserted} approbations ajoutées")

    if st.button("🧪 Vérifier FDA"):
        with sqlite3.connect(DB_PATH) as conn:
            enrichir_watchlist_avec_fda(conn)
        st.success("Watchlist mise à jour avec les données FDA.")

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
    try:
        resp_csv = requests.get(f"{API_URL}/watchlist/export", timeout=10)
        if resp_csv.status_code == 200:
            st.download_button(
                "💾 Télécharger watchlist (.csv)",
                data=resp_csv.content,
                file_name="watchlist.csv",
            )
    except Exception as e:
        st.warning(f"Export CSV indisponible: {e}")

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

# 💼 Watchlist Live
if "watchlist_live" not in st.session_state:
    st.session_state["watchlist_live"] = fetch_live_watchlist()

if st.button("🔄 Refresh"):
    st.session_state["watchlist_live"] = fetch_live_watchlist()

watchlist = st.session_state.get("watchlist_live", [])
watchlist = sorted(
    watchlist,
    key=lambda w: w.get("change")
    or w.get("percent_gain")
    or w.get("change_percent")
    or 0,
    reverse=True,
)

if not watchlist:
    st.warning("Aucune donnée disponible pour le moment")
else:
    for idx, stock in enumerate(watchlist):
        afficher_bloc_ticker(stock, idx)

st.markdown("---")
st.markdown(f"© WatchlistBot V7 – {datetime.now().year}")
