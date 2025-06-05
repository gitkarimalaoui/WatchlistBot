
# 📲 MODULE 9 – Telegram Alerts : `telegram_bot.py`

## 🎯 Objectif du module
Ce module permet d’envoyer des **notifications Telegram intelligentes** à l’utilisateur lorsqu’un événement important se produit (trade exécuté, fin de journée, score élevé, etc.).

---

## 📂 Fichier principal
- `telegram_bot.py` (anciennement `telegram_alerts.py`)

### 📁 Chemin projet recommandé :
```
BOTV7/notifications/telegram_bot.py
```

---

## 🔧 Fonction principale

### `envoyer_alerte_telegram(titre, message, ticker, chat_id=CHAT_ID)`
- Envoie un message HTML enrichi via Telegram
- Ajoute un lien direct vers Moomoo : `[Ticker Link]`
- Gère les erreurs de manière robuste (timeout, API errors)

#### Exemple :
```python
envoyer_alerte_telegram(
    "🔥 Signal détecté",
    "Le ticker $XYZ a atteint un score IA de 9.5",
    "XYZ"
)
```

---

## 🔐 Paramètres sensibles (à sécuriser)

| Élément       | Statut actuel     | Recommandation                        |
|----------------|-------------------|----------------------------------------|
| `BOT_TOKEN`     | Codé en dur (❌)   | 🔐 À extraire dans `config.py` ou `.env` |
| `CHAT_ID`       | Statique          | ✅ OK pour usage personnel              |

---

## 🔗 Intégrations prévues / existantes

| Module connecté           | Rôle de l’alerte                     |
|----------------------------|--------------------------------------|
| `cloture.py`              | Résumé de fin de journée             |
| `simulate_trade_result.py`| Alerte sur trade simulé              |
| `run_chatgpt_batch.py`    | Score élevé GPT → push immédiat      |
| `watchlist_monitor.py`    | Anomalie ou signal IA détecté        |

---

## 📌 Historique

- **2025-05-21** : Intégré et renommé depuis `telegram_alerts.py`
- ✅ Ancien placeholder `telegram_bot.py` supprimé

