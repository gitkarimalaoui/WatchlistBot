# assistant_emploi_quebec.py

import streamlit as st
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import random
from collections import Counter
from urllib.parse import urljoin
import hashlib
from transformers import pipeline
import openai

# Configuration de la page
st.set_page_config(
    page_title="Assistant Emploi & Québec",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bases de données
DB_JOBS = "jobtracker.db"
DB_TENDERS = "quebec_tenders.db"

# Initialisation des connexions
@st.cache_resource
def init_db_jobs():
    return sqlite3.connect(DB_JOBS, check_same_thread=False)

@st.cache_resource
def init_db_tenders():
    return sqlite3.connect(DB_TENDERS, check_same_thread=False)

conn_jobs = init_db_jobs()
conn_tenders = init_db_tenders()

# Profils utilisateurs
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': 'Karim EL Alaoui',
        'email': 'karim.alaoui@gmail.com',
        'phone': '613-408-6350',
        'company': 'Freelance / Consultant IBM',
        'expertise': [
            'Salesforce', 'Service Cloud', 'Sales Cloud', 'Marketing Cloud',
            'CDP', 'Omnistudio', 'Automotive Cloud', 'AI Integration',
            'MuleSoft', 'SAP', 'Vlocity', 'Digital Transformation'
        ],
        'skills': [
            'Business Analysis', 'Agile Project Management', 'AI & Analytics',
            'IBM Watsonx', 'Salesforce Einstein', 'Cloud Architecture',
            'System Integration', 'Scrum', 'Security & Compliance'
        ],
        'certifications': [
            'Salesforce AI Associate', 'Certified Salesforce Administrator',
            'Certified Omnistudio Consultant', 'Certified Service Cloud Consultant',
            'Certified Salesforce Business Analyst', 'Certified Scrum Master'
        ],
        'languages': ['Français', 'Anglais', 'Arabe'],
        'hourly_rate': 150,
        'experience': 15
    }

# Navigation principale
page = st.sidebar.selectbox("Choisir une application", [
    "🏠 Tableau de Bord",
    "🔍 Collecte d'Offres d'Emploi",
    "🧠 Analyse IA Offres",
    "✍️ Génération Candidatures",
    "📧 Envoi Automatique",
    "🤝 LinkedIn Outreach",
    "📅 Planification RDV",
    "🔍 Collecte Appels d'Offres Québec",
    "💾 Données Québec",
    "🧠 Analyse Québec",
    "📝 Propositions Québec"
])

# FONCTIONS COMMUNES (emploi + appels d'offres)
def load_job_data():
    cur = conn_jobs.cursor()
    cur.execute("SELECT title, company, location, description, requirements, salary, platform, url, date_posted FROM offers")
    st.session_state.job_offers = [
        {
            'title': row[0], 'company': row[1], 'location': row[2], 'description': row[3],
            'requirements': row[4].split(', '), 'salary': row[5], 'platform': row[6],
            'url': row[7], 'date_posted': row[8]
        } for row in cur.fetchall()
    ]
    cur.execute("SELECT job_title, company, cover_letter, date_sent FROM applications")
    st.session_state.applications_sent = [
        {
            'job': {'title': row[0], 'company': row[1]},
            'cover_letter': row[2],
            'date_sent': row[3]
        } for row in cur.fetchall()
    ]
    cur.execute("SELECT date, company, contact, type, status FROM meetings")
    st.session_state.meetings_scheduled = [
        {
            'date': row[0], 'company': row[1], 'contact': row[2],
            'type': row[3], 'status': row[4]
        } for row in cur.fetchall()
    ]

if 'job_offers' not in st.session_state:
    st.session_state.job_offers = []
if 'applications_sent' not in st.session_state:
    st.session_state.applications_sent = []
if 'meetings_scheduled' not in st.session_state:
    st.session_state.meetings_scheduled = []

# Navigation dynamique
if page == "🔍 Collecte d'Offres d'Emploi":
    st.title("🔍 Recherche Automatisée d'Emploi")
    keywords = st.text_input("Mots-clés", "Salesforce, AI")
    location = st.selectbox("Localisation", ["Remote", "Ottawa", "Montréal", "Toronto"], index=1)
    language_required = st.checkbox("Postes bilingues FR/EN uniquement", value=True)

    if st.button("Lancer la collecte"):
        sample = [
            {'title': f"Consultant {keywords}", 'company': 'TechCorp', 'location': location,
             'description': 'Consultant senior bilingue FR/EN en transformation numérique',
             'requirements': ['Salesforce', 'AI'], 'salary': '700$/jour',
             'platform': 'LinkedIn', 'url': 'https://linkedin.com/x', 'date_posted': str(datetime.today())}
        ]
        st.session_state.job_offers = [o for o in sample if (language_required and 'bilingue' in o['description'].lower()) or not language_required]
        st.success(f"{len(st.session_state.job_offers)} offres ajoutées correspondant aux critères.")

elif page == "💾 Données Québec":
    st.title("💾 Données des appels d'offres")
    df = pd.read_sql_query("SELECT * FROM tenders ORDER BY date_collected DESC LIMIT 10", conn_tenders)
    st.dataframe(df)
    if not df.empty:
        avg_score = round(df['match_score'].mean(), 1)
        st.metric("Score moyen de correspondance", f"{avg_score}%")
        budget_values = df['budget'].str.extract(r'(\\d+)')[0].dropna().astype(int)
        if not budget_values.empty:
            mean_budget = round(budget_values.mean(), 0)
            st.metric("Budget moyen estimé", f"{mean_budget:,.0f}$")
