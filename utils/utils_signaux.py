"""Fonctions pour détecter les signaux techniques d'achat."""


def is_buy_signal(stock: dict) -> bool:
    """Détecte si toutes les conditions techniques sont réunies pour un signal d'achat."""
    try:
        return (
            stock.get("ema9", 0) > stock.get("ema21", 0)
            and stock.get("macd", 0) > stock.get("macd_signal", 0)
            and stock.get("price", 0) > stock.get("vwap", 9999)
            and stock.get("volume_ratio", 0) > 2.0
            and (
                stock.get("score_ia", 0) >= 75
                or stock.get("has_catalyst", False)
            )
        )
    except Exception:
        return False


def is_scalping_ready(stock: dict) -> bool:
    """Ensure spread is acceptable for scalping."""
    try:
        spread = float(stock.get("spread_pct", 999))
        return spread < 0.5
    except Exception:
        return False

