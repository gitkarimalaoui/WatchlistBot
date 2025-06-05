
import sqlite3
from datetime import datetime
from simulate_trade_result import executer_trade_simule

def enregistrer_trade_simule(ticker, entry_price, quantity, sl=None, tp=None, exit_price=None, provenance='streamlit', note=''):
    result = executer_trade_simule(
        ticker=ticker,
        entry_price=entry_price,
        quantity=quantity,
        sl=sl,
        tp=tp,
        exit_price=exit_price
    )

    conn = sqlite3.connect('./data/trades.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades_simules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            prix_achat REAL,
            quantite INTEGER,
            frais REAL,
            montant_total REAL,
            sl REAL,
            tp REAL,
            exit_price REAL,
            date TEXT,
            provenance TEXT,
            note TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO trades_simules (
            ticker, prix_achat, quantite, frais, montant_total, sl, tp, exit_price, date, provenance, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticker, entry_price, quantity,
        result["frais_total"],
        result["montant_total"],
        sl, tp, exit_price,
        datetime.now().isoformat(),
        provenance, note
    ))

    conn.commit()
    conn.close()
