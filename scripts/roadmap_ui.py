# roadmap_ui.py – Version 8.4 avec sauvegarde et barres de progression globales
import os
import sqlite3
import streamlit as st
from roadmap_generator_tools import create_epic_md, create_bpmn_placeholder
import task_manager
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT_DIR, 'data', 'project_tracker.db')
DOC_PATH = os.path.join(ROOT_DIR, 'project_doc')
IMAGES_PATH = os.path.join(DOC_PATH, 'images')


def get_epic_list():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔄 Ajouter automatiquement les EPICs basés sur les fichiers .md si table vide
    cursor.execute("SELECT COUNT(*) FROM epics")
    count = cursor.fetchone()[0]
    if count == 0:
        epic_files = [f for f in os.listdir(DOC_PATH) if f.endswith('.md') and f[0:2].isdigit()]
        for f in epic_files:
            epic_id = f.split('.')[0]
            label = f.replace('_', ' ').replace('.md', '')
            cursor.execute("INSERT INTO epics (id, label) VALUES (?, ?)", (epic_id, label))
        conn.commit()

    cursor.execute("SELECT id, label FROM epics ORDER BY id")
    epics = cursor.fetchall()
    conn.close()
    return epics
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, label FROM epics ORDER BY id")
    epics = cursor.fetchall()
    conn.close()
    return epics


