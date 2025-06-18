
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime

DB_PATH = 'cafe_management.db'

def init_table():
    """Create the ``chiffre_affaire`` table if needed.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chiffre_affaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total REAL DEFAULT 0,
            chaud REAL DEFAULT 0,
            froid REAL DEFAULT 0,
            autres REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def insert_chiffre_affaire(entry_date, total=None, chaud=None, froid=None, autres=None):
    """Insert or update daily revenue values.

    Args:
        entry_date (str): Date of the entry.
        total (float | None): Total revenue amount.
        chaud (float | None): Hot drinks revenue.
        froid (float | None): Cold drinks revenue.
        autres (float | None): Other sales revenue.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM chiffre_affaire WHERE date = ?', (entry_date,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute('''
            UPDATE chiffre_affaire
            SET total = ?, chaud = ?, froid = ?, autres = ?
            WHERE date = ?
        ''', (total, chaud, froid, autres, entry_date))
    else:
        cursor.execute('''
            INSERT INTO chiffre_affaire (date, total, chaud, froid, autres)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_date, total, chaud, froid, autres))
    conn.commit()
    conn.close()

def get_chiffre_affaire_by_month(year, month):
    """Return revenue records for the specified month.

    Args:
        year (int): Year of interest.
        month (int): Month number (1-12).

    Returns:
        pd.DataFrame: DataFrame containing turnover entries.
    """

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year + 1 if month == 12 else year}-{(month % 12) + 1:02d}-01"
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('''
        SELECT * FROM chiffre_affaire
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    ''', conn, params=(start_date, end_date))
    conn.close()
    return df

def interface_chiffre_affaire():
    """Streamlit UI to manage daily turnover entries.

    Returns:
        None
    """

    st.header("💵 Chiffre d'Affaire Journalier")
    init_table()

    tab1, tab2 = st.tabs(["📝 Saisie", "📊 Consultation Mensuelle"])

    with tab1:
        entry_date = st.date_input("Date", value=date.today())
        mode = st.radio("Mode de saisie", ["Total seulement", "Détail par catégorie"])

        if mode == "Total seulement":
            total = st.number_input("💰 Total Chiffre d'Affaire (DH)", min_value=0.0, step=0.1)
            chaud = froid = autres = None
        else:
            chaud = st.number_input("☕ Boissons Chaudes (DH)", min_value=0.0, step=0.1)
            froid = st.number_input("🥤 Boissons Froides (DH)", min_value=0.0, step=0.1)
            autres = st.number_input("🍰 Autres Ventes (DH)", min_value=0.0, step=0.1)
            total = chaud + froid + autres

        if st.button("💾 Enregistrer le chiffre d'affaire"):
            insert_chiffre_affaire(str(entry_date), total, chaud, froid, autres)
            st.success(f"✅ Chiffre d'affaire du {entry_date} enregistré avec succès !")
            st.info(f"💰 Total : {total:.2f} DH")

    with tab2:
        year = st.selectbox("Année", list(range(2020, 2031)), index=5)
        month = st.selectbox("Mois", list(range(1, 13)), index=datetime.now().month - 1)

        df = get_chiffre_affaire_by_month(year, month)
        if not df.empty:
            st.subheader("📅 Chiffre d'Affaire par Jour")
            df["date"] = pd.to_datetime(df["date"])
            st.dataframe(df)

            st.subheader("📈 Résumé Consolidé")
            total = df["total"].sum()
            chaud = df["chaud"].sum()
            froid = df["froid"].sum()
            autres = df["autres"].sum()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Total", f"{total:.2f} DH")
            col2.metric("☕ Chaud", f"{chaud:.2f} DH")
            col3.metric("🥤 Froid", f"{froid:.2f} DH")
            col4.metric("🍰 Autres", f"{autres:.2f} DH")
        else:
            st.warning("Aucune donnée disponible pour ce mois.")
