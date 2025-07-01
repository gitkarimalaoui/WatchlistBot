import requests
from typing import Dict, List

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_crypto_prices(coins: List[str], vs_currency: str = "usd") -> Dict[str, Dict[str, float]]:
    """Return current price and 24h change/volume for the given coins.

    Parameters
    ----------
    coins: List[str]
        Coin IDs recognized by CoinGecko (e.g. "bitcoin").
    vs_currency: str, default "usd"
        Fiat currency for the price.
    """
    if not coins:
        return {}

    params = {
        "ids": ",".join(coins),
        "vs_currencies": vs_currency,
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
    }

    try:
        response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[Coingecko ERROR] {e}")
        return {}
