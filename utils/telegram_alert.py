from typing import Union

from .telegram_utils import MISSING_CREDENTIALS, send_telegram_message


def send_telegram_alert(message: str) -> Union[bool, str]:
    """Backward compatible wrapper around ``send_telegram_message``."""
    return send_telegram_message(message)
