
from datetime import datetime
from simulate_trade_result import executer_trade_simule

from core.db import get_session
from core.models import TradeSimule

def enregistrer_trade_simule(ticker, entry_price, quantity, sl=None, tp=None, exit_price=None, provenance='streamlit', note=''):
    result = executer_trade_simule(
        ticker=ticker,
        entry_price=entry_price,
        quantity=quantity,
        sl=sl,
        tp=tp,
        exit_price=exit_price
    )
    session = get_session()
    trade = TradeSimule(
        ticker=ticker,
        prix_achat=entry_price,
        quantite=quantity,
        frais=result["frais_total"],
        montant_total=result["montant_total"],
        sl=sl,
        tp=tp,
        exit_price=exit_price,
        provenance=provenance,
        note=note,
        date=datetime.now(),
    )
    session.add(trade)
    session.commit()
    session.close()
