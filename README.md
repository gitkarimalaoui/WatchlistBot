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

## Détails des répertoires

- `data/` – Données sources et fichier SQLite `trades.db`.
- `db/` – Fonctions d'accès à la base et journalisation des trades.
- `execution/` – Stratégies et routines d'exécution d'ordres.
- `utils/` – Utilitaires communs (accès API, graphes, logs…).
- `automation/` – Watchers Codex et scripts d'automatisation.
- `realtime/` – Collecte tick par tick et détection de pumps.
- `intelligence/` – Modèles et scoring IA.
- `scripts/` – Outils CLI pour charger watchlist et news.
- `ui/` – Interface Streamlit.

Consultez `project_doc/project_structure.md` pour la vue d'ensemble du projet ainsi que les fiches spécifiques (`MODULE_1_WATCHLISTBOT.md`, `MODULE_1_ORCHESTRATEUR_EVENEMENTS.md`, `MODULE_2_LEARNING_ENGINE.md`, `04_core_database_and_logging_setup.md`, ...).

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

## Workflow complet

1. **Collecte des news** : les scripts du dossier `scripts/` récupèrent les articles et posts (ex. `scraper_jaguar.py`).
2. **Scoring** : `run_chatgpt_batch.py` ou le LLM local analyse ces news et met à jour les scores dans `data/trades.db`.
3. **Détection** : `movers_detector.py` et `pump_score.py` identifient les tickers prometteurs.
4. **Exécution** : la stratégie de scalping d'`execution/` peut être lancée automatiquement via `watchlist_loop.py` ou manuellement depuis l'interface Streamlit.
5. **Journalisation** : toutes les opérations sont enregistrées via `db/trades.py` pour suivre la performance et nourrir l'apprentissage.


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
Un écran de connexion s'affichera pour saisir votre identifiant et mot de passe.
Le rôle associé (« admin », « trader », « viewer » ou « ia_debug »)
détermine les fonctionnalités accessibles dans l'interface.

Par défaut, la sidebar filtre les tickers pour n'afficher que ceux dont
le changement est positif et dont le score global atteint au moins **50**.
Vous voyez ainsi immédiatement les opportunités d'achat potentielles.

## Installation hors ligne des dépendances

Si la machine cible n'a pas accès à Internet, préparez les paquets
nécessaires sur un poste connecté :

1. Téléchargez les fichiers wheel dans un répertoire local :
   ```bash
   pip download -d /tmp/wheels -r requirements.txt
   ```
   Vous pouvez aussi récupérer manuellement les librairies essentielles
   comme `pandas`, `SQLAlchemy`, `watchdog`, `numpy`, `requests`,
   `alembic`, `finrl` et `stable-baselines3`.
2. Copiez le dossier `/tmp/wheels` sur la machine hors ligne.
3. Installez ensuite les dépendances sans interroger PyPI :
   ```bash
   pip install --no-index --find-links /chemin/vers/wheels -r requirements.txt
   ```

Assurez‑vous que tous les packages indispensables sont présents dans ce
répertoire avant de lancer l'installation.
Vous pouvez ensuite exécuter `scripts/offline_setup.sh` pour installer les dépendances depuis ce répertoire et vérifier que tous les modules sont bien présents.

## API FastAPI

Une API légère permet de récupérer la watchlist au format JSON.
Après installation des dépendances :

```bash
pip install fastapi uvicorn
```

Lancez le serveur :

```bash
python api/watchlist_api.py
```

La route `/watchlist/live` renvoie les données utilisées par l'interface.
Depuis la version 7.03, l'application Streamlit démarre automatiquement ce
serveur en arrière‑plan s'il n'est pas déjà actif.

## Exécuter les tests

Avant de lancer la suite de tests, installez les dépendances :

```bash
pip install -r requirements.txt
```

Les tests nécessitent la plupart des modules listés dans `requirements.txt`.
Veillez notamment à installer `watchdog`, `SQLAlchemy`, `pandas`, `numpy`,
`requests` et `alembic`, ainsi que `finrl`, `stable-baselines3` et bien sûr
`pytest`.

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

## Projection 100k – Exemple

La fonction `project_target_date` du module `progress_tracker` calcule la date
prévisionnelle pour atteindre 100 000 $ selon un gain moyen journalier.

Supposons un capital initial de 20 000 $ et cinq trades par jour rapportant en
moyenne 50 $ chacun (soit 250 $ de profit quotidien). Le nombre de jours requis
est :

```python
days = math.ceil((100000 - 20000) / 250)  # 320 jours
```

Dans ce scénario, l'objectif serait atteint environ 320 jours après le début de
l'activité, tant que ce rythme reste constant.


## Surveillance automatique avec Codex

Un script de veille permet d'analyser les nouveaux fichiers produits par FinRL et les mises à jour des logs. Il se lance simplement avec :

```bash
python start_watchers.py
```

Le watcher observe `models/finrl/` pour tout fichier `.pkl` ou `.json` ajouté et `logs/` pour les fichiers `local_llm.log` ou contenant `finrl`. À chaque événement, un appel à Codex est déclenché pour proposer automatiquement un patch ou ouvrir une pull request.

## Surveillance en temps réel

L'outil `realtime/pump_detector.py` analyse les ticks pour détecter les pumps soudains. Lorsque les seuils sont atteints, un dialogue Streamlit s'affiche via `ui/trade_popup.py` pour confirmer l'exécution de l'ordre. L'ancien popup Tkinter a été supprimé.
Les ticks sont collectés par `realtime/real_time_tick_collector.py` et enregistrés directement dans la base `trades.db`.

## Utilisation manuelle et automatisée

### Exécution manuelle

- Lancer l'interface : `streamlit run ui/app_unifie_watchlistbot.py`
- Exécuter individuellement les scripts de collecte ou de scoring (ex. `python scripts/run_chatgpt_batch.py`).

### Mode automatique

- Démarrer la surveillance continue avec :

```bash
python start_watchers.py
```

Les watchers gèrent l'exécution des stratégies dès qu'un nouveau modèle ou un log pertinent est détecté.

## Module 3.5 – FinRL Advanced DRL Strategy

Ce module de formation s'appuie sur les ressources officielles [FinRL](https://github.com/AI4Finance-Foundation/FinRL).
Les notebooks sont adaptés pour entraîner un agent DRL avec nos watchlists et la table `trades_simules`.
Le modèle sauvegardé dans `intelligence/models/trained_drl_model.pkl` permet d'afficher les prédictions dans l'interface.
