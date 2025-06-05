import sqlite3
import pandas as pd

def init_database():
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achats_quotidiens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            lait REAL DEFAULT 0,
            sucre REAL DEFAULT 0,
            eau REAL DEFAULT 0,
            viennoiserie REAL DEFAULT 0,
            pain REAL DEFAULT 0,
            the REAL DEFAULT 0,
            bonbon_gaz REAL DEFAULT 0,
            banane REAL DEFAULT 0,
            pomme REAL DEFAULT 0,
            olive REAL DEFAULT 0,
            orange REAL DEFAULT 0,
            produit_nettoyage REAL DEFAULT 0,
            semoule REAL DEFAULT 0,
            fromage REAL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS charges_fixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type_charge TEXT NOT NULL,
            serveur_1 REAL DEFAULT 0,
            serveur_2 REAL DEFAULT 0,
            barman_1 REAL DEFAULT 0,
            barman_2 REAL DEFAULT 0,
            femme_menage_1 REAL DEFAULT 0,
            femme_menage_2 REAL DEFAULT 0,
            wifi REAL DEFAULT 0,
            electricite REAL DEFAULT 0,
            eau_magasin REAL DEFAULT 0,
            taxe_debit_boisson REAL DEFAULT 0,
            tva REAL DEFAULT 0,
            comptable REAL DEFAULT 0,
            taxe_professionnelle REAL DEFAULT 0,
            is_impot REAL DEFAULT 0,
            taxe_locale_terrasse REAL DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

def insert_achat_quotidien(date_achat, achats_data):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM achats_quotidiens WHERE date = ?', (date_achat,))
    existing = cursor.fetchone()

    if existing:
        placeholders = ', '.join([f"{k} = ?" for k in achats_data.keys()])
        values = list(achats_data.values()) + [date_achat]
        cursor.execute(f'UPDATE achats_quotidiens SET {placeholders} WHERE date = ?', values)
    else:
        columns = ', '.join(['date'] + list(achats_data.keys()))
        placeholders = ', '.join(['?'] * (len(achats_data) + 1))
        values = [date_achat] + list(achats_data.values())
        cursor.execute(f'INSERT INTO achats_quotidiens ({columns}) VALUES ({placeholders})', values)

    conn.commit()
    conn.close()

def insert_charges_fixes(date_charge, type_charge, charges_data):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM charges_fixes WHERE date = ? AND type_charge = ?', (date_charge, type_charge))
    existing = cursor.fetchone()

    if existing:
        placeholders = ', '.join([f"{k} = ?" for k in charges_data.keys()])
        values = list(charges_data.values()) + [date_charge, type_charge]
        cursor.execute(f'UPDATE charges_fixes SET {placeholders} WHERE date = ? AND type_charge = ?', values)
    else:
        columns = ', '.join(['date', 'type_charge'] + list(charges_data.keys()))
        placeholders = ', '.join(['?'] * (len(charges_data) + 2))
        values = [date_charge, type_charge] + list(charges_data.values())
        cursor.execute(f'INSERT INTO charges_fixes ({columns}) VALUES ({placeholders})', values)

    conn.commit()
    conn.close()

def get_data_by_period(start_date, end_date):
    conn = sqlite3.connect('cafe_management.db')
    achats_df = pd.read_sql_query('''
        SELECT * FROM achats_quotidiens 
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    ''', conn, params=(start_date, end_date))

    charges_df = pd.read_sql_query('''
        SELECT * FROM charges_fixes 
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    ''', conn, params=(start_date, end_date))

    conn.close()
    return achats_df, charges_df


def get_chiffre_affaire_by_period(start_date, end_date):
    conn = sqlite3.connect('cafe_management.db')
    df = pd.read_sql_query('''
        SELECT * FROM chiffre_affaire
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    ''', conn, params=(start_date, end_date))
    conn.close()
    return df
