import time
from datetime import datetime
from typing import Optional

from data.indicateurs import (
    get_rsi,
    get_ema,
    get_vwap,
    get_macd,
    get_volume,
    get_last_price,
    get_price_5s_ago,
    get_float,
    get_catalyseur_score,
    check_breakout_sustain,
)
from utils.execution_reelle import executer_ordre_reel
from notifications.telegram_bot import envoyer_alerte_ia
from db.trades import get_nb_trades_du_jour, enregistrer_trade_auto


def _compute_score(ticker: str) -> Optional[dict]:
    rsi = get_rsi(ticker)
    emas = get_ema(ticker, [9, 21])
    vwap = get_vwap(ticker)
    macd, macd_signal = get_macd(ticker)
    volume_now = get_volume(ticker, "1m")
    volume_5min_ago = get_volume(ticker, "5m")
    last_price = get_last_price(ticker)
    price_prev = get_price_5s_ago(ticker)
    float_val = get_float(ticker)
    catalyst = get_catalyseur_score(ticker)

    if last_price is None or price_prev is None or volume_now is None:
        return None

    momentum = last_price / price_prev if price_prev else 1.0
    if not check_breakout_sustain(momentum, volume_now, volume_5min_ago or 0):
        return None

    score = 0
    if rsi is not None and 65 <= rsi <= 72:
        score += 10
    if (
        emas.get(9) is not None
        and emas.get(21) is not None
        and emas[21] != 0
        and emas[9] / emas[21] > 1.001
    ):
        score += 25
    if vwap is not None and last_price < vwap * 0.998:
        score += 5
    if volume_now is not None and volume_now > 750_000:
        score += 15
    if float_val is not None and float_val < 100_000_000:
        score += 5
    if catalyst is not None and catalyst > 0.7:
        score += 30
    if macd is not None and macd_signal is not None and macd > macd_signal and momentum > 1:
        score += 10

    return {
        "score": score,
        "price": last_price,
        "momentum": momentum,
        "volume": volume_now,
    }


def executer_strategie_scalping(ticker: str) -> Optional[dict]:
    """Execute l'algorithme de scalping sur ``ticker``.

    Retourne un dict si un trade est lancé, sinon ``None``.
    """

    today = datetime.utcnow()
    if get_nb_trades_du_jour(ticker, today) >= 3:
        return None

    data = _compute_score(ticker)
    if not data:
        return None

    if data["score"] < 80:
        return None

    time.sleep(2)
    envoyer_alerte_ia(ticker, data["score"], data["momentum"])
    res = executer_ordre_reel(ticker, data["price"], 1, action="achat")
    enregistrer_trade_auto(ticker, "achat", data["price"], 1)
    data["ordre"] = res
    return data
