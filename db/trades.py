import os
import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trades.db")


def get_nb_trades_du_jour(ticker: str, date: datetime, db_path: str = DB_PATH) -> int:
    """Retourne le nombre de trades enregistrés pour ``ticker`` à la date donnée."""
    if not os.path.exists(db_path):
        return 0
    conn = sqlite3.connect(db_path)
    try:
        date_str = date.strftime("%Y-%m-%d")
        row = conn.execute(
            "SELECT COUNT(*) FROM trades_reels WHERE symbol = ? AND timestamp LIKE ?",
            (ticker, f"{date_str}%"),
        ).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def enregistrer_trade_auto(
    ticker: str,
    action: str,
    prix: float,
    quantite: int,
    provenance: str = "scalping",
    db_path: str = DB_PATH,
) -> None:
    """Insère un trade automatique dans la base SQLite."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades_auto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                action TEXT,
                prix REAL,
                quantite INTEGER,
                provenance TEXT,
                timestamp TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO trades_auto (ticker, action, prix, quantite, provenance, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (ticker, action, prix, quantite, provenance, datetime.utcnow().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def enregistrer_trade_ia(
    ticker: str,
    prix: float,
    montant: float,
    score: int,
    pump_pct: float,
    rsi: float,
    ema9: float,
    ema21: float,
    momentum: float,
    source: str,
) -> None:
    conn = sqlite3.connect("data/trades.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO trades (datetime, ticker, action, prix, montant, score_at_entry,
        pump_pct_60s, rsi_at_entry, ema9, ema21, momentum, source_data)
        VALUES (datetime('now'), ?, 'achat', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ticker, prix, montant, score, pump_pct, rsi, ema9, ema21, momentum, source),
    )
    conn.commit()
    conn.close()
