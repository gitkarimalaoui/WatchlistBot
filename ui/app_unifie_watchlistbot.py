import os
import sys
import subprocess
import sqlite3
import math
import json
from datetime import datetime
import threading
import time
from pathlib import Path

import asyncio

if sys.platform.startswith("win"):
    try:  # pragma: no cover - depends on platform
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import pandas as pd
import streamlit as st
import requests

try:  # Optional dependency for auto refresh
    from streamlit_autorefresh import st_autorefresh
except Exception:  # pragma: no cover - fallback if package missing
    st_autorefresh = None  # type: ignore

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
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
UTILS = os.path.join(ROOT_DIR, "utils")
SIMULATION = os.path.join(ROOT_DIR, "simulation")

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ─── Ajout des chemins au système ───
for path in (ROOT_DIR, SCRIPTS, ROOT_UI, UTILS, SIMULATION):
    if path not in sys.path:
        sys.path.insert(0, path)

from db.watchlist_utils import pick_date_column, ensure_schema_watchlist_scores

# ─── Configuration base de données ───
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "trades.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH.as_posix(), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

from db.refactor_tasks import fetch_tasks as load_refactor_tasks
from db.refactor_tasks import upsert_tasks as save_refactor_tasks

from security.auth_manager import authenticate_user

if "user_role" not in st.session_state:
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        success, role = authenticate_user(username, password)
        if success:
            st.session_state["user_role"] = role
            st.success(f"Authentification réussie ({role})")
            st.rerun()
        else:
            st.error("Échec de l'authentification")
    st.stop()
else:
    st.info(f"Connecté en tant que : {st.session_state['user_role']}")
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    st.session_state["dark_mode"] = st.sidebar.checkbox(
        "\U0001f319 Mode nuit", value=st.session_state["dark_mode"]
    )
    if st.session_state["dark_mode"]:
        st.markdown(
            """
            <style>
            .stApp { background-color: #0e1117; color: #f0f0f0; }
            </style>
            """,
            unsafe_allow_html=True,
        )

# ─── Imports locaux ───
from notifications.proactive_voice import ProactiveVoiceNotifier
from monitoring.watchdog_conditions import start_watchdog_thread
from automation.codex_watcher import start_watchers
from fusion.module_import_checklist_txt import extraire_tickers_depuis_txt
from intelligence.learning_loop import run_learning_loop

# ─── Notifications vocales ───
notifier = ProactiveVoiceNotifier()


def loop_notifications() -> None:
    while True:
        notifier.run_pending()
        time.sleep(5)


# ─── Gestion des tâches de refactor ───
# ``load_refactor_tasks`` and ``save_refactor_tasks`` are imported from
# ``db.refactor_tasks`` and now operate on ``project_tracker.db``.


def import_watchlist_txt_page() -> None:
    """UI to import a Jaguar watchlist from a text file."""
    st.title("📥 Importer Watchlist .txt")
    uploaded = st.file_uploader("Fichier .txt", type="txt")
    if uploaded:
        content = uploaded.read().decode("utf-8")
        tmp_path = Path("uploaded_watchlist.txt")
        tmp_path.write_text(content)
        tickers = extraire_tickers_depuis_txt(tmp_path)
        tmp_path.unlink(missing_ok=True)
        st.success(f"{len(tickers)} tickers détectés")
        st.write(tickers)
        if tickers and st.button("Ajouter à la base"):
            conn = get_conn()
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS watchlist (
                    ticker TEXT PRIMARY KEY,
                    source TEXT,
                    date TEXT,
                    description TEXT,
                    updated_at TEXT
                )
                """
            )
            for t in tickers:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO watchlist
                    (ticker, source, date, description, updated_at)
                    VALUES (?, 'Jaguar', DATE('now'), '', CURRENT_TIMESTAMP)
                    """,
                    (t,),
                )
            conn.commit()
            conn.close()
            st.success("Watchlist mise à jour")


