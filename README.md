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

## Modules principaux

Plusieurs scripts en doublon (`app_unifie_watchlistbotx.py`, `ai_scorerx.py`, `order_executorx.py`…) ont été retirés. Les chemins à utiliser sont désormais :

- `ui/app_unifie_watchlistbot.py` – interface Streamlit centrale
- `ui/utils_affichage_ticker.py` – affichage détaillé des tickers
- `intelligence/ai_scorer.py` – calcul du score IA
- `utils/utils_graph.py` – chargement historique & intraday
- `utils/utils_finnhub.py` – récupération des données Finnhub
- `scripts/run_chatgpt_batch.py` – scoring GPT des news
- `scripts/scraper_jaguar.py` – scraping des posts Jaguar
- `scripts/load_watchlist.py` – import de la watchlist


## Mise en place de la base de données

Le bot s'appuie sur un fichier SQLite `data/trades.db`. Pour créer les tables essentielles, exécutez par exemple :

```bash
python scripts/collect_intraday_smart.py
```

Ce script crée automatiquement les tables `watchlist` et `intraday_smart` si elles n'existent pas. Le fichier `migration/migration.sql` fournit des exemples de migrations supplémentaires.

## Lancement de l'application

1. Cloner le projet
2. Installer les dépendances (ex. `pip install -r requirements.txt`)
3. Créer un fichier `.env` (voir exemple ci-dessous) et y renseigner vos clés API :
   ```
FINNHUB_API_KEY=YOUR_FINNHUB_KEY
ALPHA_VANTAGE_API_KEY=YOUR_ALPHA_VANTAGE_KEY
FMP_API_KEY=YOUR_FMP_KEY
POLYGON_API_KEY=YOUR_POLYGON_KEY
REFRESH_INTERVAL=15
DEBUG_MODE=False
   ```
4. Démarrer l'interface :

```bash
streamlit run ui/app_unifie_watchlistbot.py
```

## Exécuter les tests

Avant de lancer la suite de tests, installez les dépendances :

```bash
pip install -r requirements.txt
```

Les tests requièrent en particulier les packages `pandas` et `SQLAlchemy`,
ainsi que `finrl` et `stable-baselines3`, en plus de `pytest`.

Ensuite lancez simplement :

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

Les scores calculés sont enregistrés dans la table `news_score` **et** mis à
jour dans `watchlist.score`. Ainsi, la page Streamlit reflète immédiatement
les nouvelles analyses.

## LLM local (Mistral)

WatchlistBot peut exploiter un modèle de langage local basé sur Mistral pour
éviter les appels à l'API OpenAI. Placez le fichier
`models/mistral/mistral-7b-instruct-v0.2.Q4_K_M.gguf` dans le dépôt puis
installez la dépendance `llama-cpp-python`.

Dans l'interface Streamlit, une case à cocher permet d'activer l'option et de
charger le modèle local. Cette fonctionnalité sera prochainement couplée au
script `learning_loop.py` afin d'améliorer la boucle d'apprentissage.

## Entraînement du modèle

Pour lancer l'apprentissage par renforcement, utilisez :

```bash
python intelligence/learning_loop.py
```

Cette phase nécessite les packages `finrl` et `stable-baselines3` présents dans
`requirements.txt`.


## Surveillance automatique avec Codex

Un script de veille permet d'analyser les nouveaux fichiers produits par FinRL et les mises à jour des logs. Il se lance simplement avec :

```bash
python start_watchers.py
```

Le watcher observe `models/finrl/` pour tout fichier `.pkl` ou `.json` ajouté et `logs/` pour les fichiers `local_llm.log` ou contenant `finrl`. À chaque événement, un appel à Codex est déclenché pour proposer automatiquement un patch ou ouvrir une pull request.
