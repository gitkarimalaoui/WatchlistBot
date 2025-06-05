"""
Exécution d'un trade simulé : utilise la logique de simulate_trade_result,
puis enregistre le résultat dans la table `trades_simules`.
"""

import sqlite3
from datetime import datetime
from simulation.simulate_trade_result import executer_trade_simule

DB_PATH = "data/trades.db"

def enregistrer_trade_simule(
    ticker, entry_price, quantity, sl=None, tp=None, exit_price=None, provenance="manuel", note=None
):
    """
    Simule un trade, calcule les résultats, et enregistre dans la base SQLite.
    """

    result = executer_trade_simule(
        ticker=ticker,
        entry_price=entry_price,
        quantity=quantity,
        sl=sl,
        tp=tp,
        exit_price=exit_price
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trades_simules
            (datetime, ticker, action, prix, montant, frais, gain_net, provenance, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec='seconds'),
        result['ticker'],
        'Achat' if result['entry'] < result['exit'] else 'Vente',
        result['entry'],
        round(result['entry'] * result['quantity'], 2),
        result['frais_total'],
        result['gain_net'],
        provenance,
        note or "Simulé auto"
    ))

    conn.commit()
    conn.close()
    return result