# ─── Imports locaux ───
from roadmap_ui import (
    roadmap_interface,
    roadmap_productivity_block,
    personal_interface,
    watchlist_kpi_dashboard,
)
from query_entreprise_db import (
    get_portfolio_modules,
    get_use_cases,
    get_revenue_sources,
    get_kpi_targets,
)
from page_modules.cloture_journee import cloturer_journee
from page_modules.crypto_section import show_crypto_section
from utils_affichage_ticker import (
    afficher_ticker_panel,
    _ia_score,
    afficher_bloc_ticker,
    calculer_indicateurs,
)
from utils.execution_reelle import executer_ordre_reel
from execution.strategie_scalping import executer_strategie_scalping
from intelligence.ai_scorer import compute_global_score
from utils.progress_tracker import load_progress
from formation_ai import formation_ai_page
from ui.menu_strategie_personnelle import afficher_strategie_personnelle
from utils.fda_fetcher import fetch_fda_data, enrichir_watchlist_avec_fda
from utils.utils_news import fetch_news_finnhub
from utils.utils_graph import charger_intraday_intelligent
from intelligence.local_llm import (
    run_local_llm,
    chunk_and_query_local_llm,
    run_local_ticker_by_ticker,
    save_scores_from_objects,
)
from utils.performance_metrics import compute_performance_metrics
from intelligence.smart_finrl_agent import executer_trading_reel_auto
from train_finrl_model import launch_finrl_training, SAVED_MODEL_PATH

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

# ─── Fonctions de lecture ───
@st.cache_resource
def _shared_conn() -> sqlite3.Connection:
    conn = get_conn()
    ensure_schema_watchlist_scores(conn)
    return conn


@st.cache_data(ttl=15)
def read_top_watchlist(limit: int, freshness_key: int) -> pd.DataFrame:
    conn = _shared_conn()
    date_col = pick_date_column(conn)
    if date_col is None:
        return pd.DataFrame(columns=["symbol", "score", "dt"])

    sql = f"""
      WITH last AS (SELECT MAX({date_col}) AS d FROM watchlist WHERE score IS NOT NULL)
      SELECT symbol, score, {date_col} AS dt
      FROM watchlist, last
      WHERE {date_col} = last.d AND score IS NOT NULL
      ORDER BY score DESC
      LIMIT ?
    """
    return pd.read_sql_query(sql, conn, params=(limit,))

# ─── Menu latéral ───
st.sidebar.markdown("## 🚀 Navigation")
page = st.sidebar.radio(
    "Menu principal",
    [
        "📊 Watchlist",
        "📋 Roadmap",
        "📋 Refactor Tasks",
        "🏢 Entreprise",
        "🧘 Personal",
        "📥 Import .txt",
        "📦 Clôture",
        "🤖 Learning Engine",
        "💱 Cryptos",
        "📄 Trades simulés",
        "🎓 Formation IA",
        "📌 Plan Stratège Visionnaire",
        "🧠 Éditeur Prompt IA (Lyra)",
    ],
    index=0,
)

# Activation IA locale
use_local_llm = st.sidebar.checkbox("Activer IA locale (Mistral-7B)", key="local_llm")

# Enable or disable automatic page refresh
auto_refresh = st.sidebar.checkbox("\U0001f503 Auto refresh", value=True)
if auto_refresh and st_autorefresh:
    st_autorefresh(interval=30 * 1000, key="watchlist_global_refresh")

if "workflow_thread" not in st.session_state:
    st.session_state.workflow_thread = None
auto_mode = st.sidebar.checkbox("\U0001f3af Activer stratégie IA autonome")
if auto_mode and st.session_state.workflow_thread is None:

    def _run_workflow() -> None:
        from config.config_manager import ConfigManager
        from core.workflow_automated_mode import lancer_workflow_ia

        _, creds_missing = lancer_workflow_ia(ConfigManager())
        if creds_missing:
            st.warning("Telegram credentials missing; alerts not sent")

    t = threading.Thread(target=_run_workflow, daemon=True)
    t.start()
    st.session_state.workflow_thread = t
if st.sidebar.button("⏹ Stopper IA") and st.session_state.workflow_thread:
    st.session_state.workflow_thread = None

if "voice_thread" not in st.session_state:
    st.session_state.voice_thread = None
if "watchdog_thread" not in st.session_state:
    st.session_state.watchdog_thread = None
if "watchlist_updater" not in st.session_state:
    st.session_state.watchlist_updater = None
if "api_process" not in st.session_state:
    st.session_state.api_process = None


