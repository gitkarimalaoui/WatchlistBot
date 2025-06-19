import sys
from utils.telegram_utils import send_telegram_message

# Ensure UTF-8 console output for emoji support
sys.stdout.reconfigure(encoding="utf-8")


def envoyer_alerte_ia(ticker, score_ia, gain_estime):
    """Send an AI alert message via Telegram."""
    message = (
        f"\U0001F4E1 *ALERTE IA - {ticker}*\n"
        f"\uD83D\uDD22 *Score IA* : {score_ia:.1f}%\n"
        f"\U0001F4B0 *Gain estimé* : {gain_estime:.2f} $\n"
        "\U0001F4C8 Potentiel détecté par WatchlistBot"
    )
    return send_telegram_message(message)
