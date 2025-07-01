import streamlit as st
from typing import Dict

from utils.utils_crypto import fetch_crypto_prices

COINS = {
    "bitcoin": "BTC",
    "ripple": "XRP",
    "solana": "SOL",
}


def show_crypto_section() -> None:
    """Display current prices for a small crypto watchlist."""
    st.title("💱 Cryptomonnaies")
    data: Dict[str, Dict[str, float]] = fetch_crypto_prices(list(COINS.keys()))
    if not data:
        st.error("Impossible de récupérer les données CoinGecko")
        return

    cols = st.columns(len(COINS))
    for idx, (coin_id, symbol) in enumerate(COINS.items()):
        coin = data.get(coin_id, {})
        price = coin.get("usd")
        change = coin.get("usd_24h_change")
        vol = coin.get("usd_24h_vol")
        cols[idx].metric(
            symbol,
            f"${price:,.2f}" if price is not None else "N/A",
            f"{change:.2f}%" if change is not None else "N/A",
        )
        cols[idx].write(
            f"Volume 24h: {vol:,.0f}" if vol is not None else "Volume N/A"
        )
