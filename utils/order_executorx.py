
import sqlite3
from datetime import datetime

def calculer_frais_moomoo(prix_unitaire, quantite):
    montant = prix_unitaire * quantite
    commission = max(0.0049 * quantite, 0.99)
    plateforme = max(min(0.005 * quantite, 0.01 * montant), 1)
    return round(commission + plateforme, 2)

def executer_order_simule(ticker, prix_achat, quantite, db_path="data/trades.db"):
    frais = calculer_frais_moomoo(prix_achat, quantite)
    date_achat = datetime.now().isoformat()
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO trades_simules (ticker, prix_achat, quantite, frais, date_achat) VALUES (?, ?, ?, ?, ?)",
        (ticker, prix_achat, quantite, frais, date_achat)
    )
    conn.commit()
    conn.close()
    return {"ticker": ticker, "prix_achat": prix_achat, "quantite": quantite, "frais": frais, "date_achat": date_achat}
