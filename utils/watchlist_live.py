from __future__ import annotations

from typing import Iterable, List, Dict

from utils.telegram_utils import send_telegram_message

# Track which tickers already triggered a pump notification
seen_pumps: set[str] = set()


def get_watchlist_data_for_ui(entries: Iterable[Dict]) -> List[Dict]:
    """Return ``entries`` after sending pump alerts for new tickers.

    Parameters
    ----------
    entries : Iterable[Dict]
        Sequence of watchlist rows. Each row should provide ``ticker`` and
        ``isPump`` fields.
    """
    result: List[Dict] = []
    for entry in entries:
        ticker = entry.get("ticker")
        if entry.get("isPump") and ticker and ticker not in seen_pumps:
            send_telegram_message(f"PUMP detected on {ticker}")
            seen_pumps.add(ticker)
        result.append(entry)
    return result
