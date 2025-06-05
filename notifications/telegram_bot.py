
import requests
import os

# Paramètres Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TON_BOT_TOKEN_ICI")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "TON_CHAT_ID_ICI")

def envoyer_alerte_ia(ticker, score_ia, gain_estime):
    if TELEGRAM_TOKEN.startswith("TON_") or TELEGRAM_CHAT_ID.startswith("TON_"):
        print("❌ Config Telegram manquante.")
        return False

    message = f"📡 *ALERTE IA - {ticker}*\n" \
              f"🔢 *Score IA* : {score_ia:.1f}%\n" \
              f"💰 *Gain estimé* : {gain_estime:.2f} $\n" \
              f"📈 Potentiel détecté par WatchlistBot"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response.ok
