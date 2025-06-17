"""Fonctions pour détecter les signaux techniques d'achat."""


def is_buy_signal(stock: dict) -> bool:
    """Détecte si toutes les conditions techniques sont réunies pour un signal d'achat."""
    try:
        return (
            stock.get("ema9", 0) > stock.get("ema21", 0)
            and stock.get("macd", 0) > stock.get("macd_signal", 0)
            and stock.get("price", 0) > stock.get("vwap", 9999)
            and stock.get("volume_ratio", 0) > 1.5
            and (
                stock.get("score_ia", 0) >= 70
                or stock.get("has_catalyst", False)
            )
        )
    except Exception:
        return False

