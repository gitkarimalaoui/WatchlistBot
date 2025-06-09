
import json
import os
from datetime import datetime

from core.db import get_session
from core.models import TradeSimule

JOURNAL_PATH = "journal_simule.json"  # deprecated
META_PATH = "meta_ia.json"

def charger_journal():
    """Charge les trades simulés depuis la base de données."""
    session = get_session()
    trades = session.query(TradeSimule).all()
    session.close()
    journal = []
    for t in trades:
        journal.append(
            {
                "prix_achat": t.prix_achat,
                "prix_vente": t.exit_price,
                "qty": t.quantite,
                "frais": t.frais,
                "pattern": t.provenance,
            }
        )
    return journal

def charger_meta():
    if not os.path.exists(META_PATH):
        return {}
    with open(META_PATH, "r") as f:
        return json.load(f)

def sauvegarder_meta(meta):
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

def analyser_performance_trades():
    journal = charger_journal()
    meta = charger_meta()

    if "apprentissage" not in meta:
        meta["apprentissage"] = {}

    apprentissage = meta["apprentissage"]

    for trade in journal:
        if trade.get("prix_vente") is not None:
            achat = trade["prix_achat"]
            vente = trade["prix_vente"]
            frais = trade.get("frais", 0) + trade.get("frais_vente", 0)
            profit = (vente - achat) * trade["qty"] - frais

            if profit > 0:
                pattern = trade.get("pattern", "pattern_inconnu")
                apprentissage.setdefault(pattern, {"gagnants": 0, "perdants": 0})
                apprentissage[pattern]["gagnants"] += 1
            else:
                pattern = trade.get("pattern", "pattern_inconnu")
                apprentissage.setdefault(pattern, {"gagnants": 0, "perdants": 0})
                apprentissage[pattern]["perdants"] += 1

    meta["derniere_mise_a_jour"] = datetime.now().isoformat()
    meta["apprentissage"] = apprentissage
    sauvegarder_meta(meta)
    return meta
