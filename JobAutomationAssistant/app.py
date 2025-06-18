import streamlit as st
import pandas as pd
import sqlite3
import time
import random
from datetime import datetime
import plotly.express as px

DB_PATH = "jobtracker.db"

def save_offer_to_db(offer):
    """Persist a scraped job offer in the database.

    Args:
        offer (dict): Normalized job offer structure.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO offers (title, company, location, description, requirements, salary, platform, url, date_posted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        offer['title'], offer['company'], offer['location'], offer['description'],
        ', '.join(offer['requirements']), offer['salary'], offer['platform'],
        offer['url'], offer['date_posted']
    ))
    conn.commit()
    conn.close()

def save_application_to_db(application):
    """Save an application entry to the database.

    Args:
        application (dict): Application details with nested job info.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO applications (job_title, company, cover_letter, date_sent)
        VALUES (?, ?, ?, ?)
    """, (
        application['job']['title'], application['job']['company'],
        application['cover_letter'], application['date_sent']
    ))
    conn.commit()
    conn.close()

def save_meeting_to_db(meeting):
    """Store an upcoming meeting in the database.

    Args:
        meeting (dict): Meeting information to persist.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO meetings (date, company, contact, type, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        meeting['date'], meeting['company'], meeting['contact'],
        meeting['type'], meeting['status']
    ))
    conn.commit()
    conn.close()

def load_data_from_db():
    """Load offers, applications and meetings into session state.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT title, company, location, description, requirements, salary, platform, url, date_posted FROM offers")
    st.session_state.job_offers = [
        {
            'title': row[0], 'company': row[1], 'location': row[2], 'description': row[3],
            'requirements': row[4].split(', '), 'salary': row[5], 'platform': row[6],
            'url': row[7], 'date_posted': row[8]
        }
        for row in cur.fetchall()
    ]

    cur.execute("SELECT job_title, company, cover_letter, date_sent FROM applications")
    st.session_state.applications_sent = [
        {
            'job': {'title': row[0], 'company': row[1]},
            'cover_letter': row[2],
            'date_sent': row[3]
        }
        for row in cur.fetchall()
    ]

    cur.execute("SELECT date, company, contact, type, status FROM meetings")
    st.session_state.meetings_scheduled = [
        {
            'date': row[0], 'company': row[1], 'contact': row[2],
            'type': row[3], 'status': row[4]
        }
        for row in cur.fetchall()
    ]
    conn.close()

# Streamlit UI
st.set_page_config(page_title="Assistant Emploi", layout="wide")
st.title("🚀 Assistant Automatisé de Recherche d'Emploi")

if 'initialized' not in st.session_state:
    load_data_from_db()
    st.session_state.initialized = True

st.markdown("Bienvenue dans votre assistant IA pour la recherche d’emploi !")

st.markdown("### Dernières Offres")
for offer in st.session_state.job_offers[-5:]:
    st.write(f"📌 **{offer['title']}** chez *{offer['company']}* — {offer['location']}")

st.markdown("### 📊 Candidatures envoyées")
st.write(f"Total : {len(st.session_state.applications_sent)}")

st.markdown("### 📅 RDV Planifiés")
st.write(f"Total : {len(st.session_state.meetings_scheduled)}")
