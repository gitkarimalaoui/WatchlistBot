
from utils.utils_intraday import fetch_intraday_data

def charger_intraday_intelligent(ticker, api_key=None):
    """Fetch intraday data from multiple free sources."""
    return fetch_intraday_data(ticker)