def get_user_stories(epic_code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, story, status FROM user_stories WHERE epic LIKE ?", (f"%{epic_code}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows


def roadmap_productivity_block():
    st.subheader("📆 Daily Productivity – EPIC 27")
    type_selection = st.selectbox("🔍 Filtrer par catégorie", [
        "AUDIT","Toutes", "Technique", "Test", "Assistant", "Interface", "Automation", "Roadmap", "Suivi", "Intégration", "Database", "Documentation", "Intelligence"], key="selectbox_productivity")
    todos = task_manager.get_todo_today()
    if type_selection and type_selection != "Toutes":
        todos = [t for t in todos if len(t) > 1 and type_selection.lower() in t[1].lower()]
    st.subheader("📆 Daily Productivity – EPIC 27")
    todos = task_manager.get_todo_today()
    if type_selection and type_selection != "Toutes":
        todos = [t for t in todos if len(t) > 1 and type_selection.lower() in t[1].lower()]
    if todos:
        done = len([t for t in todos if len(t) > 3 and t[3] == 1])
        progress = done / len(todos)
        st.progress(progress, text=f"Progression des tâches : {int(progress*100)}%")

    epic_options = ["Toutes"] + [f"{e[0]} - {e[1]}" for e in get_epic_list()]
    selected_epic = st.selectbox("Associer à un EPIC (optionnel)", [""] + epic_options, key="epic_task_selector")

    us_id_input = st.text_input("ID de la User Story (optionnel)")
    us_id = us_id_input.strip() if us_id_input else None

    task_desc = st.text_input("Description de la tâche")
    due_date = st.date_input("Date limite")
    reminder = st.checkbox("Rappel Telegram activé", value=True)

    if st.button("✅ Ajouter la tâche"):
        task_manager.add_task(us_id, task_desc, str(due_date), reminder)
        st.success("Tâche enregistrée.")

    st.markdown("---")
    st.markdown("### 📋 Tâches du jour")
    type_selection = st.selectbox("🔍 Filtrer par catégorie", [
        "AUDIT","Toutes", "Technique", "Test", "Assistant", "Interface", "Automation", "Roadmap", "Suivi", "Intégration", "Database", "Documentation", "Intelligence"])
    if type_selection and type_selection != "Toutes":
        todos = [t for t in todos if len(t) > 1 and type_selection.lower() in t[1].lower()]

    for t in todos:
        st.markdown(f"- ✅ **#{t[0]}** : {t[1]} *(Échéance : {t[2] or 'Aucune'})*")
        if st.button(f"✔️ Terminer #{t[0]}", key=f"done_{t[0]}"):
            task_manager.mark_task_done(t[0])
            st.success(f"Tâche #{t[0]} validée.")

    if st.button("📬 Envoyer rappels Telegram"):
        task_manager.send_telegram_reminders()
        st.success("Rappels envoyés via le bot.")


def roadmap_interface():
    # 🔄 Barre de progression tâches journalières
    todos = task_manager.get_todo_today()
    if todos:
        done = len([t for t in todos if len(t) > 3 and t[3] == 1])
        progress = done / len(todos)
        st.progress(progress, text=f"Tâches journalières : {int(progress*100)}%")

    # 🔄 Barre de progression User Stories globale (tous EPICs)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_stories")
    total_us = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user_stories WHERE LOWER(status) = 'done'")
    done_us = cursor.fetchone()[0]
    conn.close()
    if total_us > 0:
        st.progress(done_us / total_us, text=f"Progression globale US : {int(100 * done_us / total_us)}%")
        st.title("📘 Roadmap Tracker - WatchlistBot V7")
    st.markdown("### EPIC actif")
    epic_files = [f for f in os.listdir(DOC_PATH) if f.endswith('.md') and f[0:2].isdigit()]
    epic_files.sort()

    selected_epic = st.selectbox("EPICs disponibles", epic_files, key="epic_selector")
    if selected_epic:
        prefix = selected_epic.split('.')[0]

        with open(os.path.join(DOC_PATH, selected_epic), "r", encoding="utf-8") as f:
            content = f.read()

        with st.expander("📄 Markdown de l'EPIC"):
            st.code(content)

        img_name = f"bpmn_epic_{prefix}.png"
        img_path = os.path.join(IMAGES_PATH, img_name)
        if os.path.exists(img_path):
            with st.expander("🧩 Diagramme BPMN"):
                st.image(img_path, caption=img_name, use_container_width=True)

        stories = get_user_stories(prefix)
        with st.expander("✅ User Stories de l'EPIC sélectionné"):
            if stories:
                total = len(stories)
                done = sum(1 for s in stories if s[2].lower() == "done")
                st.progress(done / total, text=f"Progression globale des US : {int(100 * done/total)}%")

                us_options = [f"#{s[0]} - {s[1][:60]}..." if len(s[1]) > 60 else f"#{s[0]} - {s[1]}" for s in stories]
                selected_us_display = st.selectbox("Sélectionner une User Story à gérer", us_options, key="us_selector")
                selected_sid = selected_us_display.split(" ")[0][1:]
                selected_story = next(s for s in stories if str(s[0]) == selected_sid)

                with st.form(f"form_{selected_sid}"):
                    st.markdown(f"### 🧾 User Story #{selected_sid}")
                    st.markdown(f"**Description :** {selected_story[1]}")
                    new_status = st.selectbox("Statut", ["To Do", "In Progress", "Done"], index=["To Do", "In Progress", "Done"].index(selected_story[2]) if selected_story[2] in ["To Do", "In Progress", "Done"] else 0)
                    priority = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute"], key=f"prio_{selected_sid}")
                    if st.form_submit_button("💾 Sauvegarder"):
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("UPDATE user_stories SET status = ?, priority = ? WHERE id = ?", (new_status, priority, str(selected_sid)))
                        conn.commit()
                        conn.close()
                        st.success("✅ User Story mise à jour")
            else:
                st.warning("Aucune user story trouvée pour cet EPIC.")

        with st.expander("🛠 Génération de fichiers EPIC"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Générer fichier .md"):
                    create_epic_md(prefix)
                    st.success(".md généré")
            with col2:
                if st.button("🧭 Générer image BPMN"):
                    create_bpmn_placeholder(prefix)
                    st.success("Image BPMN générée")

        with st.expander("📥 Importer des User Stories (Excel)"):
            us_file = st.file_uploader("Charger un fichier .xlsx", type=["xlsx"], key="upload_us_file")
            if us_file:
                try:
                    df = pd.read_excel(us_file)
                    required_cols = {"ID", "Epic", "User Story", "Acceptance Criteria", "Module", "Priority", "Status", "Testable"}
                    if not required_cols.issubset(set(df.columns)):
                        st.error("❌ Le fichier doit contenir : " + ", ".join(required_cols))
                    else:
                        df.rename(columns={
                            "ID": "id",
                            "Epic": "epic",
                            "User Story": "story",
                            "Acceptance Criteria": "criteria",
                            "Module": "module",
                            "Priority": "priority",
                            "Status": "status",
                            "Testable": "testable"
                        }, inplace=True)
                        df["epic"] = prefix
                        st.dataframe(df.head())
                        conn = sqlite3.connect(DB_PATH)
                        df.to_sql("user_stories", conn, if_exists="append", index=False)
                        conn.close()
                        st.success(f"✅ {len(df)} user stories importées dans l'EPIC {prefix}")
                except Exception as e:
                    st.error(f"Erreur : {e}")


def personal_interface():
    
    type_selection = st.selectbox("🔍 Filtrer les tâches personnelles par catégorie", ["Toutes", "Santé", "Énergie", "Mental", "Finance", "Famille", "Assistant"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, objectif, date_cible, statut FROM personal_goals"
    if type_selection != "Toutes":
        query += " WHERE categorie LIKE ?"
        cursor.execute(query, (f"%{type_selection}%",))
    else:
        cursor.execute(query)
    tasks = cursor.fetchall()
    conn.close()

    if tasks:
        st.markdown(f"### 📋 {len(tasks)} tâche(s) affichée(s) pour {type_selection if type_selection != 'Toutes' else 'toutes les catégories'}")
        for t in tasks:
            st.markdown(f"- 🔹 **#{t[0]}** : {t[1]} *(Échéance : {t[2] or 'Aucune'})*")
            if st.button(f"✔️ Marquer comme faite #{t[0]}", key=f"done_personal_{t[0]}"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE personal_goals SET statut = 'Done' WHERE id = ?", (t[0],))
                conn.commit()
                conn.close()
                st.success(f"Tâche #{t[0]} validée.")
    st.title("🧘 Personal Assistant Hub")
    tabs = st.tabs(["Santé", "Énergie", "Mental", "Finance", "Famille", "🧠 Assistant IA (soon)"])

    with tabs[0]:
        st.markdown("📊 Suivi Hydratation, Sommeil, Sport")
    with tabs[1]:
        st.markdown("💡 Niveau d'énergie, stress, motivation")
    with tabs[2]:
        st.markdown("🧠 État émotionnel / affirmations")
    with tabs[3]:
        st.markdown("💸 Objectifs budgétaires, alertes dépenses")
    with tabs[4]:
        st.markdown("🏡 Priorités familiales & sociales")
    with tabs[5]:
        st.markdown("🤖 Assistant IA personnel en cours d'intégration...")


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        ).fetchone()
        is not None
    )


def compute_watchlist_kpis(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        data = {}
        data["total_tickers"] = conn.execute(
            "SELECT COUNT(*) FROM watchlist"
        ).fetchone()[0]
        data["tickers_fda"] = conn.execute(
            "SELECT COUNT(*) FROM watchlist WHERE has_fda = 1"
        ).fetchone()[0]
        data["tickers_newspr"] = conn.execute(
            "SELECT COUNT(*) FROM watchlist WHERE source LIKE '%NewsPR%'"
        ).fetchone()[0]
        data["tickers_newsauto"] = conn.execute(
            "SELECT COUNT(*) FROM watchlist WHERE source LIKE '%NewsAuto%'"
        ).fetchone()[0]
        if _table_exists(conn, "news_by_ticker"):
            data["total_news"] = conn.execute(
                "SELECT COUNT(*) FROM news_by_ticker"
            ).fetchone()[0]
        else:
            data["total_news"] = 0
    finally:
        conn.close()
    return data


def watchlist_dashboard(db_path: str) -> None:
    st.markdown("### 📈 KPIs Watchlist")
    if "watch_kpis" not in st.session_state:
        st.session_state["watch_kpis"] = compute_watchlist_kpis(db_path)
    if st.button("🔁 Recalculer les KPI"):
        st.session_state["watch_kpis"] = compute_watchlist_kpis(db_path)
    kpis = st.session_state["watch_kpis"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tickers totaux", kpis.get("total_tickers", 0))
    c2.metric("Tickers FDA", kpis.get("tickers_fda", 0))
    c3.metric("NewsPR", kpis.get("tickers_newspr", 0))
    c4.metric("NewsAuto", kpis.get("tickers_newsauto", 0))
    c5.metric("News", kpis.get("total_news", 0))
