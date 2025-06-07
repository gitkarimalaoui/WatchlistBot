# WatchlistBot V7.03

WatchlistBot est un assistant de trading focalisé sur les valeurs très volatiles. Le projet combine ingestion de données, scoring IA et une interface Streamlit pour suivre sa watchlist en temps réel.

## Objectif du projet

Ce dépôt fournit l'ensemble des scripts et de la documentation pour:

- Importer et fusionner des listes de tickers
- Stocker les données de marché et les informations de trading dans une base SQLite
- Visualiser et gérer la watchlist via Streamlit
- Alimenter un moteur d'apprentissage à partir des historiques de trades

## Organisation du dépôt

- `ui/` – Application Streamlit principale (`app_unifie_watchlistbot.py`).
- `scripts/` – Outils en ligne de commande pour collecter les données et peupler la base.
- `data/` – Contient la base `trades.db` et les fichiers sources (watchlist, etc.).
- `project_doc/` – Documentation détaillée des modules et de l'architecture.
- `tests/` – Suite de tests PyTest.
- `utils/`, `models/`, `simulation/` – Modules utilisés par le bot et la partie IA.

Consultez `project_doc/project_structure.md` pour la vue d'ensemble du projet ainsi que les fiches spécifiques (`MODULE_1_WATCHLISTBOT.md`, `MODULE_2_LEARNING_ENGINE.md`, `04_core_database_and_logging_setup.md`, ...).

## Mise en place de la base de données

Le bot s'appuie sur un fichier SQLite `data/trades.db`. Pour créer les tables essentielles, exécutez par exemple :

```bash
python scripts/collect_intraday_smart.py
```

Ce script crée automatiquement les tables `watchlist` et `intraday_smart` si elles n'existent pas. Le fichier `migration/migration.sql` fournit des exemples de migrations supplémentaires.

## Lancement de l'application

1. Cloner le projet
2. Installer les dépendances (ex. `pip install -r requirements.txt`)
3. Créer un fichier `.env` avec votre clé API Finnhub :`FINNHUB_API_KEY=<votre clé>`
4. Démarrer l'interface :

```bash
streamlit run ui/app_unifie_watchlistbot.py
```

## Exécuter les tests

Après installation de `pytest`, lancez simplement :

```bash
pytest
```

pour valider les modules principaux.

## Analyse batch ChatGPT

Le script `scripts/run_chatgpt_batch.py` exploite ChatGPT pour scorer les news
de votre watchlist. Il démarre automatiquement Google Chrome avec un profil
persistant stocké dans `~/.watchlistbot_chrome`.
Lors de la première exécution, connectez-vous à
[https://chat.openai.com](https://chat.openai.com) dans la fenêtre ouverte.

Ensuite, lancez simplement :

```bash
python scripts/run_chatgpt_batch.py
```