def ensure_api_server() -> None:
    """Start local FastAPI server if not already running."""
    if st.session_state.api_process is not None:
        return

    try:
        requests.get(f"{API_URL}/watchlist/live", timeout=2)
        st.session_state.api_process = True
        return
    except Exception:
        pass

    api_script = os.path.join(ROOT_DIR, "api", "watchlist_api.py")
    try:
        proc = subprocess.Popen(
            [sys.executable, api_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        st.session_state.api_process = proc
        time.sleep(1)
    except Exception as exc:
        st.warning(f"Impossible de démarrer l'API: {exc}")
        st.session_state.api_process = None


ensure_api_server()


def start_watchlist_updater(interval: int = 30) -> None:
    """Background thread fetching latest watchlist periodically."""

    if st.session_state.watchlist_updater is not None:
        return

    def _loop() -> None:
        while True:
            try:
                st.session_state["watchlist_live"] = fetch_live_watchlist()
            except Exception as exc:  # pragma: no cover - best effort logging
                print(f"[watchlist_updater] {exc}")
            time.sleep(interval)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    st.session_state.watchlist_updater = thread


if (
    st.sidebar.button("🎤 Activer notifications vocales")
    and st.session_state.voice_thread is None
):
    thread = threading.Thread(target=loop_notifications, daemon=True)
    thread.start()
    st.session_state.voice_thread = thread
    st.success("Notifications vocales activées")

if st.sidebar.button("🛡️ Activer surveillance IA"):
    start_watchdog_thread()
    st.sidebar.success("Surveillance IA activée")

if st.sidebar.button("📡 Lancer Codex Watcher") and not st.session_state.get(
    "codex_observer"
):
    st.session_state["codex_observer"] = start_watchers()
    st.sidebar.success("Codex Watcher lancé")

if st.sidebar.button("Afficher paramètres IA"):
    st.session_state["show_ai_params"] = not st.session_state.get(
        "show_ai_params", False
    )

if st.session_state.get("show_ai_params"):
    from intelligence.meta_ia import load_meta

    meta = load_meta()
    st.sidebar.json(meta.get("weights", {}))
    disabled = meta.get("disabled_signals", {})
    if disabled:
        st.sidebar.write("Signaux désactivés :")
        st.sidebar.json(disabled)

activer_agent = st.sidebar.checkbox("🤖 Activer SmartFinRL")
if SAVED_MODEL_PATH.exists():
    st.sidebar.info("⚙️ Modèle FinRL PPO chargé avec succès")

if st.sidebar.checkbox(
    "🔁 Lancer IA FinRL (PPO)", key="launch_finrl"
) and not st.session_state.get("finrl_training_done"):
    with st.spinner("Entraînement FinRL en cours..."):
        result = launch_finrl_training()
    st.session_state["finrl_training_done"] = True
    st.session_state["finrl_model_path"] = result["model_path"]
    st.sidebar.success("Modèle PPO entraîné")
    st.sidebar.metric("Sharpe", f"{result['sharpe_ratio']:.2f}")
    st.sidebar.metric("Return", f"{result['cumulative_return']*100:.2f}%")

if activer_agent:
    st.sidebar.success(
        "L’agent SmartFinRL est activé. Il apprendra et exécutera les trades."
    )
    if st.sidebar.button("▶️ Exécuter stratégie en live"):
        path = st.session_state.get("finrl_model_path", str(SAVED_MODEL_PATH))
        executer_trading_reel_auto(path)


# ─── Pages secondaires ───
if page == "📋 Roadmap":
    roadmap_interface()
    roadmap_productivity_block()
    st.stop()

if page == "📋 Refactor Tasks":
    st.title("📋 Refactor Tracker")
    if "refactor_tasks" not in st.session_state:
        st.session_state["refactor_tasks"] = load_refactor_tasks()

    tasks_data = st.session_state["refactor_tasks"]
    # ``tasks_data`` may be a list of dicts or a mapping depending on
    # how the JSON was saved. ``from_records`` handles both cases
    # gracefully and avoids the ambiguous ordering error raised by
    # ``pd.DataFrame()`` when given a plain ``dict``.
    df = (
        tasks_data
        if isinstance(tasks_data, pd.DataFrame)
        else pd.DataFrame.from_records(tasks_data)
    )

    status_options = ["Todo", "In Progress", "Done", "Blocked"]

    priorities = sorted(df["priority"].unique()) if not df.empty else []
    selected_status = st.multiselect(
        "Filtrer par statut", status_options, default=status_options
    )
    selected_priority = st.multiselect(
        "Filtrer par priorité", priorities, default=priorities
    )

    filtered_df = (
        df[df["status"].isin(selected_status) & df["priority"].isin(selected_priority)]
        if not df.empty
        else df
    )

    with st.expander("➕ Nouvelle tâche"):
        col1, col2 = st.columns(2)
        new_id = col1.text_input("ID")
        new_priority = col2.selectbox(
            "Priorité", ["Low", "Medium", "High"], key="new_priority"
        )
        new_desc = st.text_input("Description")
        new_module = st.text_input("Module")
        new_status = st.selectbox("Statut", status_options, key="new_status")
        if st.button("Ajouter") and new_id:
            new_row = {
                "id": new_id,
                "description": new_desc,
                "module": new_module,
                "priority": new_priority,
                "status": new_status,
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state["refactor_tasks"] = df.to_dict(orient="records")
            save_refactor_tasks(st.session_state["refactor_tasks"])
            st.success("Tâche ajoutée")

    def _save_tasks() -> None:
        edited = st.session_state["task_editor"]
        if isinstance(edited, pd.DataFrame):
            tasks_list = edited.to_dict(orient="records")
        else:
            tasks_list = edited
        st.session_state["refactor_tasks"] = tasks_list
        save_refactor_tasks(tasks_list)
        st.toast("Sauvegardé", icon="💾")

    st.data_editor(
        filtered_df,
        key="task_editor",
        num_rows="dynamic",
        on_change=_save_tasks,
        disabled=False,
        use_container_width=True,
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Statut",
                options=status_options,
            )
        },
    )
    delete_id = st.selectbox(
        "Supprimer la tâche", df["id"] if not df.empty else [], key="delete_select"
    )
    if st.button("Supprimer") and delete_id:
        df = df[df["id"] != delete_id]
        st.session_state["refactor_tasks"] = df.to_dict(orient="records")
        save_refactor_tasks(st.session_state["refactor_tasks"])
        st.success("Tâche supprimée")
    st.stop()

if page == "🏢 Entreprise":
    st.title("🏢 Entreprise IA & Solutions d’Architecture")
    st.dataframe(get_portfolio_modules(), use_container_width=True)
    st.stop()

if page == "🧘 Personal":
    personal_interface()
    st.stop()

if page == "📥 Import .txt":
    import_watchlist_txt_page()
    st.stop()

if page == "📦 Clôture":
    cloturer_journee()
    st.stop()

if page == "🤖 Learning Engine":
    st.title("🤖 Learning Engine")
    cycles = st.number_input("Cycles", 1, 10, 1)
    launch_finrl = st.checkbox("Activer stratégie IA FinRL sur penny stocks")
    if st.button("Lancer l'apprentissage"):
        run_learning_loop(cycles=cycles)
        st.success("Boucle terminée")
    if launch_finrl:
        from intelligence.smart_finrl_agent import run_pipeline, dummy_live_signals

        with st.spinner("Entra\xeenement FinRL en cours..."):
            result = run_pipeline()
        st.metric("Sharpe", f"{result['sharpe_ratio']:.2f}")
        st.metric("Cumulative Return", f"{result['cumulative_return']*100:.2f}%")
        if result.get("equity_curve"):
            st.line_chart(result["equity_curve"])
        st.success("Strat\xe9gie pr\xeate \xe0 \xeatre utilis\xe9e")
        if st.button("Utiliser mod\xe8le FinRL pour simulation en live"):
            signals = dummy_live_signals()
            st.write(signals)
    st.stop()

if page == "💱 Cryptos":
    show_crypto_section()
    st.stop()

# ─── Page : Trades simulés ───
if page == "📄 Trades simulés":
    st.title("📄 Historique des trades simulés")
    try:
        conn = get_conn()
        df = pd.read_sql_query("SELECT * FROM trades_simules ORDER BY date DESC", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur chargement trades : {e}")
    st.stop()

if page == "🎓 Formation IA":
    formation_ai_page()
    st.stop()

if page == "📌 Plan Stratège Visionnaire":
    afficher_strategie_personnelle()
    st.stop()

if page == "🧠 Éditeur Prompt IA (Lyra)":
    from ui.editeur_prompt_lyra import main as afficher_editeur_lyra

    afficher_editeur_lyra()
    st.stop()

# ─── Watchlist ───
st.title("📊 WatchlistBot – Version V7")

st.subheader("Top scores")

if "freshness_key" not in st.session_state:
    st.session_state.freshness_key = int(time.time())

if st.button("🔄 Refresh"):
    read_top_watchlist.clear()
    st.session_state.freshness_key = int(time.time())

topN = read_top_watchlist(20, st.session_state.freshness_key)
st.caption(f"Dernier lot: {topN['dt'].max() if not topN.empty else '—'}")
st.dataframe(topN[["symbol", "score"]])

# ─── Progression vers l'objectif 100k$ ────────────────────────────────────────
try:
    data = load_progress()
    last_capital = data[-1][1] if data else 3000
    progress = min(last_capital / 100000, 1.0)
    st.progress(progress, text=f"Capital actuel : {last_capital}$")
    daily_gain = st.number_input(
        "Gain moyen par jour ($)", value=0.0, key="gain_journalier"
    )
    if daily_gain > 0:
        from utils.progress_tracker import project_target_date

        target_date = project_target_date(last_capital, daily_gain)
        if target_date:
            days = (target_date - datetime.now().date()).days
            st.write(f"Objectif 100k estimé dans ~{days} jours (le {target_date})")
except Exception:
    st.progress(0.0, text="Capital actuel : inconnue")

watchlist_kpi_dashboard()

with st.sidebar.expander("📈 Performance réelle"):
    metrics = compute_performance_metrics(DB_PATH.as_posix())
    if metrics:
        col_a, col_b = st.columns(2)
        col_a.metric("Win Rate", f"{metrics['win_rate']*100:.1f}%")
        col_b.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
        col_a.metric("Sharpe", f"{metrics['sharpe_ratio']:.2f}")
        col_b.metric("Drawdown", f"{metrics['drawdown']:.2f}$")
    else:
        st.write("Aucune donnée")


def count_watchlist_tickers():
    conn = get_conn()
    cnt = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    conn.close()
    return cnt


@st.cache_data
def load_watchlist():
    conn = get_conn()
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
    df["global_score"] = df.apply(
        lambda r: compute_global_score(
            r.get("score"),
            r.get("score_gpt"),
            r.get("percent_gain"),
            r.get("volume"),
            r.get("float"),
            r.get("sentiment"),
        ),
        axis=1,
    )
    return df.to_dict(orient="records")


def fetch_live_watchlist():
    try:
        resp = requests.get(f"{API_URL}/watchlist/live", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        if not st.session_state.get("api_error_displayed"):
            st.warning(f"API indisponible ({e}). Utilisation des donn\xe9es locales.")
            st.session_state["api_error_displayed"] = True
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
    conn = get_conn()
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


def update_green_indicators(watchlist):
    """Update indicators for tickers with positive change."""
    updated = []
    for itm in watchlist:
        change = (
            itm.get("change")
            or itm.get("percent_gain")
            or itm.get("change_percent")
            or 0
        )
        if change > 0:
            ticker = itm.get("ticker") or itm.get("symbol")
            if not ticker:
                continue
            df = charger_intraday_intelligent(ticker)
            ind = calculer_indicateurs(df)
            if ind:
                itm.update(ind)
                updated.append(ticker)
    return updated


def render_top_tickers_panel(watchlist, autorefresh: bool = False) -> None:
    """Display a vertical panel with top 20 tickers by daily change."""
    if autorefresh and st_autorefresh:
        st_autorefresh(interval=30 * 1000, key="top_tickers_refresh")
    top = sorted(
        watchlist,
        key=lambda w: w.get("change")
        or w.get("percent_gain")
        or w.get("change_percent")
        or 0,
        reverse=True,
    )[:20]
    st.markdown("#### 🔥 Top 20 Tickers")
    for itm in top:
        tic = itm.get("ticker") or itm.get("symbol")
        if not tic:
            continue
        change = (
            itm.get("change")
            or itm.get("percent_gain")
            or itm.get("change_percent")
            or 0
        )
        if change > 5:
            color = "green"
        elif change >= 0:
            color = "orange"
        else:
            color = "red"
        st.markdown(
            f"<a href='?ticker={tic}' style='color:{color}; text-decoration:none; display:block; margin:2px 0;'>{tic} {change:+.2f}%</a>",
            unsafe_allow_html=True,
        )


# ➕ Ajout manuel
st.markdown("### ➕ Ajouter un ticker manuellement")
with st.expander("Saisie manuelle"):
    new_tic = st.text_input("Ticker", key="manual_ticker")
    new_desc = st.text_area("Description", key="manual_desc")
    if st.button("Ajouter", key="manual_add"):
        if new_tic and new_desc:
            conn = get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO watchlist (ticker, source, date, description, updated_at) VALUES (?, 'Manual', ?, ?, CURRENT_TIMESTAMP)",
                (new_tic.upper(), datetime.now().isoformat(), new_desc),
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
            conn = get_conn()
            df_scores = pd.read_sql_query("SELECT * FROM news_score", conn)
            conn.close()
            st.dataframe(df_scores)
        except Exception as e:
            st.error(f"Erreur IA locale: {e}")

    def run_and_show():
        if use_local_llm:
            run_local_batch()
            return
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "run_chatgpt_batch.py")],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            st.error(f"Batch failed:\n{proc.stderr}")
            return
        st.success("✅ Analyse GPT terminée.")
        conn = get_conn()
        df_scores = pd.read_sql_query("SELECT * FROM news_score", conn)
        conn.close()
        st.dataframe(df_scores)

    if st.button("🚀 Lancer analyse GPT", key="btn_batch") or auto_batch:
        run_and_show()

    if st.button("🔬 Récupérer approbations FDA récentes"):
        with st.spinner("Chargement des approbations…"):
            inserted = fetch_fda_data(limit=100, verbose=True, db_path=DB_PATH.as_posix())
        st.success(f"✅ {inserted} approbations ajoutées")

    if st.button("🧪 Vérifier FDA"):
        with get_conn() as conn:
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
    st.markdown(
        "Génère les données depuis l’API Yahoo Finance pour tous les tickers de la base (7d/1min + 2y/daily)."
    )
    if st.button("🟢 Lancer collecte et enregistrement DB"):
        proc = subprocess.run(
            [
                sys.executable,
                os.path.join(SCRIPTS, "collect_historical_batch_to_db.py"),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            st.success("✅ Collecte et insertion en base terminées avec succès.")
            st.code(proc.stdout)
        else:
            st.error("❌ Échec pendant la collecte.")
            st.code(proc.stderr)

# 💼 Watchlist Live
start_watchlist_updater()
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

page_size = st.sidebar.number_input("Tickers par page", 5, 50, 10, step=5)
show_positive = st.sidebar.checkbox("Change positif uniquement", value=True)
min_score = st.sidebar.slider("Score global minimum", 0, 100, 50)
auto_score = st.sidebar.slider("Score auto-ouverture", 0, 100, 85, step=5)
st.session_state["auto_expand_score"] = auto_score

if show_positive:
    watchlist = [
        w
        for w in watchlist
        if (w.get("change") or w.get("percent_gain") or w.get("change_percent") or 0)
        > 0
    ]

watchlist = [w for w in watchlist if w.get("global_score", 0) >= min_score]

page_count = max(1, math.ceil(len(watchlist) / page_size))
page = st.sidebar.number_input("Page", 1, page_count, 1, step=1)
start = (page - 1) * page_size
end = start + page_size
page_watchlist = watchlist[start:end]

if st.sidebar.button("🔧 MAJ indicateurs verts"):
    updated = update_green_indicators(watchlist)
    st.sidebar.success(f"{len(updated)} tickers mis \xe0 jour")

main_col, right_col = st.columns([8, 1])

with right_col:
    render_top_tickers_panel(watchlist)

with main_col:
    if not page_watchlist:
        st.warning("Aucune donnée disponible pour le moment")
    else:
        for idx, stock in enumerate(page_watchlist, start=start):
            afficher_bloc_ticker(stock, idx)

st.markdown("---")
st.markdown(f"© WatchlistBot V7 – {datetime.now().year}")
