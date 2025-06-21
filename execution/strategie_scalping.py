import time
from datetime import datetime
from typing import Optional


class TrailingManager:
    """Simple trailing stop manager.

    Once the price gains more than 2% from entry the stop is moved to
    break even. When gains exceed 5% it is moved to secure roughly 3%
    profit. ``update`` returns the potentially adjusted stop loss.
    """

    def __init__(self, entry_price: float, stop_loss: float) -> None:
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self._breakeven_done = False
        self._secure_done = False

    def update(self, price: float) -> float:
        gain_pct = (price - self.entry_price) / self.entry_price * 100
        if not self._breakeven_done and gain_pct >= 2:
            self.stop_loss = max(self.stop_loss, self.entry_price)
            self._breakeven_done = True
        if not self._secure_done and gain_pct >= 5:
            self.stop_loss = max(self.stop_loss, self.entry_price * 1.03)
            self._secure_done = True
        return self.stop_loss


import pandas as pd

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
    get_atr,
)
from data.stream_data_manager import get_latest_data
from utils.execution_reelle import executer_ordre_reel
from notifications.telegram_bot import envoyer_alerte_ia
from db.trades import get_nb_trades_du_jour, enregistrer_trade_auto


def enter_breakout(
    ticker: str,
    volume_spike: float = 3.0,
    min_body_ratio: float = 0.5,
) -> bool:
    """Return ``True`` if the last 1m candle shows a breakout."""
    try:
        import yfinance as yf

        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if len(df) < 2:
            return False
        last = df.iloc[-1]
        prev = df.iloc[-2]
        if prev["Volume"] == 0:
            return False
        vol_ratio = last["Volume"] / prev["Volume"]
        body = abs(last["Close"] - last["Open"])
        rng = last["High"] - last["Low"]
        body_ratio = body / rng if rng else 0
        breakout = last["Close"] > prev["High"]
        return bool(
            vol_ratio >= volume_spike and body_ratio >= min_body_ratio and breakout
        )
    except Exception:
        return False


def enter_pullback(
    ticker: str,
    volume_spike: float = 3.0,
    min_body_ratio: float = 0.5,
) -> bool:
    """Return ``True`` if the last 1m candle confirms a pullback."""
    try:
        import yfinance as yf

        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if len(df) < 2:
            return False
        last = df.iloc[-1]
        prev = df.iloc[-2]
        if prev["Volume"] == 0:
            return False
        vol_ratio = last["Volume"] / prev["Volume"]
        body = abs(last["Close"] - last["Open"])
        rng = last["High"] - last["Low"]
        body_ratio = body / rng if rng else 0
        pullback = last["Open"] < prev["Close"] < last["Close"]
        return bool(
            vol_ratio >= volume_spike and body_ratio >= min_body_ratio and pullback
        )
    except Exception:
        return False


def _compute_score(ticker: str) -> Optional[dict]:
    rsi = get_rsi(ticker)
    emas = get_ema(ticker, [9, 21])
    vwap = get_vwap(ticker)
    macd, macd_signal = get_macd(ticker)
    tick_data = get_latest_data(ticker)
    if tick_data.get("status") != "ERR":
        volume_now = tick_data.get("volume")
        last_price = tick_data.get("price")
    else:
        volume_now = get_volume(ticker, "1m")
        last_price = get_last_price(ticker)

    # Ensure scalar values to avoid pandas truth ambiguity
    if isinstance(last_price, pd.Series):
        last_price = last_price.squeeze()
    if isinstance(vwap, pd.Series):
        vwap = vwap.squeeze()
    volume_5min_ago = get_volume(ticker, "5m")
    price_prev = get_price_5s_ago(ticker)
    float_val = get_float(ticker)
    catalyst = get_catalyseur_score(ticker)
    atr = get_atr(ticker)

    # gap filter between previous close and today's open
    gap_pct = None
    try:
        import yfinance as yf

        df_gap = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(df_gap) >= 2:
            prev_close = float(df_gap["Close"].iloc[-2])
            today_open = float(df_gap["Open"].iloc[-1])
            gap_pct = (today_open - prev_close) / prev_close * 100
            if abs(gap_pct) >= 15:
                return None
    except Exception:
        pass

    if last_price is None or price_prev is None or volume_now is None:
        return None

    momentum = last_price / price_prev if price_prev else 1.0
    if not check_breakout_sustain(momentum, volume_now, volume_5min_ago or 0):
        return None

    score = 0
    if rsi is not None and 65 <= rsi <= 72:
        score += 8
    if (
        emas.get(9) is not None
        and emas.get(21) is not None
        and emas[21] != 0
        and emas[9] / emas[21] > 1.001
    ):
        score += 20
    if vwap is not None and last_price < vwap * 0.998:
        score += 5
    if volume_now is not None and volume_now > 750_000:
        score += 20
    if float_val is not None and float_val < 100_000_000:
        score += 4
    if catalyst is not None and catalyst > 0.7:
        score += 35
    if (
        macd is not None
        and macd_signal is not None
        and macd > macd_signal
        and momentum > 1
    ):
        score += 8

    stop_loss = None
    take_profit = None
    trailing_atr = None
    if atr is not None and last_price:
        sl_pct = min((2 * atr) / last_price, 0.08)
        stop_loss = round(last_price * (1 - sl_pct), 4)
        take_profit = round(last_price * 1.05, 4)
        trailing_atr = round(atr * 1.5, 4)

    return {
        "score": score,
        "price": last_price,
        "momentum": momentum,
        "volume": volume_now,
        "source": tick_data.get("source", "FALLBACK"),
        "atr": atr,
        "gap_pct": gap_pct,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "trailing_atr": trailing_atr,
    }


def executer_strategie_scalping(
    ticker: str,
    volume_spike: float = 3.0,
    min_body_ratio: float = 0.5,
) -> Optional[dict]:
    """Execute l'algorithme de scalping sur ``ticker``.

    Retourne un dict si un trade est lancé, sinon ``None``.
    """

    now = datetime.utcnow()
    if now.hour == 13 and now.minute < 45:
        return None
    if now.hour == 20 and now.minute > 45:
        return None

    today = now
    if get_nb_trades_du_jour(ticker, today) >= 3:
        return None

    data = _compute_score(ticker)
    if not data:
        return None

    if data["score"] < 80:
        return None

    if not (
        enter_breakout(ticker, volume_spike, min_body_ratio)
        or enter_pullback(ticker, volume_spike, min_body_ratio)
    ):
        return None

    time.sleep(2)
    envoyer_alerte_ia(ticker, data["score"], data["momentum"])
    res = executer_ordre_reel(ticker, data["price"], 1, action="achat")
    enregistrer_trade_auto(ticker, "achat", data["price"], 1)
    data["ordre"] = res
    # Preserve backward compatibility: return order details directly
    res["score"] = data["score"]
    res["momentum"] = data["momentum"]
    return res
