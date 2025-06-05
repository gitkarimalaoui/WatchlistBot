"""
Simulation d’un trade avec calcul de frais, SL/TP, gain net.
Utilisé dans les modules IA et interfaces manuelles.
"""

def executer_trade_simule(ticker, entry_price, quantity, sl, tp, exit_price=None):
    """
    Simule un trade avec :
    - prix d'entrée
    - quantité
    - stop-loss (SL)
    - take-profit (TP)
    - prix de sortie (optionnel pour override)

    Applique les frais réels de Moomoo :
    - Commission : 0.0049$/action, min 0.99$
    - Frais plateforme : 0.005$/action, min 1$, max 1% du total
    """
    # Calcul du montant d'achat
    montant = entry_price * quantity

    # Frais commission
    commission = max(0.0049 * quantity, 0.99)

    # Frais de plateforme
    plateforme = max(1.00, min(0.005 * quantity, 0.01 * montant))  # max 1%

    total_frais = round(commission + plateforme, 2)

    # Détermination du prix de sortie
    if exit_price is None:
        # Exécution virtuelle selon SL/TP
        if tp and tp > entry_price:
            exit_price = tp
        elif sl and sl < entry_price:
            exit_price = sl
        else:
            exit_price = entry_price  # aucune variation détectée

    gain_brut = (exit_price - entry_price) * quantity
    gain_net = round(gain_brut - total_frais, 2)

    return {
        "ticker": ticker,
        "entry": entry_price,
        "exit": exit_price,
        "quantity": quantity,
        "sl": sl,
        "tp": tp,
        "frais_total": total_frais,
        "gain_net": gain_net,
        "executed": True,
    }
