import sqlite3
from datetime import datetime
from pathlib import Path
import streamlit as st
from core.db import DB_PATH

BADGE_DIR = Path(__file__).parent / "badges"

MODULES = [
    {
        "id": "m1",
        "title": "Fondamentaux IA (CS50 AI)",
        "link": "https://www.edx.org/", 
        "summary": "Cours d'introduction sur edX.",
    },
    {
        "id": "m2",
        "title": "IA pour le Trading (Coursera)",
        "link": "https://www.coursera.org/",
        "summary": "Cours Coursera consacré au trading.",
    },
    {
        "id": "m3",
        "title": "IA Penny Stocks (Interne WatchlistBot)",
        "link": "",
        "summary": "Modules internes IA scoring et backtest.",
    },
    {
        "id": "m35",
        "title": "FinRL Advanced DRL Strategy",
        "link": "https://github.com/AI4Finance-Foundation/FinRL",
        "summary": "Prise en main FinRL avec nos watchlists et trades_simules.",
    },
    {
        "id": "m36",
        "title": "FinRL Automation Module (Post-certification)",
        "link": "",
        "summary": "Ce module permet d’activer un agent IA autonome entraîné sur vos penny stocks préférés.",
    },
    {
        "id": "m4",
        "title": "IA News & Pattern",
        "link": "",
        "summary": "Utilisation du sentiment et des patterns graphiques.",
    },
    {
        "id": "m5",
        "title": "IA Production & Logs",
        "link": "",
        "summary": "Process de sauvegarde modèle et logs.",
    },
    {
        "id": "m6",
        "title": "Vision Language Models (VLM Bootcamp)",
        "link": "https://courses.opencv.org/courses/course-v1:Vision-Language-Models+Bootcamp+VLMs/courseware/6010d8df776c4f96ae1b09bc859b0b21/12356a27ac3b4725bdd431ec05f3b08b/",
        "summary": "Introduction aux VLM (BLIP, CLIP, GPT-4V), captioning de graphiques boursiers et Q&A visuelle. Fusion avec FinBERT et scoring IA.",
    },
]


def _get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(str(db_path))


def _init_table() -> None:
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progression_ia (
            module TEXT PRIMARY KEY,
            completed INTEGER DEFAULT 0,
            badge TEXT,
            completion_date TEXT
        )
        """
    )
    for m in MODULES:
        conn.execute(
            "INSERT OR IGNORE INTO progression_ia (module) VALUES (?)",
            (m["id"],),
        )
    conn.commit()
    conn.close()


def _load_progress():
    conn = _get_conn()
    rows = conn.execute(
        "SELECT module, completed FROM progression_ia"
    ).fetchall()
    conn.close()
    return {r[0]: bool(r[1]) for r in rows}


def _update_module(module: str, completed: bool) -> None:
    conn = _get_conn()
    conn.execute(
        "UPDATE progression_ia SET completed=?, completion_date=? WHERE module=?",
        (1 if completed else 0, datetime.utcnow().isoformat() if completed else None, module),
    )
    conn.commit()
    conn.close()


def formation_ai_page() -> None:
    _init_table()
    st.title("🎓 Formation IA")
    progress = _load_progress()
    total = len(MODULES)
    done = sum(1 for m in progress.values() if m)
    st.progress(done / total, text=f"{done}/{total} modules complétés")
    tabs = st.tabs([m["title"] for m in MODULES] + ["QCM Final"])
    for tab, module in zip(tabs, MODULES):
        with tab:
            st.subheader(module["title"])
            if module["link"]:
                st.markdown(f"[Lien vers le cours]({module['link']})")
            st.write(module["summary"])
            if BADGE_DIR.joinpath(f"module{MODULES.index(module)+1}.png").exists():
                st.image(str(BADGE_DIR / f"module{MODULES.index(module)+1}.png"), width=64)
            done_state = st.checkbox("Terminé", value=progress.get(module["id"], False), key=module["id"])
            if st.button("Enregistrer", key=f"save_{module['id']}"):
                _update_module(module["id"], done_state)
                st.success("Sauvegardé")
    with tabs[-1]:
        from ui.quiz_ia import run_quiz
        from ui.certificat_ia import generate_certificate

        score = run_quiz()
        if score is not None:
            name = st.text_input("Nom pour le certificat", key="cert_name")
            if name:
                pdf_bytes = generate_certificate(name, score)
                st.download_button(
                    "Télécharger certificat",
                    data=pdf_bytes,
                    file_name="certificat.pdf",
                    mime="application/pdf",
                )

    st.markdown("## 🧠 FinRL Automation Module (Post-certification)")
    st.write(
        "Ce module permet d’activer un agent IA autonome entraîné sur vos penny stocks préférés."
    )
