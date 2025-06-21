import subprocess
import sqlite3
from datetime import datetime

from core.db import DB_PATH


def executer_ordre_reel(ticker: str, prix: float, quantite: int, action: str = "achat") -> dict:
    """Exécute un ordre réel via le script Moomoo local.

    Args:
        ticker (str): Le symbole de l'action.
        prix (float): Le prix limite de l'ordre.
        quantite (int): La quantité à acheter ou vendre.
        action (str): 'achat' ou 'vente'

    Returns:
        dict: Résultat de l'exécution (success, message)
    """
    try:
        prix = round(float(prix), 2)
        quantite = int(quantite)

        if prix <= 0 or quantite <= 0:
            return {"success": False, "message": "Prix ou quantité invalide"}

        if action == "vente":
            return {"success": False, "message": "Vente réelle non encore implémentée."}

        subprocess.run([
            "python",
            os.path.join("scripts", "executer_ordre_moomoo.py"),
            ticker,
            str(prix),
            str(quantite),
        ], check=True)

        # Log vers trades.db si possible
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "CREATE TABLE IF NOT EXISTS trades_reels (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, price REAL, qty INTEGER, side TEXT, timestamp TEXT, source TEXT)"
            )
            conn.execute(
                "INSERT INTO trades_reels (symbol, price, qty, side, timestamp, source) VALUES (?, ?, ?, ?, ?, ?)",
                (ticker, prix, quantite, action, datetime.utcnow().isoformat(), "streamlit"),
            )
            conn.commit()
        finally:
            conn.close()

        return {
            "success": True,
            "message": f"Ordre réel exécuté : {ticker} à {prix}$ x{quantite}",
        }

    except subprocess.CalledProcessError as e:
        return {"success": False, "message": f"Erreur d'exécution du script : {e}"}
    except Exception as e:
        return {"success": False, "message": str(e)}
