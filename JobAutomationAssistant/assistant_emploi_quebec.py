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

# Fonctions base de données offres

def save_offer_to_db(offer):
    cur = conn_jobs.cursor()
    cur.execute("""
        INSERT INTO offers (title, company, location, description, requirements, salary, platform, url, date_posted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        offer['title'], offer['company'], offer['location'], offer['description'],
        ', '.join(offer['requirements']), offer['salary'], offer['platform'],
        offer['url'], offer['date_posted']
    ))
    conn_jobs.commit()

# Chargement des données emploi

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

if 'job_offers' not in st.session_state:
    st.session_state.job_offers = []
if 'applications_sent' not in st.session_state:
    st.session_state.applications_sent = []
if 'meetings_scheduled' not in st.session_state:
    st.session_state.meetings_scheduled = []

# Ajout de scraping API Jobbank Canada

def scrape_jobbank_offers(keywords, location, lang="bilingual"):
    api_url = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
    params = {
        "searchstring": keywords,
        "locationstring": location,
        "sort": "date",
        "fage": 7,
        "fsrc": 16,
        "lang": "en"
    }
    response = requests.get(api_url, params=params)
    offers = []
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='resultJob')
        for r in results:
            title_tag = r.find('a', class_='title')
            if not title_tag: continue
            title = title_tag.text.strip()
            url = 'https://www.jobbank.gc.ca' + title_tag.get('href')
            company_tag = r.find('div', class_='business')
            company = company_tag.text.strip() if company_tag else "Unknown"
            loc_tag = r.find('li', class_='location')
            loc = loc_tag.text.strip() if loc_tag else location
            date_tag = r.find('li', class_='date')
            date = date_tag.text.strip() if date_tag else str(datetime.today().date())
            offers.append({
                'title': title,
                'company': company,
                'location': loc,
                'description': f"Offre récupérée depuis Jobbank pour {keywords}",
                'requirements': [keywords],
                'salary': 'Non spécifié',
                'platform': 'Jobbank',
                'url': url,
                'date_posted': date
            })
    return offers

# Mise à jour collecte emploi
if page == "🔍 Collecte d'Offres d'Emploi":
    st.title("🔍 Recherche Automatisée d'Emploi")
    keywords = st.text_input("Mots-clés", "Salesforce, AI")
    location = st.selectbox("Localisation", ["Remote", "Ottawa", "Montréal", "Toronto"], index=1)
    language_required = st.checkbox("Postes bilingues FR/EN uniquement", value=True)

    if st.button("Lancer la collecte"):
        scraped = scrape_jobbank_offers(keywords, location)
        filtered = [o for o in scraped if (language_required and 'bilingue' in o['description'].lower()) or not language_required]
        for offer in filtered:
            save_offer_to_db(offer)
        load_job_data()
        st.success(f"{len(filtered)} offres Jobbank collectées et ajoutées à la base.")

    if st.session_state.job_offers:
        st.subheader("📝 Offres récemment collectées")
        for offer in st.session_state.job_offers[-5:]:
            with st.expander(f"{offer['title']} chez {offer['company']} ({offer['location']})"):
                st.write(f"**Date:** {offer['date_posted']}")
                st.write(f"**Description:** {offer['description']}")
                st.write(f"**Exigences:** {', '.join(offer['requirements'])}")
                st.write(f"**Salaire:** {offer['salary']}")
                st.write(f"[Lien vers l'offre]({offer['url']})")

# Navigation dynamique
if page == "🏠 Tableau de Bord":
    st.title("📊 Tableau de Bord - Assistant Emploi")
    load_job_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Offres en base", len(st.session_state.job_offers))
    with col2:
        st.metric("Candidatures envoyées", len(st.session_state.applications_sent))
    with col3:
        st.metric("RDV planifiés", len(st.session_state.meetings_scheduled))

    if st.session_state.job_offers:
        st.subheader("📈 Évolution des candidatures (fictif)")
        dates = pd.date_range(start=datetime.today() - timedelta(days=30), periods=30)
        df = pd.DataFrame({
            'Date': dates,
            'Candidatures': [random.randint(0, 2) for _ in range(30)],
            'Réponses': [random.randint(0, 1) for _ in range(30)]
        })
        fig = px.line(df, x='Date', y=['Candidatures', 'Réponses'], title="Activité sur 30 jours")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée d'offres encore disponible. Lancez la collecte pour commencer.")