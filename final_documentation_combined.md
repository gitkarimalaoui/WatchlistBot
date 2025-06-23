

# 00_intro_watchlistbot

# 📘 Chapitre 00 – Introduction Générale au Projet WatchlistBot V7.03

## 🎯 Objectif du document
Ce chapitre introduit le projet WatchlistBot V7.03, une solution unifiée de **trading algorithmique spécialisé dans les penny stocks à forte volatilité**, conçue pour une utilisation par des traders, analystes IA, développeurs, DBA et architectes techniques.

Il sert de **point d'entrée officiel** pour toute la documentation, avec une vision complète de l’écosystème du bot, les motivations, les rôles impliqués, et les fondements nécessaires pour maintenir ou faire évoluer le projet.

---

## 🧠 Contexte et Motivation
WatchlistBot a été conçu pour répondre aux problématiques suivantes :
- Détection en temps réel d’opportunités sur des titres très volatils (biotech, pharma, small caps US).
- Prise de décision assistée par IA basée sur des indicateurs techniques, fondamentaux, et catalyseurs externes.
- Exécution simulée ou réelle avec journalisation, calculs de PnL et alertes dynamiques.
- Architecture modulaire, adaptée à l’échelle locale ou cloud.

---

## 🔍 Utilisateurs cibles
| Rôle                     | Objectifs clés |
|--------------------------|----------------|
| **Trader / utilisateur**      | Interface simple, rapide, signaux IA, exécution ou simulation |
| **Développeur Python**       | Modules testables, logique claire, code modulaire |
| **Architecte logiciel**      | Structure scalable, traçabilité des flux, IA intégrée |
| **Responsable IA**           | Ajustement des modèles, retrain, analyse de performance |
| **Administrateur BDD**       | Migration, sauvegarde, surveillance des tables SQLite |
| **Testeur / QA**             | Couverture des cas, stratégie de non-régression |

---

## 🧩 Modules techniques clés
Le projet se compose de plusieurs **EPICs** décrits dans la documentation (voir `project_structure.md`). Parmi les modules critiques :

- `intelligence/ai_scorer.py` – Scoring IA multi-paramètres
- `execution/strategie_scalping.py` – Stratégie d’entrée/sortie avec trailing stop
- `simulation/simulate_trade_result.py` – Simulation avec frais réels
- `realtime/pump_detector.py` – Détection en direct de pumps
- `ui/app_unifie_watchlistbot.py` – Interface centralisée Streamlit
- `db/scores.py`, `db/trades.py` – Persistance des scores & journaux de trades
- `fusion/module_fusion_watchlist.py` – Agrégation des sources (manuel, IA, scrapping)

---

## 🛠️ Prérequis techniques
| Élément                 | Détail |
|-------------------------|--------|
| **Python**              | Version 3.8+ (recommandé : 3.10) |
| **Dépendances**         | Listées dans `requirements.txt` (Streamlit, pandas, yfinance, openai...) |
| **Base de données**     | SQLite – fichier `data/trades.db` |
| **API externes**        | Finnhub (clé requise), yfinance, OpenAI (optionnelle pour GPT) |
| **Système de fichiers** | Organisation en modules / sous-dossiers décrits dans `project_structure.md` |

---

## 🗃️ Tables et données principales
| Table SQLite           | Colonnes clés |
|------------------------|----------------|
| `watchlist`            | `symbol`, `source`, `score`, `timestamp` |
| `trades`               | `id`, `symbol`, `price`, `volume`, `type`, `pnl`, `date_exec` |
| `trades_simules`       | `symbol`, `entry`, `exit`, `gain`, `stop_loss`, `comment` |
| `ticks` / `intraday_smart` | `symbol`, `price`, `volume`, `timestamp` |
| `scores`               | `symbol`, `score`, `details`, `timestamp` |
| `news_score`           | `symbol`, `score_news`, `gpt_label`, `text` |

---

## 🧾 User Stories associées
- **US-GEN-001** – En tant qu’utilisateur, je souhaite avoir un point d’entrée unique pour accéder à la logique du bot.
- **US-GEN-002** – En tant que développeur, je veux comprendre l’organisation technique du projet.
- **US-GEN-003** – En tant qu’architecte, je veux pouvoir cartographier tous les modules pour garantir leur évolutivité.
- **US-GEN-004** – En tant qu’administrateur BDD, je veux pouvoir visualiser toutes les tables utilisées et leurs champs.

---

## 🔄 Liens de navigation vers les chapitres suivants
- [31 – Daily Workflow](31_daily_workflow.md)
- [05 – Import Watchlist](05_watchlist_import.md)
- [09 – Analyse IA](09_analyse_ia.md)
- [23 – Daily Closure](23_daily_closure.md)
- [28 – Pump Detector & Trailing Stop](28_pump_detector_trailing_stop.md)

---

## 📌 Notes importantes
- Tous les scripts sont interopérables via `app_unifie_watchlistbot.py`
- Le projet est conçu pour fonctionner **sans dépendance cloud critique**, à l’exception des API publiques (Finnhub, yfinance)
- Les tests unitaires sont disponibles dans `tests/`, avec un coverage partiel pour les modules IA & exécution
- Le système de `meta_ia.json` stocke les pondérations apprises automatiquement par le moteur IA

---

> 📘 **À retenir** : ce chapitre est à lire impérativement avant toute modification de code ou reprise technique du projet.

---


# 05_watchlist_import

# 📘 Chapitre 05 – Import de Watchlist (manuel, fichier, Jaguar, IA)

Ce module permet d'importer, fusionner, filtrer et enrichir une liste de tickers à analyser dans la journée. Il centralise plusieurs sources (manuel, fichier `.txt`, scraping Jaguar, scoring IA) dans une **watchlist unifiée**.

Il constitue le point d’entrée **initial** de toute session de trading IA.

---

## 🎯 Objectifs fonctionnels

- Permettre à l’utilisateur d’ajouter ou d’importer des tickers.
- Scraper automatiquement la watchlist postée par Jaguar sur StockTwits.
- Ajouter dynamiquement les tickers issus de l’IA (`meta_ia.json`).
- Générer une **watchlist fusionnée**, prête à être scorée et analysée.

---

## 📂 Sources de données watchlist

| Source          | Format / Support                | Module impliqué             |
| --------------- | ------------------------------- | --------------------------- |
| Manuel          | Interface utilisateur Streamlit | `tickers_manuels.json`      |
| Fichier externe | `.txt` simple                   | `watchlist_jaguar.txt`      |
| Scraping Jaguar | Texte posté quotidiennement     | `scripts/scraper_jaguar.py` |
| Résultats IA    | Pondérations IA pré-apprises    | `meta_ia.json`              |

---

## 🔧 Fonction de fusion centrale : `fusionner_watchlists(...)`

Localisation : `fusion/module_fusion_watchlist.py`

### Logique simplifiée :

```python
watchlist = set()
watchlist.update(lire_json("tickers_manuels.json"))
watchlist.update(charger_txt("watchlist_jaguar.txt"))
watchlist.update(extraire_tickers_meta("meta_ia.json"))
return list(sorted(watchlist))
```

---

## 🧪 Déclencheurs dans l’interface UI

- **Bouton “Importer fichier Jaguar”** : permet de charger manuellement un fichier `.txt`.
- **Scraping automatique toutes les 15 min** : déclenché en arrière-plan.
- **Ajout manuel** : champ texte + bouton “Ajouter” en Streamlit.

---

## 🧠 Filtres appliqués avant analyse IA

| Filtre           | Valeur par défaut | Raison                       |
| ---------------- | ----------------- | ---------------------------- |
| Prix minimum     | 0.5 \$            | Exclure microcaps illiquides |
| Penny stock ?    | configurable      | Permet d’exclure les < 1\$   |
| Float maximum    | 200M              | Sensibilité au pump          |
| Existence réelle | API Finnhub       | Vérification de validité     |

---

## 🗃️ Données enregistrées

Les tickers fusionnés sont insérés dans :

| Table       | Colonnes                        |
| ----------- | ------------------------------- |
| `watchlist` | `symbol`, `source`, `timestamp` |

> Chaque ligne indique la provenance : `manuel`, `fichier`, `IA`, `Jaguar`, `scraper`, etc.

---

## 🔗 Modules liés

| Module                       | Usage                                           |
| ---------------------------- | ----------------------------------------------- |
| `check_tickers.py`           | Valide que le ticker existe vraiment via API    |
| `app_unifie_watchlistbot.py` | UI Streamlit : boutons d'import, d’ajout manuel |
| `db/watchlist.py`            | Insère les tickers validés                      |
| `ai_scorer.py`               | Analyse la watchlist générée                    |

---

## 📌 User Stories associées

- **US-WL-001** – En tant qu’utilisateur, je veux ajouter manuellement un ticker.
- **US-WL-002** – En tant qu’utilisateur, je veux importer un fichier `.txt` de tickers.
- **US-WL-003** – En tant que bot, je veux scraper automatiquement la watchlist de Jaguar.
- **US-WL-004** – En tant que moteur IA, je veux fusionner toutes les sources et analyser la liste proprement.

---

> ✅ Ce module constitue le socle de départ du processus IA. Il garantit que seuls les tickers valides et intéressants passent à l'étape d’analyse.

---


# 06_simulation_engine

# 📘 Chapitre 06 – Moteur de Simulation (Simulation Engine)

Ce module est au cœur des tests de stratégie et de l’apprentissage IA : il permet de simuler des ordres d’achat et de vente avec gestion des frais, journalisation, et analyse des gains ou pertes. Il s’appuie sur une logique proche de l’exécution réelle tout en conservant une séparation claire (pas d’ordre vers broker).

---

## 🎯 Objectifs du moteur de simulation

- Simuler un achat/vente avec paramètres réels (frais, prix, quantité).
- Tester une stratégie (SL, TP, trailing, etc.).
- Enregistrer les résultats dans la base `trades.db`.
- Servir de feedback pour l’IA (modèle d’apprentissage).

---

## 📁 Modules principaux

| Fichier                    | Rôle                                          |
| -------------------------- | --------------------------------------------- |
| `simulate_trade_result.py` | Simulation principale IA + calculs            |
| `execution_simulee.py`     | Enregistrement SQL dans `trades_simules`      |
| `simulation_achat.py`      | Interface manuelle pour ajout de trade (JSON) |
| `simulation_vente.py`      | Interface manuelle pour vente simulée (JSON)  |

---

## 🧠 Fonction centrale : `executer_trade_simule()`

### Paramètres :

- `ticker`: symbole analysé
- `prix_achat`, `prix_vente`: prix de la simulation
- `quantite`: volume simulé
- `frais`: calculés automatiquement (plateforme Moomoo par défaut)
- `stop_loss`, `take_profit`, `strategie`, `commentaire`

### Logique (extrait simplifié) :

```python
def executer_trade_simule(ticker, prix_achat, prix_vente, quantite):
    frais = max(1.0, 0.005 * quantite)  # frais plateforme Moomoo
    gain = (prix_vente - prix_achat) * quantite - frais
    trade = {
        'symbol': ticker,
        'entry': prix_achat,
        'exit': prix_vente,
        'gain': round(gain, 2),
        'strategy': 'simu_trailing',
        'comment': 'test auto'
    }
    enregistrer_trade_simule(conn, trade)
    return trade
```

---

## 🧮 Modèle de frais utilisé (Moomoo Canada)

| Type de frais                | Montant                                |
| ---------------------------- | -------------------------------------- |
| Commission                   | 0.0049\$/action (min 0.99\$ par ordre) |
| Frais plateforme             | 0.005\$/action (min 1\$, max 1%)       |
| Exemple (1000 actions à 1\$) | ≈ 9.9\$ + 5\$ = 14.9\$ (en simulation) |

Les frais sont configurables dans un fichier `config/frais.json`.

---

## 💾 Table utilisée : `trades_simules`

| Colonne       | Type     | Description                         |
| ------------- | -------- | ----------------------------------- |
| `symbol`      | TEXT     | Ticker simulé                       |
| `entry`       | REAL     | Prix d’achat                        |
| `exit`        | REAL     | Prix de sortie                      |
| `gain`        | REAL     | Résultat net (après frais)          |
| `stop_loss`   | REAL     | Niveau de SL simulé (si applicable) |
| `take_profit` | REAL     | Niveau de TP simulé (si applicable) |
| `strategy`    | TEXT     | Nom de la stratégie testée          |
| `comment`     | TEXT     | Remarque IA ou utilisateur          |
| `timestamp`   | DATETIME | Horodatage du trade                 |

---

## 🔗 Intégration avec autres modules

| Module                       | Usage de la simulation |
| ---------------------------- | ---------------------- |
| `learning_loop.py`           | Apprentissage IA       |
| `ai_backtest.py`             | Validation offline     |
| `app_unifie_watchlistbot.py` | Affichage dans UI      |
| `dashboard.py`               | Résumé des gains/pnls  |

---

## 📌 User Stories associées

- **US-SIMU-001** – En tant que trader, je veux tester une idée avant de passer un ordre réel.
- **US-SIMU-002** – En tant qu’IA, je veux simuler un trade pour apprendre à ajuster mes seuils.
- **US-SIMU-003** – En tant qu’utilisateur, je veux voir mes trades simulés dans l’interface.
- **US-SIMU-004** – En tant que testeur, je veux vérifier que la logique de frais est bien prise en compte.

---

> ✅ Ce moteur permet d'itérer rapidement sur des stratégies en limitant le risque. Il est la base du module de backtest et du renforcement IA.

---


# 07_news_detection

# 📘 Chapitre 07 – Détection de News & Catalyseurs (FDA, IPO, Fusions)

Ce module identifie les catalyseurs externes (news) ayant un impact direct sur le comportement des tickers : annonces FDA, uplisting, IPO, fusions, acquisitions, etc.

Il permet de repérer en amont les titres susceptibles de connaître une forte volatilité intraday.

---

## 🎯 Objectifs fonctionnels

- Récupérer automatiquement les news liées aux tickers de la watchlist.
- Détecter des **mots-clés critiques** dans les titres et descriptions.
- Générer un **score de catalyseur** utilisé par le moteur IA.
- Afficher les événements détectés dans l’interface utilisateur.

---

## 📁 Modules & Fichiers impliqués

| Fichier                          | Rôle                                     |
| -------------------------------- | ---------------------------------------- |
| `news/finnhub_news_collector.py` | Récupération via API Finnhub             |
| `intelligence/news_scoring.py`   | Attribution d’un score `score_news`      |
| `db/news_score.py`               | Insertion dans table `news_score`        |
| `ai_scorer.py`                   | Utilise `score_news` dans le score final |

---

## 🌐 Source de données : API Finnhub

- Endpoint : `https://finnhub.io/api/v1/company-news?symbol={ticker}`
- Requête faite pour chaque ticker de la watchlist
- Fenêtre temporelle : 2 derniers jours (configurable)

---

## 🧠 Détection des catalyseurs

| Mot-clé détecté     | Pondération | Exemples                  |
| ------------------- | ----------- | ------------------------- |
| "FDA", "approval"   | +0.4        | FDA approval, drug review |
| "IPO", "listing"    | +0.3        | IPO announced, uplisting  |
| "merger", "acquire" | +0.3        | M&A, acquisition, fusion  |
| "earnings"          | +0.2        | quarterly report, revenue |
| "offering"          | -0.2        | dilution, shelf offering  |

Le score de catalyseur est **normalisé entre 0 et 1** (`score_news`).

---

## 💾 Table `news_score`

| Colonne      | Type     | Description                    |
| ------------ | -------- | ------------------------------ |
| `symbol`     | TEXT     | Ticker concerné                |
| `score_news` | REAL     | Score basé sur les news        |
| `text`       | TEXT     | Texte de la news (résumé)      |
| `gpt_label`  | TEXT     | Optionnel : validation par GPT |
| `timestamp`  | DATETIME | Date d’analyse                 |

---

## 🔁 Cycle de traitement

1. Lecture des tickers de la `watchlist`
2. Appel API Finnhub pour chaque ticker
3. Parsing des titres et résumés des news
4. Calcul d’un `score_news` entre 0 et 1
5. Enregistrement dans `news_score`
6. Utilisation dans le module `ai_scorer`

---

## 🧪 Exemple de score appliqué dans le scorer IA

```python
if score_news > 0.7:
    score += 20  # Signal fort IA
elif score_news > 0.4:
    score += 10
```

---

## 📌 User Stories associées

- **US-NEWS-001** – En tant que moteur IA, je veux détecter automatiquement les catalyseurs pour ajuster le score d’un ticker.
- **US-NEWS-002** – En tant qu’utilisateur, je veux voir les raisons d’un score élevé basées sur les news.
- **US-NEWS-003** – En tant qu’analyste, je veux savoir si une dilution potentielle est présente.
- **US-NEWS-004** – En tant que développeur, je veux pouvoir configurer la période et les mots-clés utilisés.

---

> ✅ Ce module permet d’anticiper les mouvements liés à l’actualité en enrichissant le score IA de manière transparente et dynamique.

---


# 09_ai_scorer_analysis

# 📘 Chapitre 09 – Analyse IA & Scoring Avancé

Ce chapitre documente en profondeur le module `ai_scorer.py`, chargé de générer un **score global** pour chaque ticker analysé, basé sur des indicateurs techniques, fondamentaux et contextuels. Ce score guide ensuite les décisions de trading.

---

## 🎯 Objectif du module `ai_scorer.py`

- Fusionner plusieurs signaux en un **score global pondéré** (0 à 100).
- Identifier en priorité les tickers à fort potentiel.
- Offrir une base pour les modules de simulation, exécution et apprentissage IA.

---

## ⚙️ Fonctions principales

### `get_rsi(ticker)`

- **But** : détecter les zones de surachat/survente.
- Valeurs typiques : RSI > 70 = risque de retournement (ou continuation si catalyseur).

### `get_ema(ticker, periods=[9, 21])`

- **But** : détecter le croisement de moyennes mobiles.
- Logique : EMA9 > EMA21 = tendance haussière court terme.

### `get_vwap(ticker)`

- **But** : évaluer si le prix actuel est soutenu par le volume.
- Choix : prix > VWAP = confirmation d’un mouvement solide.

### `get_macd(ticker)`

- **But** : détecter des signaux de momentum.
- Signal positif si MACD > 0 et MACD > signal.

### `get_volume(ticker, interval='1m')`

- **But** : confirmer la liquidité et l’intérêt du marché.
- Seuil typique : > 500 000 en 1 min.

### `get_float(ticker)`

- **But** : identifier les low float stocks (< 100M) → forte réactivité au volume.

### `get_catalyseur_score(ticker)`

- **But** : mesurer l'impact des news (FDA, IPO, fusion...).
- Seuil de détection fort : > 0.7

### `get_atr(ticker)`

- **But** : mesurer la volatilité du ticker pour définir des SL/TP dynamiques.

---

## 🧠 Fonction centrale : `_compute_score()`

```python
def _compute_score(ticker):
    rsi = get_rsi(ticker)
    ema = get_ema(ticker, [9, 21])
    vwap = get_vwap(ticker)
    macd, signal = get_macd(ticker)
    volume = get_volume(ticker)
    float_val = get_float(ticker)
    catalyst = get_catalyseur_score(ticker)
    atr = get_atr(ticker)

    score = 0
    if ema[9] > ema[21]: score += 20
    if macd > signal: score += 15
    if rsi > 70: score += 5  # momentum positif
    if volume > 500_000: score += 20
    if float_val < 100_000_000: score += 10
    if catalyst > 0.7: score += 20
    if atr > 0.5: score += 10

    return {
        'symbol': ticker,
        'score': min(score, 100),
        'atr': atr,
        'source': 'WS'
    }
```

> 📌 Tous les scores sont arrondis à 100 max, sauf cas de désactivation IA.

---

## 🧾 Résultat enregistré

| Table `scores` | Description                  |
| -------------- | ---------------------------- |
| `symbol`       | Nom du ticker                |
| `score`        | Score calculé global (0-100) |
| `atr`          | Valeur d'ATR utilisée        |
| `source`       | Source d'analyse (ex: WS)    |
| `timestamp`    | Datetime d’analyse           |

---

## ⚖️ Justification des pondérations

- **EMA** : clé de tendance rapide → 20% poids
- **Volume** : nécessaire pour scalping → 20%
- **Catalyseur** : facteur exogène fort → 20%
- **MACD** : signal de tendance → 15%
- **Float** : sensible aux pumps → 10%
- **ATR** : important pour gestion du risque → 10%
- **RSI** : ajustement secondaire → 5%

Ces poids sont ajustables via `meta_ia.json` ou `config/rules_auto.json`.

---

## 🧬 Interaction avec les autres modules

| Module consommateur                   | Utilité                                           |
| ------------------------------------- | ------------------------------------------------- |
| `execution/strategie_scalping.py`     | Exécute la stratégie sur tickers avec score élevé |
| `simulation/simulate_trade_result.py` | Base de calcul de PnL attendu                     |
| `learning_loop.py`                    | Feedback IA sur la qualité du score               |
| `ui/app_unifie_watchlistbot.py`       | Affichage du score par ticker                     |

---

## 📌 User Stories associées

- **US-SCORE-001** – En tant que moteur IA, je dois produire un score global fiable pour chaque ticker.
- **US-SCORE-002** – En tant que développeur, je souhaite pouvoir comprendre et tester les poids appliqués à chaque signal.
- **US-SCORE-003** – En tant que trader, je veux voir des tickers avec des scores classés pour choisir rapidement les meilleurs.
- **US-SCORE-004** – En tant qu’administrateur, je veux savoir quand un score a été calculé et avec quelles valeurs.

---

> ✅ Ce chapitre est fondamental pour ajuster les performances du bot et interpréter les choix de trading IA.

---


# 12_ai_backtest_engine

# 📘 Chapitre 12 – Moteur de Backtest IA (Backtest Engine)

Ce module permet de rejouer les stratégies IA sur des données historiques pour évaluer leur performance dans le passé. C’est un outil de validation hors-ligne essentiel pour affiner les pondérations, tester les filtres et évaluer la robustesse des signaux IA.

---

## 🎯 Objectifs fonctionnels
- Reproduire le comportement du moteur IA sur une période historique.
- Tester les combinaisons d’indicateurs avec différentes pondérations.
- Générer des métriques globales (PnL, taux de réussite, Sharpe).
- Exporter les résultats pour analyse comparative.

---

## 🧪 Fonction principale : `run_backtest()`

| Fichier                          | Rôle principal                            |
|----------------------------------|--------------------------------------------|
| `backtest/ai_backtest_runner.py` | Lance le backtest sur tous les tickers     |
| `intelligence/ai_scorer.py`      | Utilisé pour recalculer les scores IA      |
| `simulation/simulate_trade_result.py` | Simule les trades sur données historiques |
| `utils/qlib_loader.py`           | Charge les données formatées pour IA       |

---

## 📁 Données utilisées
- Chemin : `qlib_data/daily/{symbol}.csv`
- Format attendu : OHLCV (Open, High, Low, Close, Volume)
- Sources compatibles : Yahoo Finance, Finnhub, données locales

---

## 🧠 Paramètres de simulation
| Paramètre             | Description                           | Valeur par défaut |
|-----------------------|---------------------------------------|-------------------|
| `threshold_score_min` | Score IA minimum pour entrer         | 70                |
| `sl_ratio`            | Stop Loss en %                       | 5%                |
| `tp_ratio`            | Take Profit en %                     | 10%               |
| `atr_multiplier`      | Utilisation de l’ATR pour SL/TP dyn. | 1.5               |

Tous ces paramètres sont configurables dans `config/backtest_config.json`.

---

## 📊 Résultats produits
- Fichier : `backtest_results_{date}.csv`
- Colonnes : `symbol`, `score`, `entry`, `exit`, `gain`, `sl_triggered`, `tp_triggered`, `comment`
- Tableau de synthèse : taux de réussite, PnL total, profit factor, Sharpe ratio

---

## 🔁 Intégration avec apprentissage IA
- Les meilleurs trades identifiés sont transférés vers le `learning_loop.py`
- Permet d’ajuster les pondérations `meta_ia.json`
- Sert aussi à tester les pondérations proposées par le module `ai_perf_maximizer.py`

---

## 📌 User Stories associées
- **US-BACKTEST-001** – En tant qu’analyste, je veux valider que mes stratégies auraient fonctionné dans le passé.
- **US-BACKTEST-002** – En tant qu’IA, je veux analyser les meilleures combinaisons passées pour apprendre.
- **US-BACKTEST-003** – En tant que développeur, je veux lancer un backtest massif sur 2 ans de données.
- **US-BACKTEST-004** – En tant qu’utilisateur, je veux visualiser les résultats dans le tableau de bord IA.

---

> ✅ Ce module permet d’évaluer objectivement la qualité des signaux IA et d’affiner les paramètres de trading avant tout déploiement réel.

---


# 13_ai_learning_loop

# 📘 Chapitre 13 – Apprentissage IA (Learning Loop)

Le module d’apprentissage IA (« learning loop ») permet à WatchlistBot d’ajuster ses décisions à partir des résultats passés (trades simulés et réels), en renforçant les critères ayant conduit à des gains significatifs.

Ce système crée une **amélioration continue** basée sur les performances historiques.

---

## 🎯 Objectifs fonctionnels

- Récupérer les résultats de trades passés.
- Identifier les patterns, combinaisons d’indicateurs ou conditions gagnantes.
- Mettre à jour les pondérations dans `meta_ia.json`.
- Renforcer les scores IA et prioriser les tickers similaires.

---

## 🧠 Principe du cycle d’apprentissage

```mermaid
graph TD
    A[Résultats des trades (simulés + réels)] --> B[Analyse des patterns gagnants]
    B --> C[Mise à jour des poids IA]
    C --> D[Réécriture de meta_ia.json]
    D --> E[Utilisation dans le scoring IA futur]
```

---

## 📁 Modules impliqués

| Fichier                           | Rôle                                       |
| --------------------------------- | ------------------------------------------ |
| `intelligence/learning_loop.py`   | Boucle principale d’apprentissage          |
| `intelligence/meta_ia.py`         | Gestion et écriture des pondérations       |
| `simulation/execution_simulee.py` | Fournit les données issues des simulations |
| `db/trades.py`                    | Récupération des trades réels              |

---

## 📄 Fichier cible : `meta_ia.json`

Contient les pondérations par indicateur ou paramètre :

```json
{
  "ema_cross_weight": 20,
  "macd_weight": 15,
  "volume_weight": 20,
  "float_weight": 10,
  "news_score_weight": 20,
  "rsi_weight": 5,
  "atr_weight": 10
}
```

---

## 🔎 Données analysées (features)

| Source           | Champ                   | Utilisation dans IA |
| ---------------- | ----------------------- | ------------------- |
| `trades_simules` | `gain`, `entry`, `exit` | Évalue la stratégie |
| `scores`         | `score`, `details`      | Corrèle score/gain  |
| `watchlist`      | `source`, `symbol`      | Suit la provenance  |

---

## 🔁 Méthode de renforcement

- Les stratégies gagnantes (> +5%) sont priorisées.
- Les indicateurs présents dans ces stratégies voient leur poids augmenté.
- Les stratégies perdantes réduisent le poids de certains facteurs.
- Le fichier `meta_ia.json` est régénéré à chaque boucle (quotidienne).

Extrait de code :

```python
if gain > 5.0:
    meta_ia['volume_weight'] += 1
else:
    meta_ia['volume_weight'] -= 1
```

---

## 🛡️ Sécurité et contrôle

- Les pondérations sont plafonnées entre 0 et 30.
- Un backup quotidien est sauvegardé dans `meta_ia_backup/{date}.json`
- Le module ne s’exécute que si la base contient > 20 trades.

---

## 📌 User Stories associées

- **US-LEARN-001** – En tant que moteur IA, je veux apprendre des trades passés pour ajuster mes critères.
- **US-LEARN-002** – En tant qu’administrateur, je veux voir comment les poids sont mis à jour.
- **US-LEARN-003** – En tant qu’utilisateur, je veux que le système devienne plus intelligent avec le temps.
- **US-LEARN-004** – En tant que développeur, je veux pouvoir ajuster manuellement les pondérations si besoin.

---

> ✅ Ce module rend le système adaptatif, capable d’évoluer au fil du temps pour détecter les meilleures configurations gagnantes.

---


# 14_meta_ia_config

# 📘 Chapitre 14 – Configuration IA Dynamique (`meta_ia.json`)

Ce module permet de **piloter dynamiquement le comportement du moteur IA** à partir d’un fichier centralisé `meta_ia.json`, contenant les pondérations et paramètres qui influencent le score attribué aux tickers.

C’est un mécanisme de configuration intelligent, mis à jour automatiquement par le moteur d’apprentissage, ou modifiable manuellement par un administrateur IA.

---

## 🎯 Objectifs fonctionnels

- Centraliser tous les **poids utilisés dans le scoring IA**.
- Permettre une mise à jour dynamique après apprentissage.
- Assurer une **traçabilité et auditabilité** des versions.
- Offrir un **point de tuning manuel** pour les analystes avancés.

---

## 📁 Fichier : `meta_ia.json`

Structure typique :

```json
{
  "ema_cross_weight": 20,
  "macd_weight": 15,
  "volume_weight": 20,
  "float_weight": 10,
  "news_score_weight": 20,
  "rsi_weight": 5,
  "atr_weight": 10
}
```

> Chaque clé représente un **indicateur IA**, chaque valeur un **poids entre 0 et 30**.

---

## 🧠 Modules consommateurs

| Module                       | Utilisation                                          |
| ---------------------------- | ---------------------------------------------------- |
| `ai_scorer.py`               | Application des pondérations dans `_compute_score()` |
| `learning_loop.py`           | Met à jour les pondérations en fonction des trades   |
| `meta_ia.py`                 | Lecture/écriture avec validation JSON                |
| `dashboard_apprentissage.py` | Affichage graphique des pondérations actuelles       |

---

## 🔁 Cycle de mise à jour automatique

1. Exécution d’un batch d’analyse ou d’un apprentissage.
2. Calcul de performance sur trades passés.
3. Pondérations ajustées (+/-) selon stratégie gagnante.
4. Écriture dans `meta_ia.json`
5. Sauvegarde backup dans `meta_ia_backup/YYYY-MM-DD.json`

---

## 🔒 Contrôles de sécurité

- **Validation de structure JSON** (types, bornes)
- **Limites de pondération** : entre 0 et 30 par défaut
- **Backup automatique** journalier
- **Verrouillage manuel** possible via clé `"editable": false`

---

## ⚙️ Exemple de code d’application dans le scorer

```python
weights = charger_meta_ia()
score = 0
if ema_cross: score += weights['ema_cross_weight']
if macd > signal: score += weights['macd_weight']
```

---

## 📌 User Stories associées

- **US-METAIA-001** – En tant qu’IA, je veux utiliser des poids optimisés pour noter les tickers.
- **US-METAIA-002** – En tant qu’analyste IA, je veux ajuster manuellement les pondérations si nécessaire.
- **US-METAIA-003** – En tant qu’administrateur, je veux sauvegarder un historique des changements.
- **US-METAIA-004** – En tant qu’utilisateur, je veux visualiser et comprendre les paramètres IA utilisés.

---

> ✅ Ce système rend le moteur IA personnalisable, traçable et optimisable sans modifier le code source.

---


# 15_ai_performance_maximizer (1)

# 📘 Chapitre 15 – Optimiseur de Performance IA (AI Performance Maximizer)

Le module **AI Performance Maximizer** est conçu pour tester automatiquement **des combinaisons alternatives de pondérations IA**, évaluer leur impact sur les performances simulées, et proposer des configurations optimisées.

Il complète la boucle d’apprentissage par une **approche d’optimisation proactive**.

---

## 🎯 Objectifs fonctionnels

- Générer des variantes de `meta_ia.json` (modification des pondérations).
- Exécuter des backtests sur chaque configuration générée.
- Évaluer la performance cumulée (PnL, taux de réussite, drawdown).
- Identifier et proposer la meilleure combinaison pondérée.

---

## 📁 Modules impliqués

| Fichier                             | Rôle                                         |
| ----------------------------------- | -------------------------------------------- |
| `intelligence/ai_perf_maximizer.py` | Génération et test des configurations IA     |
| `backtest/ai_backtest_runner.py`    | Lance les tests de validation                |
| `meta_ia.py`                        | Gère les fichiers `meta_ia.json` alternatifs |

---

## 🔧 Méthodologie d’optimisation

1. Charger la configuration actuelle `meta_ia.json`.
2. Générer X variantes : pondérations modifiées légèrement.
3. Pour chaque configuration :
   - Appliquer dans `ai_scorer.py`
   - Lancer `run_backtest()`
   - Enregistrer résultats dans `perf_logs.csv`
4. Comparer les configurations selon :
   - **PnL total**
   - **Taux de réussite (%)**
   - **Ratio gain/perte**
   - **Sharpe ratio**
5. Afficher la meilleure configuration et sa performance.

---

## 🧪 Exemple de variation générée

```json
{
  "ema_cross_weight": 22,
  "macd_weight": 14,
  "volume_weight": 18,
  "float_weight": 12,
  "news_score_weight": 21,
  "rsi_weight": 5,
  "atr_weight": 8
}
```

---

## 📊 Résultats stockés dans `perf_logs.csv`

| config\_id | ema | macd | pnl\_total | winrate | sharpe | path                     |
| ---------- | --- | ---- | ---------- | ------- | ------ | ------------------------ |
| 001        | 22  | 14   | 12,400\$   | 63%     | 1.35   | meta\_ia\_test\_001.json |
| 002        | 18  | 20   | 10,800\$   | 59%     | 1.10   | meta\_ia\_test\_002.json |

---

## 🔁 Intégration avec UI et apprentissage

- Les meilleures pondérations peuvent être **proposées à l’utilisateur dans l’interface**.
- Une version validée peut remplacer `meta_ia.json` manuellement ou automatiquement.

---

## 📌 User Stories associées

- **US-MAXIA-001** – En tant qu’IA, je veux tester plusieurs configurations pour maximiser ma rentabilité.
- **US-MAXIA-002** – En tant qu’utilisateur, je veux être informé si une meilleure combinaison a été trouvée.
- **US-MAXIA-003** – En tant qu’analyste IA, je veux auditer les essais passés et comprendre les écarts.
- **US-MAXIA-004** – En tant que développeur, je veux relancer l’optimiseur de manière batch ou planifiée.

---

> ✅ Ce module permet à l’IA de découvrir de nouvelles combinaisons gagnantes et de renforcer sa rentabilité sans supervision constante.

---


# 16_execution_scalping_strategy

# 📘 Chapitre 16/17 – Exécution Réelle & Stratégie Scalping

Ce module regroupe la **logique d’entrée en position réelle ou simulée** en fonction du score, des indicateurs techniques et de la fenêtre de volatilité identifiée.

La stratégie de scalping vise à profiter rapidement des mouvements sur des titres volatils à float faible, souvent liés à des catalyseurs (FDA, news, IPO, etc.).

---

## 🎯 Objectifs de la stratégie

- Entrer uniquement sur les opportunités validées par l’IA et les indicateurs techniques.
- Choisir le bon moment via un **breakout** ou un **pullback**.
- Calculer dynamiquement les niveaux de **Stop Loss (SL)**, **Take Profit (TP)** et **Trailing Stop (TS)**.
- Exécuter l’ordre (ou le simuler), puis le journaliser automatiquement.

---

## 📁 Modules concernés

| Fichier                           | Rôle                            |
| --------------------------------- | ------------------------------- |
| `execution/strategie_scalping.py` | Logique principale d’exécution  |
| `utils/order_executor.py`         | Envoi de l’ordre (réel ou mock) |
| `db/trades.py`                    | Enregistrement des ordres       |
| `notifications/telegram_bot.py`   | Alerte en temps réel            |

---

## ⚙️ Fonction centrale : `executer_strategie_scalping(ticker)`

### Logique complète :

```python
def executer_strategie_scalping(ticker):
    score = _compute_score(ticker)
    if score['score'] < 70:
        return {'status': 'ignored'}

    price = get_last_price(ticker)
    atr = score['atr']

    if enter_breakout(ticker, price, atr):
        ordre = executer_ordre_reel(ticker, price, atr)
        enregistrer_trade_auto(ticker, ordre)
        envoyer_alerte_ia(ticker, ordre)
        return {'ordre': ordre}
    return {'status': 'no_entry'}
```

---

## 🧠 Conditions d’entrée

| Type d’entrée               | Conditions                                 |
| --------------------------- | ------------------------------------------ |
| `enter_breakout(t, p, atr)` | Nouvelle cassure du plus haut avec support |
| `enter_pullback(t, p, atr)` | Rebond sur support après forte hausse      |

Ces fonctions analysent la bougie actuelle via `yfinance.download(...)` et les données `intraday_smart`.

---

## 📏 Gestion du risque (TP/SL/TS)

| Élément            | Calcul typique          | Explication                |
| ------------------ | ----------------------- | -------------------------- |
| SL (Stop Loss)     | `price - atr`           | Base sur volatilité locale |
| TP (Take Profit)   | `price + atr * 2`       | Objectif standard 2:1      |
| TS (Trailing Stop) | Suivi du plus haut - X% | Verrouille les gains       |

Le **TrailingManager** peut être utilisé pour ajuster dynamiquement la sortie.

```python
TM = TrailingManager(entry_price=2.0, stop_loss=1.9)
for p in [2.05, 2.15, 2.10]:
    TM.update(p)
```

---

## 🔁 Journalisation des ordres

Appel de : `enregistrer_trade_auto(ticker, ordre)`

| Table `trades` | Colonnes principales |
| -------------- | -------------------- |
| `symbol`       | Ticker               |
| `price`        | Prix d’entrée        |
| `volume`       | Volume               |
| `type`         | Réel / Simulé        |
| `pnl`          | Gain ou perte        |
| `timestamp`    | Date                 |

---

## 🔔 Notifications en temps réel

- Via `envoyer_alerte_ia(ticker, ordre)`
- Format : `📈 Achat exécuté AAA à 2.12$ - TP: 2.40$ / SL: 1.95$`

---

## 📌 User Stories associées

- **US-EXEC-001** – En tant que bot, je veux exécuter un trade quand le score et les conditions sont réunis.
- **US-EXEC-002** – En tant qu’utilisateur, je veux voir le résultat d’un ordre directement dans l’interface.
- **US-EXEC-003** – En tant qu’IA, je veux enregistrer chaque trade avec ses paramètres pour apprendre.
- **US-EXEC-004** – En tant qu’analyste, je veux être notifié quand un trade a lieu automatiquement.

---

> ✅ Ce module permet une exécution encadrée et optimisée des ordres IA. Il repose sur une logique robuste avec journalisation et alerte automatique.

---


# 16_stop_loss_manager

# 📘 Chapitre 16 – Stop Loss Manager & Sécurité Automatique

Le module **Stop Loss Manager** assure une gestion sécurisée des ordres en activant automatiquement des **mécanismes de protection** comme :

- stop loss fixe,
- trailing stop dynamique basé sur ATR,
- passage au point mort après un certain gain (breakeven),
- sécurisation partielle des profits.

C’est une brique essentielle pour garantir une protection constante du capital en trading algorithmique.

---

## 🎯 Objectifs fonctionnels

- Protéger les ordres ouverts automatiquement.
- Appliquer des règles adaptatives selon la volatilité (ATR).
- Encadrer les pertes et sécuriser progressivement les gains.
- Être réutilisable pour les ordres réels et les simulations.

---

## 📁 Modules concernés

| Fichier                            | Rôle                                        |
| ---------------------------------- | ------------------------------------------- |
| `execution/stop_manager.py`        | Gestion des seuils dynamiques               |
| `execution/strategie_scalping.py`  | Intégration dans les stratégies de scalping |
| `simulation/simulateur_trading.py` | Application dans le moteur de simulation    |

---

## ⚙️ Logique interne – TrailingManager

```python
class TrailingManager:
    def __init__(self, entry_price, stop_loss):
        self.entry = entry_price
        self.sl = stop_loss

    def update(self, current_price):
        if current_price >= self.entry * 1.02:
            self.sl = max(self.sl, self.entry)  # breakeven
        if current_price >= self.entry * 1.05:
            self.sl = max(self.sl, self.entry * 1.03)  # sécurisation
        return self.sl
```

> Le `TrailingManager` adapte le stop loss selon la progression du prix.

---

## 📊 Paramètres IA utilisés

- **ATR (Average True Range)** : mesure la volatilité → adapte la distance du stop.
- **Breakout détecté** : permet d'appliquer un trailing plus agressif.
- **Momentum** : peut désactiver le stop si le flux est trop instable.

---

## 📌 Valeurs typiques recommandées

| Indicateur | Utilisation                      | Valeur par défaut |
| ---------- | -------------------------------- | ----------------- |
| ATR        | Distance initiale du stop        | 1.5 x ATR         |
| Breakeven  | Seuil de passage au point mort   | +2%               |
| Secured TP | Sécurisation partielle des gains | +5% → SL à +3%    |

---

## 🔐 Sécurité & Robustesse

- Trailing toujours déclenché après passage d’un gain seuil.
- Réévaluation en temps réel toutes les X secondes.
- Historique des mises à jour stocké en mémoire ou journalisé.
- Peut fonctionner sans UI, en tâche de fond.

---

## 📌 User Stories associées

- **US-STPLS-001** – En tant qu’IA, je veux ajuster dynamiquement mon stop loss selon la volatilité.
- **US-STPLS-002** – En tant qu’utilisateur, je veux visualiser les niveaux de protection en cours.
- **US-STPLS-003** – En tant que bot, je veux passer à breakeven après un gain > 2%.
- **US-STPLS-004** – En tant que développeur, je veux pouvoir réutiliser le `TrailingManager` dans tous les modules.

---

> ✅ Ce module renforce la sécurité des stratégies et réduit l’exposition aux retournements brutaux.

---


# 17_ui_streamlit_interface

# 📘 Chapitre 17 – Interface Utilisateur (Streamlit App)

L’interface utilisateur développée avec **Streamlit** permet une interaction directe, claire et interactive avec l’ensemble des fonctionnalités du bot WatchlistBot V7.03. Elle est pensée pour :

- les traders (prise de décision rapide),
- les analystes IA (analyse des scores et signaux),
- les développeurs (debug visuel, affichage des logs),
- les chefs de projet (vue roadmap et user stories).

---

## 🎯 Objectifs fonctionnels de l’UI

- Afficher les tickers détectés en temps réel.
- Permettre le lancement et l’arrêt des analyses.
- Visualiser les graphiques et indicateurs clés.
- Exécuter des ordres simulés ou réels.
- Gérer les watchlists (manuel, IA, Jaguar).
- Afficher les logs, KPIs, scores IA et historiques.
- Naviguer entre modules via un menu clair.

---

## 📁 Fichiers Streamlit

| Fichier                         | Rôle                                         |
| ------------------------------- | -------------------------------------------- |
| `ui/app_unifie_watchlistbot.py` | Application principale, menu global          |
| `ui/pages/heatmap_realtime.py`  | Affichage de la heatmap des scores IA        |
| `ui/pages/simulation.py`        | Lancement d’ordres simulés + suivi           |
| `ui/pages/roadmap_tracker.py`   | Suivi des user stories et progression projet |
| `ui/pages/watchlist_manager.py` | Gestion des watchlists                       |

---

## 🧭 Structure du Menu UI

```txt
📊 Analyse & Watchlist
  └─ Lancer analyse 🔎
  └─ Arrêter analyse ✋
  └─ Résultats IA (heatmap, tableaux)

📈 Simulation & Ordres
  └─ Passer un ordre simulé ✅
  └─ Suivre les résultats 📉

🧠 IA & Apprentissage
  └─ Meta IA (paramètres dynamiques)
  └─ Résultats apprentissage
  └─ Optimiseur IA

📋 Roadmap & Stories
  └─ Suivi des tâches
  └─ Affichage par EPIC / Sprint

⚙️ Configuration
  └─ Paramètres utilisateur, Penny Stocks, Alerts
```

---

## 🧩 Composants visuels principaux

- **Boutons interactifs** : démarrage, stop, exécution d’ordres
- **Graphiques dynamiques** : avec `plotly`, `matplotlib`, `yfinance`
- **Tableaux filtrables** : watchlist IA, résultats simulation, journal
- **Checkboxes & sliders** : filtres IA, penny stocks, seuils de volume
- **Panneaux dépliables** : détails d’un ticker, debug, logs, trade info

---

## 🔄 Rafraîchissement temps réel

- Utilisation de `st.experimental_rerun()` pour forcer les mises à jour.
- Les heatmaps et graphiques sont recalculés à intervalle régulier (15 min).
- Support d’un **mode auto** pour les scans, et d’un **mode manuel** pour les tests ou analyses ponctuelles.

---

## 👥 Rôles utilisateurs cibles

| Rôle           | Utilisation UI                              |
| -------------- | ------------------------------------------- |
| Trader         | Watchlist, ordres, signaux et exécution     |
| Analyste IA    | Analyse des résultats IA, tuning des poids  |
| Architecte     | Navigation dans les modules, debug, journal |
| Chef de projet | Suivi roadmap, tests, EPICs et user stories |

---

## 📌 User Stories associées

- **US-UI-001** – En tant qu’utilisateur, je veux pouvoir lancer l’analyse en un clic.
- **US-UI-002** – En tant qu’analyste, je veux voir les résultats IA par score dans une heatmap.
- **US-UI-003** – En tant que trader, je veux exécuter un ordre simulé en 1 clic.
- **US-UI-004** – En tant qu’utilisateur, je veux basculer entre les watchlists (IA, manuel, Jaguar).
- **US-UI-005** – En tant que chef de projet, je veux suivre l’avancement du backlog en UI.
- **US-UI-006** – En tant que dev, je veux voir les logs et le debug dans des sections claires.

---

> ✅ Cette interface rend le bot utilisable, débogable, présentable et pilotable, même sans expertise Python.

---


# 18_journalisation_trades_db

# 📘 Chapitre 18 – Journalisation des ordres (`trades.db`)

La base de données `trades.db` est au cœur du suivi historique, de la simulation, et de l’apprentissage IA. Chaque ordre exécuté (réel ou simulé) y est enregistré avec précision, permettant :

- la traçabilité complète,
- la rétro-analyse des stratégies,
- l'entraînement du module IA,
- le calcul des statistiques journalières,
- la détection automatique des anomalies ou des modèles gagnants.

---

## 🗂️ Structure de la base `trades.db`

### 📌 Table `simulated_trades`

| Colonne           | Type    | Description                                                |
| ----------------- | ------- | ---------------------------------------------------------- |
| `id`              | INTEGER | Identifiant unique de la ligne (clé primaire)              |
| `symbol`          | TEXT    | Ticker de l’action                                         |
| `entry_price`     | REAL    | Prix d’achat                                               |
| `exit_price`      | REAL    | Prix de vente (si clôturé)                                 |
| `quantity`        | INTEGER | Nombre d’actions tradées                                   |
| `fees`            | REAL    | Frais estimés ou calculés (Moomoo Canada, par défaut)      |
| `gain_pct`        | REAL    | Gain/perte en pourcentage                                  |
| `timestamp_entry` | TEXT    | Horodatage de l’achat                                      |
| `timestamp_exit`  | TEXT    | Horodatage de la vente (si applicable)                     |
| `strategy`        | TEXT    | Stratégie utilisée (e.g. `breakout`, `pullback`, `manual`) |
| `score`           | INTEGER | Score IA au moment de l’achat                              |
| `source`          | TEXT    | Source du signal (IA, manuel, news, Jaguar...)             |
| `stop_loss`       | REAL    | Valeur du SL à l’achat                                     |
| `take_profit`     | REAL    | Valeur du TP initial                                       |
| `atr`             | REAL    | Valeur de l’ATR lors de l’entrée                           |
| `status`          | TEXT    | État (`open`, `closed`, `cancelled`, `error`)              |
| `comment`         | TEXT    | Notes ou raison spécifique liée à l’ordre                  |

---

## ⚙️ Fichier Python responsable : `journal.py`

```python
import sqlite3

def enregistrer_trade_auto(trade_data):
    conn = sqlite3.connect("trades.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO simulated_trades (
            symbol, entry_price, quantity, fees, timestamp_entry,
            strategy, score, source, stop_loss, take_profit, atr, status, comment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade_data["symbol"], trade_data["entry_price"], trade_data["quantity"],
        trade_data["fees"], trade_data["timestamp_entry"], trade_data["strategy"],
        trade_data["score"], trade_data["source"], trade_data["stop_loss"],
        trade_data["take_profit"], trade_data["atr"], "open", trade_data.get("comment", "")
    ))
    conn.commit()
    conn.close()
```

---

## ✅ Pourquoi ce design ?

- **Simplicité SQLite** : légère, sans serveur externe, idéale pour local/dev.
- **Historique structuré** : tous les ordres sont consultables.
- **Compatible apprentissage IA** : le module `learn_from_trades.py` s’appuie sur ces données.
- **Filtrable pour le dashboard** : affichage des PnL, performance journalière, etc.

---

## 📌 User Stories associées

- **US-JOURNAL-001** – En tant qu’utilisateur, je veux que chaque ordre soit automatiquement enregistré.
- **US-JOURNAL-002** – En tant qu’analyste, je veux pouvoir visualiser l’historique des trades.
- **US-JOURNAL-003** – En tant qu’IA, je veux pouvoir utiliser ces données pour améliorer les prédictions.
- **US-JOURNAL-004** – En tant que chef de projet, je veux que les erreurs ou statuts soient traçables.

---

## 🔍 À noter pour la maintenance

- Toujours vérifier que la table existe avant d’écrire.
- Prévoir une routine d’archivage pour éviter les surcharges.
- Ajouter un test automatique pour valider l’intégrité des lignes.

> Cette journalisation est un **pilier de l’auditabilité** et du **renforcement IA**. Elle permet d’analyser le comportement réel vs théorique du bot.

---


# 19_moteur_ia_learn_trades

# 📘 Chapitre 19 – Moteur IA d’apprentissage à partir des trades (`learn_from_trades.py`)

Le fichier `learn_from_trades.py` est un module central du **mécanisme adaptatif** du bot. Il analyse tous les trades enregistrés dans `trades.db` pour en tirer des **enseignements**, ajuster le **poids des indicateurs**, et recalibrer automatiquement la stratégie IA en fonction des résultats passés.

---

## 🎯 Objectifs du moteur d'apprentissage

- Identifier les patterns gagnants/perdants.
- Comparer les gains estimés vs. réels (écarts d’exécution).
- Réajuster les formules de score IA.
- Sélectionner les meilleurs paramètres d’entrée (entry price, SL, TP).
- Générer un fichier `meta_ia.json` mis à jour automatiquement.

---

## ⚙️ Fichier Python : `learn_from_trades.py`

```python
import sqlite3
import json
import numpy as np

PARAMS_FILE = "intelligence/meta_ia.json"

# Valeurs initiales par défaut si aucun apprentissage n’a encore été fait
def default_params():
    return {
        "rsi_weight": 1.0,
        "ema_weight": 1.0,
        "vwap_weight": 1.0,
        "volume_weight": 1.0,
        "catalyst_weight": 1.0,
        "min_gain_threshold": 3.0  # % minimal pour trade considéré comme gagnant
    }

def learn_from_trades():
    conn = sqlite3.connect("trades.db")
    df = pd.read_sql("SELECT * FROM simulated_trades WHERE status = 'closed'", conn)
    conn.close()

    if df.empty:
        return default_params()

    successful = df[df['gain_pct'] >= 3.0]
    failed = df[df['gain_pct'] < 0.0]

    # Exemple de pondération simple
    win_rate = len(successful) / len(df)
    updated_params = default_params()

    updated_params["rsi_weight"] = np.clip(win_rate * 2.5, 0.5, 3.0)
    updated_params["volume_weight"] = np.clip((len(successful)/max(1, len(failed))) * 1.2, 0.5, 3.0)
    updated_params["min_gain_threshold"] = max(2.0, df['gain_pct'].mean())

    with open(PARAMS_FILE, "w") as f:
        json.dump(updated_params, f, indent=4)

    return updated_params
```

---

## 🔁 Fichier généré : `meta_ia.json`

```json
{
    "rsi_weight": 2.4,
    "ema_weight": 1.0,
    "vwap_weight": 1.0,
    "volume_weight": 1.8,
    "catalyst_weight": 1.0,
    "min_gain_threshold": 3.5
}
```

Ce fichier est lu automatiquement par le module de scoring IA. Il permet au système de s’améliorer **en continu**.

---

## 📌 User Stories associées

- **US-LEARN-001** – En tant qu’IA, je veux ajuster les poids d’indicateurs en fonction des performances passées.
- **US-LEARN-002** – En tant qu’utilisateur, je veux que les poids soient sauvegardés dans un fichier exploitable.
- **US-LEARN-003** – En tant que bot, je veux utiliser ce fichier pour influencer le score au prochain trade.
- **US-LEARN-004** – En tant qu’architecte IA, je veux auditer les impacts des changements de paramètres.

---

## 📊 Variables apprises & logiques

| Variable             | Rôle                                                 | Appris depuis             |
| -------------------- | ---------------------------------------------------- | ------------------------- |
| `rsi_weight`         | Pondère l’importance du RSI dans le score            | Ratio succès trades RSI   |
| `volume_weight`      | Pondère l’impact du volume (ex: > 1M = bon signal)   | Ratio volume dans trades  |
| `min_gain_threshold` | Seuil minimal de gain attendu pour considérer succès | Moyenne des meilleurs PnL |

---

## 🔐 Sécurité & robustesse

- Vérification de l’existence de `trades.db` et `meta_ia.json`.
- Protection contre les divisions par zéro.
- Utilisation de `clip` pour encadrer les poids (anti-régression).

> Ce module rend le bot **vivant**, capable d’apprendre de ses erreurs comme de ses réussites. Chaque jour, il devient plus efficace.

---


# 20_watchlists_enrichies

# 📘 Chapitre 20 – Watchlists enrichies : Manuel, IA et Jaguar

Le système WatchlistBot génère une **liste intelligente de tickers à surveiller** à partir de **trois sources principales** :

- **Liste manuelle** (`tickers_manuels.json`),
- **Liste IA** (`meta_ia.json`, résultats de scoring),
- **Scraping Jaguar** (données temps réel de sentiment et de volume).

L’objectif est de produire une **watchlist unifiée**, triée par score et enrichie d’indicateurs clés, pour optimiser la prise de décision du trader ou du bot.

---

## 🧩 Fichiers et formats

### `tickers_manuels.json`

Ajout manuel des tickers par l’utilisateur via l’interface Streamlit.

```json
{
  "tickers": [
    { "symbol": "GNS", "provenance": "manuel", "ajout": "2024-06-20" },
    { "symbol": "APDN", "provenance": "manuel", "ajout": "2024-06-20" }
  ]
}
```

### `meta_ia.json`

Liste générée automatiquement par le moteur IA après analyse des patterns historiques + scorings des indicateurs.

```json
[
  { "symbol": "TTOO", "score": 94, "provenance": "IA", "catalyseur": true },
  { "symbol": "TOPS", "score": 91, "provenance": "IA", "catalyseur": false }
]
```

### Fichier `tickers_jaguar.json` (scraping)

Contient les tickers détectés via le scraping Jaguar (sentiment, volume anormal, activité forum).

```json
[
  { "symbol": "AVTX", "score": 88, "provenance": "jaguar", "volume": 1500000 },
  { "symbol": "FNHC", "score": 86, "provenance": "jaguar" }
]
```

---

## 🧠 Logique de fusion et filtrage : `watchlist_manager.py`

1. Charger les trois fichiers.
2. Fusionner en une seule liste (en supprimant les doublons).
3. Appliquer les règles de filtrage :
   - Exclure les penny stocks < \$1 (optionnel selon UI).
   - Score minimal (ex: 60).
   - Exclure tickers invalides ou sans données récentes.
4. Trier la liste finale par `score` décroissant.

```python
def generer_watchlist_unifiee():
    tickers = charger_tous_les_tickers()
    tickers = [t for t in tickers if t['score'] >= 60]
    tickers = filtrer_tickers_invalides(tickers)
    tickers_uniques = fusionner_et_supprimer_doublons(tickers)
    return sorted(tickers_uniques, key=lambda x: x['score'], reverse=True)
```

---

## 🔎 Détail des champs standardisés par ticker

| Champ        | Description                                |
| ------------ | ------------------------------------------ |
| `symbol`     | Ticker du titre                            |
| `score`      | Score calculé par IA ou scraping           |
| `provenance` | Source (manuel, IA, jaguar, news, scanner) |
| `catalyseur` | Si vrai, événement comme FDA, IPO, etc.    |
| `ajout`      | Date d’ajout à la watchlist                |
| `volume`     | Volume échangé (si disponible)             |

---

## 📌 User Stories associées

- **US-WATCHLIST-001** – En tant qu’utilisateur, je veux ajouter un ticker manuellement à la watchlist.
- **US-WATCHLIST-002** – En tant que bot, je veux fusionner les tickers IA, Jaguar et manuels dans une liste unique.
- **US-WATCHLIST-003** – En tant qu’IA, je veux filtrer les tickers invalides ou trop faibles.
- **US-WATCHLIST-004** – En tant qu’interface UI, je veux afficher la provenance, le score et le graphique de chaque ticker.
- **US-WATCHLIST-005** – En tant qu’utilisateur, je veux voir les tickers triés par pertinence (score).

---

## 📂 Modules Python concernés

- `utils_watchlist.py` → chargement/fusion
- `check_tickers.py` → validation ticker avec Finnhub
- `dashboard.py` → affichage final des tickers
- `tickers_manuels.json` → stockage côté utilisateur
- `meta_ia.json` → résultats IA
- `tickers_jaguar.json` → scraping dynamique

---

## 🧪 Cas de test clés

| Cas de test                           | Attendu                                       |
| ------------------------------------- | --------------------------------------------- |
| Ajout manuel d’un ticker              | Sauvegardé et visible dans la liste           |
| Ticker présent dans plusieurs sources | Fusionné, provenance prioritaire selon règles |
| Score < 60                            | Exclu sauf en mode debug                      |
| Ticker sans données récentes          | Exclu                                         |

---

## 📊 Table `tickers_enrichis` (base de données optionnelle future)

| Colonne        | Type    | Description                 |
| -------------- | ------- | --------------------------- |
| `symbol`       | TEXT    | Code du ticker              |
| `score`        | INTEGER | Score calculé               |
| `source`       | TEXT    | manuel / jaguar / IA / news |
| `added_on`     | TEXT    | Date d’intégration          |
| `has_catalyst` | BOOLEAN | Présence d’un catalyseur    |
| `volume`       | INTEGER | Volume au moment du scan    |

---

> Cette logique garantit que chaque matin, le bot dispose d’une watchlist **triée, pertinente et actualisée automatiquement**, combinant la connaissance humaine, l’IA et le sentiment de marché.

---


# 21_pre_market_post_market_scanner

# 📘 Chapitre 21 – Scanner Pré-Market & Post-Market Automatique

Ce module permet de **scanner automatiquement les marchés** en dehors des heures d'ouverture (entre 16h00 et 9h30) afin de détecter les tickers potentiellement explosifs pour le lendemain.

Il est **essentiel pour les penny stocks biotech/pharma** avec news ou catalyseurs récents.

---

## 🕐 Période de scan

- **Post-Market** : 16h00 à 00h00
- **Pre-Market** : 05h00 à 09h30

Le bot exécute un **scan automatique toutes les 15 minutes** pendant ces plages horaires.

---

## 🧪 Critères de détection

Un ticker est retenu s’il répond à **tous** les critères suivants :

| Critère                  | Valeur minimale           | Source           |
| ------------------------ | ------------------------- | ---------------- |
| Pourcentage de hausse    | > +50 %                   | Finnhub          |
| Volume                   | > 500 000 actions         | Finnhub / Jaguar |
| Float                    | < 200 millions d’actions  | Finnhub          |
| Anomalie carnet d’ordres | Oui (via scraping)        | Jaguar / forums  |
| Catalyseur actif         | IPO, FDA, SPAC, Fusion... | News Finnhub     |

---

## 📂 Fichiers et scripts

- `postmarket_scanner.py` → exécute les scans horaires
- `utils_finnhub.py` → récupère les données float, prix, news
- `scraper_jaguar.py` → détecte l’activité anormale
- `tickers_scanned.json` → stockage temporaire des tickers

---

## 🔁 Fonctionnement général

```python
def scanner_postmarket():
    tickers = detecter_tickers_volatils()
    for t in tickers:
        if valider_criteres(t):
            ajouter_watchlist_auto(t)
            alerter_user(t)
```

Chaque ticker retenu est :

- ajouté à la **watchlist IA avec provenance = "PostMarketScanner"**,
- accompagné d’une **alerte Telegram + alarme sonore**,
- visible dans le tableau de bord du lendemain matin.

---

## 📌 User Stories associées

- **US-SCAN-001** – En tant que bot, je veux détecter les tickers actifs en dehors des horaires pour les surveiller à l'ouverture.
- **US-SCAN-002** – En tant qu’utilisateur, je veux recevoir une alerte dès qu’un ticker postmarket est identifié.
- **US-SCAN-003** – En tant que bot, je veux filtrer uniquement les tickers avec catalyseur et conditions réunies.

---

## 🔐 Sécurité & validation

Avant chaque ajout, le bot vérifie :

- Que les données du ticker sont valides (`valider_ticker_finnhub`)
- Qu’il n’a pas déjà été ajouté dans la watchlist IA
- Que l’activité est récente (moins de 24h)

---

## 📊 Table future `postmarket_tickers`

| Colonne       | Type    | Description                |
| ------------- | ------- | -------------------------- |
| `symbol`      | TEXT    | Code du ticker             |
| `detected_on` | TEXT    | Timestamp UTC de détection |
| `score`       | INTEGER | Score IA calculé           |
| `catalyseur`  | TEXT    | FDA, IPO, SPAC, etc.       |
| `float`       | INTEGER | Nombre d’actions en float  |
| `volume`      | INTEGER | Volume détecté             |

---

## ✅ Impact sur le bot WatchlistBot

- Génère automatiquement des **opportunités analysables dès l’ouverture**
- Prend une **longueur d’avance sur les scanners classiques**
- Permet d’**entraîner l’IA en continu** avec ces détections

> Ce module est une **brique clé de la version IA pro-active** du bot, assurant une détection précoce à haut potentiel.

---


# 22_pump_detector_et_trailing_stop

# 📘 Chapitre 22 – Détecteur de Pump et Trailing Stop Automatique

Ce module permet d’identifier en temps réel les **phases de pump suspectes** ou les **explosions de volume**, puis de **sécuriser automatiquement les gains via un trailing stop dynamique**.

C’est un élément clé du scalping intelligent pour penny stocks à forte volatilité.

---

## 🚀 Détection de Pump : logique IA

Le pump est détecté par l’agrégation des indicateurs suivants :

| Indicateur             | Seuil / déclencheur                | Source         |
| ---------------------- | ---------------------------------- | -------------- |
| Variation sur 1min     | > +5%                              | Finnhub        |
| Volume 1min            | > 200% moyenne mobile 5min         | Finnhub        |
| Bougie haussière forte | Close > Open + 2x ATR              | Interne        |
| RSI                    | > 75 (confirmé par hausse brutale) | Interne        |
| MACD                   | Croisement + momentum positif      | Interne        |
| Détection IA           | Score IA > 85                      | `meta_ia.json` |

Ces règles sont combinées avec une **pondération IA dynamique**.

```python
if variation_pct > 5 and volume_surge and rsi > 75 and score_ia > 85:
    detect_pump(ticker)
```

---

## 🧠 Réactions possibles

Lorsqu’un pump est détecté :

- une **alerte est envoyée** (Telegram + Streamlit + alarme),
- l’ordre d’achat peut être simulé ou exécuté si activé,
- un **stop loss suiveur (trailing stop)** est déclenché immédiatement.

---

## 📉 Trailing Stop : Sécurisation intelligente

Le stop suiveur permet de **laisser courir les gains tout en bloquant les pertes**.

### Règles intégrées (module `trailing.py`)

| Seuil       | Action                                  |
| ----------- | --------------------------------------- |
| Gain > +2%  | SL déplacé au prix d’entrée (breakeven) |
| Gain > +5%  | SL remonté à +3%                        |
| Gain > +10% | SL à +7%, Take Profit partiel possible  |

L’ajustement est fait **en temps réel** sur chaque nouveau prix détecté.

```python
trailing = TrailingManager(entry_price=1.0, stop_loss=0.95)
sl = trailing.update(current_price)
```

---

## 📂 Modules Python concernés

- `execution/pump_detector.py` → détection temps réel
- `execution/trailing.py` → stop dynamique
- `utils_finnhub.py` → récupération volume / prix
- `journal.py` → enregistrement des trades exécutés

---

## 📌 User Stories associées

- **US-PUMP-001** – En tant qu’IA, je veux détecter les hausses anormales sur une minute pour alerter l’utilisateur.
- **US-PUMP-002** – En tant que bot, je veux initier un trailing stop dès l’achat sur pump.
- **US-PUMP-003** – En tant qu’utilisateur, je veux visualiser le niveau du SL en temps réel dans l’interface.
- **US-PUMP-004** – En tant que système, je veux sécuriser une partie des gains à +10% automatiquement.

---

## 🧪 Cas de test clés

| Cas de test                | Résultat attendu                        |
| -------------------------- | --------------------------------------- |
| Pump détecté > 5% + volume | Alerte déclenchée                       |
| Pump + score IA > 85       | Ordre d’achat simulé et trailing activé |
| Gain > +2%                 | SL = prix d’entrée                      |
| Gain > +5%                 | SL remonté                              |
| Gain > +10%                | TP partiel + SL haut                    |

---

## 🗄️ Table `trailing_trades` (optionnel en base)

| Colonne         | Type | Description                       |
| --------------- | ---- | --------------------------------- |
| `symbol`        | TEXT | Ticker du trade                   |
| `entry_price`   | REAL | Prix d’entrée                     |
| `initial_sl`    | REAL | SL de départ                      |
| `current_sl`    | REAL | SL mis à jour dynamiquement       |
| `current_price` | REAL | Prix de marché                    |
| `gain_pct`      | REAL | % de gain actuel                  |
| `status`        | TEXT | actif / sécurisé / vendu          |
| `updated_on`    | TEXT | Timestamp de dernière mise à jour |

---

> Ce module permet une **sécurisation intelligente des trades explosifs**, sans intervention manuelle, avec une compatibilité IA et des règles adaptatives. Il est indispensable dans un environnement de scalping ultra-rapide.

---


# 23_daily_closure

# 📘 Chapitre 23 – Clôture Journalière (Daily Closure)

Le module de **clôture de journée** est une étape essentielle pour garantir l’intégrité des données, archiver les résultats, déclencher les alertes récapitulatives, et préparer une nouvelle session propre.

Il intervient en toute fin de journée après les analyses, simulations et exécutions éventuelles.

---

## 🎯 Objectifs de la clôture

- Geler les données de la session (résultats, scores, watchlist).
- Calculer les statistiques globales (PnL, nombre de trades, efficacité IA).
- Nettoyer l’environnement (réinitialisation des listes temporaires).
- Archiver les fichiers exportables (Excel, JSON, logs).
- Envoyer une notification Telegram résumant la journée.

---

## 🧪 Fonction principale : `cloturer_journee()`

### Localisation :

- `ui/page_modules/cloture_journee.py`

### Déclencheur :

- Bouton dans l’interface Streamlit : `st.button("Clôturer la journée")`

### Logique principale (extrait simplifié) :

```python
def cloturer_journee():
    stats = calculer_stats_du_jour()
    exporter_resultats_journaliers(stats)
    envoyer_alerte_telegram(stats)
    reset_watchlist_temporaire()
    vider_scores()
    logger("Clôture terminée avec succès")
```

---

## 🗃️ Tables affectées

| Table            | Action effectuée                       |
| ---------------- | -------------------------------------- |
| `watchlist`      | Suppression ou archivage               |
| `scores`         | Réinitialisation                       |
| `trades`         | Lecture seule pour calcul des KPIs     |
| `trades_simules` | Lecture + possibilité d’archivage JSON |

---

## 📁 Exports générés

- `export_journalier_{date}.json` : résultat des trades
- `pnl_resume_{date}.xlsx` : synthèse des gains/pertes
- `log_cloture_{date}.txt` : journalisation complète

Fichiers placés dans le dossier `exports/`.

---

## 🔔 Notification finale

- Appel de `envoyer_alerte_telegram(stats)` (via `telegram_bot.py`)
- Message résumé :

```
📊 Clôture du {date}
- Total trades : X
- Gain net : $Y
- Score IA moyen : Z
```

---

## 🔐 Sécurité & conditions

- Bouton de clôture **désactivé automatiquement** après usage (1 fois / jour).
- Historique journalier conservé dans `exports/`.
- Option de relancer `cloturer_journee(force=True)` en cas de correction manuelle.

---

## 📌 User Stories associées

- **US-CLOSE-001** – En tant qu’utilisateur, je veux archiver mes résultats de trading à la fin de chaque journée.
- **US-CLOSE-002** – En tant que système, je veux remettre à zéro la watchlist et les scores pour la prochaine session.
- **US-CLOSE-003** – En tant que responsable IA, je veux récupérer les journaux pour affiner les modèles d’apprentissage.
- **US-CLOSE-004** – En tant qu’utilisateur, je veux recevoir un résumé des résultats sans avoir à chercher dans les fichiers.

---

> ✅ Ce module garantit une base saine pour les sessions suivantes, tout en assurant la traçabilité des performances quotidiennes.

---


# 24_simulation_et_backtest_ia

# 📘 Chapitre 24 – Simulation et Backtest IA

Ce module est au cœur de l'amélioration continue du bot. Il permet de simuler des trades passés à partir de données historiques et d’évaluer l’efficacité des stratégies IA dans divers contextes de marché.

---

## 🎯 Objectif

- Tester les stratégies IA sur plusieurs jours/mois/années de données historiques
- Évaluer les performances (gains, drawdown, fiabilité)
- Ajuster dynamiquement les paramètres IA pour les futures sessions live
- Renforcer l’IA avec apprentissage supervisé + renforcement

---

## 🔁 Fonction principale

```python
from simulation.simulateur import lancer_backtest

resultats = lancer_backtest(
    liste_tickers=['GNS', 'CAMP'],
    periode='1y',
    capital_initial=2000,
    strategie='scalping_ai_v2',
    mode='historique'
)
```

Résultat : dictionnaire structuré contenant le PnL, les taux de réussite, les logs, et les ajustements IA.

---

## ⚙️ Paramètres du moteur

| Paramètre         | Type  | Description                                          |
| ----------------- | ----- | ---------------------------------------------------- |
| `strategie`       | str   | Nom de la stratégie à tester                         |
| `periode`         | str   | Durée : `1y`, `6mo`, `3mo`, `30d`, etc.              |
| `capital_initial` | float | Capital de départ pour calcul du PnL                 |
| `tickers`         | list  | Liste de symboles à analyser                         |
| `frais_reels`     | bool  | Appliquer ou non les frais Moomoo Canada             |
| `slippage_pct`    | float | Valeur à simuler pour slippage                       |
| `mode`            | str   | `historique`, `intraday`, `reel`                     |
| `afficher_graphs` | bool  | Générer ou non les graphiques Streamlit / Matplotlib |

---

## 🔍 Détail des indicateurs simulés

Chaque trade simule :

- RSI, EMA(9,21), VWAP, MACD, Volume, Bollinger, ATR, ADX
- Timing (cassure, pullback, rebond), float, catalyseur IA
- Application des seuils IA validés (score IA > 85, volume > seuil, etc.)

```python
if score_ia > 85 and vwap_crossed and breakout_validated:
    acheter(ticker)
```

---

## 📂 Modules Python concernés

- `simulation/simulateur.py` → moteur de backtest principal
- `intelligence/learning_engine.py` → ajustement des poids IA
- `execution/strategie_scalping.py` → logique de scalping
- `utils/data_loader.py` → récupération des données historiques
- `journal.py` → enregistrement des résultats simulés

---

## 📊 Structure de la table `simulated_trades`

| Colonne      | Type | Description                       |
| ------------ | ---- | --------------------------------- |
| `symbol`     | TEXT | Ticker                            |
| `timestamp`  | TEXT | Heure de l’action simulée         |
| `prix_achat` | REAL | Prix d’entrée simulé              |
| `prix_vente` | REAL | Prix de sortie simulé             |
| `strategie`  | TEXT | Stratégie IA utilisée             |
| `gain`       | REAL | Gain brut                         |
| `gain_pct`   | REAL | % de gain                         |
| `resultat`   | TEXT | `WIN` ou `LOSS`                   |
| `duration`   | TEXT | Durée du trade                    |
| `notes`      | TEXT | Détails stratégiques / erreurs IA |

---

## 📌 User Stories associées

- **US-SIM-001** – En tant qu’utilisateur, je veux tester une stratégie IA sur 6 mois de données historiques.
- **US-SIM-002** – En tant que système, je veux enregistrer tous les trades simulés dans une table dédiée.
- **US-SIM-003** – En tant qu’IA, je veux ajuster mes poids après chaque backtest pour m’améliorer.
- **US-SIM-004** – En tant qu’utilisateur, je veux visualiser un rapport graphique après simulation.
- **US-SIM-005** – En tant qu’architecte, je veux exporter les résultats pour audit / migration.

---

## 🧪 Cas de test clés

| Cas de test                 | Résultat attendu                       |
| --------------------------- | -------------------------------------- |
| Simulation sur 30 jours     | Résultat PnL global                    |
| Trade IA avec gain > 5%     | Enregistrement dans `simulated_trades` |
| Trade IA avec perte         | Stocké avec note d’erreur              |
| Ajustement IA après test    | Nouveau poids IA sauvegardé            |
| Visualisation des résultats | Graphique Streamlit avec gain/jour     |

---

## 📤 Fichiers de sortie

- `results/simulation_{date}.json` – Résultats structurés complets
- `graphs/simulation_{date}.png` – Graphique de performance
- `simulated_trades.db` – Table complète des ordres simulés

---

> Ce module permet un **entraînement IA à grande échelle**, une **validation empirique des stratégies** et une **préparation fiable à l’exécution réelle** sur compte démo ou réel.

---


# 25_apprentissage_renforce_ia

# 📘 Chapitre 25 – Apprentissage Renforcé IA

Ce module applique une logique d’apprentissage par renforcement à partir des résultats de trading (réels ou simulés) pour ajuster automatiquement les décisions futures du bot IA.

Il repose sur une **formule de récompense** calibrée, la **pénalisation des erreurs critiques**, et une **mise à jour dynamique des poids stratégiques**.

---

## 🎯 Objectif du module

- Apprendre automatiquement des trades gagnants et perdants
- Renforcer les décisions menant à de bons résultats
- Éviter les patterns conduisant à des pertes
- Mettre à jour dynamiquement les règles IA (score, stop loss, timing)

---

## 🧠 Logique de renforcement IA

Chaque trade (réel ou simulé) est analysé à postériori selon ces règles :

```python
reward = gain_pct * facteur_confiance
penalty = erreur_strategique * facteur_erreur
score_ajuste = score_ia + reward - penalty
```

**Explications :**

- `gain_pct` : gain du trade en %
- `facteur_confiance` : pondération basée sur la solidité des signaux
- `erreur_strategique` : erreurs détectées (ex: entrée tardive, SL trop serré)
- `score_ia` : score de départ du trade

Un système de **logique floue** permet de moduler ces valeurs entre 0 et 1.

---

## 🧩 Modules Python concernés

- `intelligence/learning_engine.py` → moteur IA de mise à jour
- `simulation/simulateur.py` → fournit les résultats des trades simulés
- `execution/strategie_scalping.py` → fournit les signaux bruts
- `journal.py` → source de vérité pour les trades réels
- `utils/math_tools.py` → fonctions de pondération et normalisation

---

## 🧾 Format des données d’entrée (résultats de trade)

| Champ         | Type | Description                            |
| ------------- | ---- | -------------------------------------- |
| `symbol`      | TEXT | Ticker analysé                         |
| `score_ia`    | REAL | Score initial au moment de la décision |
| `gain_pct`    | REAL | Gain ou perte (en %)                   |
| `sl_touch`    | BOOL | Si le stop loss a été touché           |
| `tp_reached`  | BOOL | Si le take profit a été atteint        |
| `duree_trade` | TEXT | Durée entre achat et vente             |
| `volume`      | INT  | Volume échangé pendant le trade        |
| `indicateurs` | JSON | Valeurs des indicateurs clés utilisés  |
| `notes`       | TEXT | Observations du moteur IA              |

---

## ⚙️ Paramètres par défaut

| Paramètre              | Valeur défaut | Description                                    |
| ---------------------- | ------------- | ---------------------------------------------- |
| `facteur_confiance`    | 1.0           | Pondération des signaux                        |
| `facteur_erreur`       | 1.5           | Pénalité en cas de défaillance                 |
| `seuil_gain_minimal`   | 3.0           | % à partir duquel un trade est considéré utile |
| `score_min_retenu`     | 85            | Score minimal pour renforcement                |
| `max_trades_par_cycle` | 1000          | Pour éviter surcharge mémoire                  |

---

## 🧪 Cas de test clés

| Cas de test                              | Résultat attendu                     |
| ---------------------------------------- | ------------------------------------ |
| Trade gagnant avec TP atteint            | Augmentation du poids de stratégie   |
| Trade perdant avec SL déclenché          | Diminution du score de configuration |
| Trade neutre (0% gain)                   | Pas de mise à jour                   |
| Erreur IA détectée (entrée trop tardive) | Pénalité sur le critère de timing    |
| Plusieurs trades avec même pattern       | Ajustement groupé des paramètres     |

---

## 📌 User Stories associées

- **US-IA-REWARD-001** – En tant qu’IA, je veux renforcer les stratégies qui génèrent des gains > 5%.
- **US-IA-REWARD-002** – En tant qu’utilisateur, je veux voir l’évolution des poids IA dans l’interface.
- **US-IA-REWARD-003** – En tant que système, je veux éviter d’utiliser une stratégie si elle a échoué 3 fois.
- **US-IA-REWARD-004** – En tant qu’architecte, je veux exporter les pondérations IA pour debug / analyse.

---

## 📤 Fichiers de sortie

- `logs/learning/poids_ia_{date}.json` – Nouveau mapping des pondérations IA
- `learning_history.db` – Historique complet des ajustements stratégiques
- `rapport_apprentissage.csv` – Résumé lisible des mises à jour

---

## 📌 Impact système

✅ Ce module permet à l’IA d’apprendre de manière **autonome et continue**, avec un focus sur :

- La **fiabilité** des signaux IA (par renforcement positif)
- La **correction des erreurs fréquentes** (par pénalité)
- L’**adaptation automatique** au marché

> C’est l’un des piliers majeurs de la performance long terme du bot de trading.

---


# 26_watchlist_multi_source

# 📘 Chapitre 26 – Générateur de Watchlist Multi-Sources

Ce module centralise les tickers à analyser chaque jour, en fusionnant plusieurs sources (manuel, IA, scraping), avec un mécanisme de filtrage, priorisation, et enrichissement automatique.

---

## 🎯 Objectif du module

- Créer une watchlist quotidienne unifiée à partir de plusieurs sources
- Appliquer des règles de priorité, nettoyage, et enrichissement
- Éviter les doublons, les erreurs, et les faux signaux
- Proposer des tickers avec score, timing et provenance claire

---

## 📥 Sources de données principales

| Source          | Format | Fichier / Module utilisé  | Détails                                             |
| --------------- | ------ | ------------------------- | --------------------------------------------------- |
| Manuel          | JSON   | `tickers_manuels.json`    | Ajouts directs via interface ou fichier             |
| Scraping Jaguar | JSON   | `resultats_scraping.json` | Tickers détectés sur sites spécialisés              |
| IA interne      | JSON   | `meta_ia.json`            | Résultats du moteur IA sur les patterns historiques |

---

## ⚙️ Logique de fusion / enrichissement

```python
from intelligence.watchlist_engine import generer_watchlist

tickers_fusionnes = generer_watchlist(sources=['manuel', 'ia', 'scraping'])
```

### Étapes appliquées :

1. Chargement de chaque fichier source
2. Suppression des doublons (clé = `symbol`)
3. Fusion des métadonnées (score, float, volume, provenance)
4. Calcul du score final pondéré (score IA, catalyseur, anomalie volume)
5. Enrichissement avec données techniques :
   - VWAP, EMA9/21, RSI, news FDA, float < 200M, etc.
6. Tri décroissant par score

---

## 🧩 Modules Python concernés

- `intelligence/watchlist_engine.py` → module principal de fusion
- `utils_fusion.py` → fonctions de nettoyage / enrichissement
- `data/sources_loader.py` → charge chaque fichier source
- `ui/pages/gestion_watchlist.py` → interface de visualisation

---

## 🧾 Structure finale d’un ticker

| Champ            | Type | Description                                         |
| ---------------- | ---- | --------------------------------------------------- |
| `symbol`         | TEXT | Code du ticker (ex: GNS, HLTH)                      |
| `provenance`     | TEXT | Source d’origine : `manuel`, `IA`, `scraping`, etc. |
| `score_final`    | REAL | Score combiné (sur 100) calculé dynamiquement       |
| `float`          | INT  | Nombre d’actions en circulation                     |
| `variation_pct`  | REAL | % de gain journalier                                |
| `volume`         | INT  | Volume journalier observé                           |
| `news_detected`  | BOOL | True si catalyseur type FDA / Fusion détecté        |
| `graph_snapshot` | STR  | Lien vers image graphique (optionnel)               |

---

## 📌 User Stories associées

- **US-WL-001** – En tant qu’utilisateur, je veux que tous les tickers soient centralisés dans une seule liste triée.
- **US-WL-002** – En tant que système, je veux ignorer les doublons et les tickers invalides (prix ≤ 0).
- **US-WL-003** – En tant qu’IA, je veux que le score soit recalculé après enrichissement.
- **US-WL-004** – En tant qu’utilisateur, je veux voir la provenance de chaque ticker dans l’interface.
- **US-WL-005** – En tant qu’architecte, je veux que les règles de fusion soient traçables et auditées.

---

## 🧪 Cas de test clés

| Cas de test                       | Résultat attendu                                   |
| --------------------------------- | -------------------------------------------------- |
| Présence du même ticker 2x        | Un seul ticker fusionné avec métadonnées enrichies |
| Ticker avec float > 200M          | Exclu automatiquement (règle IA)                   |
| Ticker sans catalyseur            | Score réduit                                       |
| Chargement manuel + IA + scraping | Liste complète triée par score final               |

---

## ⚙️ Fichier de sortie

- `watchlist_du_jour.json` → Liste complète triée avec scores et provenances
- `watchlist_log.csv` → Historique des ajouts par source + horodatage
- `watchlist_debug_invalids.json` → Liste des tickers exclus avec raison

---

## 📌 Impact système

✅ Ce module garantit une **base de travail fiable chaque matin**, avec des tickers analysés, enrichis et triés automatiquement, permettant à l’IA de démarrer avec une liste cohérente et performante.

> Un module stratégique pour éviter les faux positifs et focaliser les ressources IA sur les meilleurs candidats journaliers.

---


# 27_analyse_graphique_signaux (1)

# 📘 Chapitre 27 – Analyse Graphique & Signaux Visuels

Ce module vise à détecter visuellement des signaux techniques clés sur les graphiques des tickers, notamment via les cassures de niveau, les chandeliers, les volumes anormaux, et les patterns de breakout. Il sert à alerter l'utilisateur via l'interface Streamlit avec une lecture claire, sans interférence sur la logique IA principale.

---

## 🎯 Objectif du module

- Visualiser les signaux techniques pertinents directement dans l’interface utilisateur
- Détecter automatiquement des patterns : cassure, pullback, volume, chandelier, etc.
- Générer des instantanés graphiques (snapshots) à afficher avec chaque ticker
- Ne pas interférer avec les décisions IA (module purement visuel)

---

## 🔍 Patterns détectés

| Pattern / Signal      | Condition de déclenchement                       | Exemple visuel                               |
| --------------------- | ------------------------------------------------ | -------------------------------------------- |
| Cassure de résistance | Dernier prix > plus haut des 2 dernières bougies | `df['Close'].iloc[-1] > df['High'].iloc[-2]` |
| Pullback validé       | Retour au niveau cassé + volume supérieur        | `Volume[-1] > moyenne(3)`                    |
| Marubozu haussier     | Bougie sans mèche basse, forte clôture au sommet | `Open ≈ Low` et `Close ≈ High`               |
| Engulfing haussier    | Bougie verte > bougie rouge précédente           | `BodyGreen > BodyRed`                        |
| Volume anormal        | Volume dernier tick > 1.5× moyenne précédente    | `vol[-1] > 1.5 * moyenne(vol[-10:])`         |

---

## 🧠 Logique technique (extrait de code)

```python
import pandas as pd
import matplotlib.pyplot as plt

def detect_breakout(df):
    return df['Close'].iloc[-1] > df['High'].iloc[-2]

def snapshot_graph(df, symbol):
    fig, ax = plt.subplots()
    df[['Open','High','Low','Close']].tail(20).plot(ax=ax, title=f"{symbol} - Derniers chandeliers")
    img_path = f"images_snapshots/{symbol}.png"
    fig.savefig(img_path)
    return img_path
```

---

## 🧩 Modules Python concernés

- `utils_graph.py` → gestion des graphiques, snapshots
- `intelligence/pattern_graphique.py` → détection des patterns
- `ui/pages/heatmap_realtime.py` → affichage interactif
- `data/historique_manager.py` → accès aux données de bougies

---

## 🧾 Structure d’un signal visuel (dans ticker enrichi)

| Champ             | Type   | Description                                   |
| ----------------- | ------ | --------------------------------------------- |
| `symbol`          | TEXT   | Code du ticker                                |
| `graph_snapshot`  | STRING | Chemin vers l’image snapshot (PNG)            |
| `pattern_detecte` | TEXT   | Pattern détecté (`breakout`, `pullback`, ...) |
| `volume_alert`    | BOOL   | True si volume anormal détecté                |

---

## 📌 User Stories associées

- **US-GRAPH-001** – En tant qu’utilisateur, je veux voir le graphique de chaque ticker avec des indications visuelles.
- **US-GRAPH-002** – En tant que bot, je veux générer un snapshot au moment du scan journalier.
- **US-GRAPH-003** – En tant que système, je veux détecter automatiquement les patterns sans interagir avec les décisions IA.
- **US-GRAPH-004** – En tant qu’utilisateur, je veux comprendre visuellement pourquoi un score élevé est attribué à un ticker.

---

## 🧪 Cas de test fonctionnels

| Cas de test                 | Résultat attendu                            |
| --------------------------- | ------------------------------------------- |
| Cassure détectée            | Image générée + tag `breakout` dans ticker  |
| Pullback après cassure      | Pattern = `pullback`                        |
| Volume > 1.5x moyenne       | Champ `volume_alert` = True                 |
| Affichage graphique dans UI | Image visible dans panneau ticker Streamlit |

---

## 📤 Dossiers de sortie

- `/images_snapshots/` → Contient les images graphiques par ticker
- `tickers_enrichis.json` → Contient les champs `pattern_detecte`, `graph_snapshot`

---

## 🔄 Mécanisme de rafraîchissement

- Snapshots générés **uniquement lors de l’ouverture manuelle du ticker** dans l’interface
- Aucun impact sur les performances IA (traitement uniquement visuel)

---

## 🎯 Impact global

✅ Améliore l’interprétation humaine et la prise de décision ✅ Permet aux traders de valider visuellement les signaux IA ✅ Sert de support à l’audit et à l’apprentissage visuel

Un module complémentaire essentiel pour renforcer la confiance dans le système de détection, tout en conservant la séparation claire entre IA et interface visuelle.

---


# 27_analyse_graphique_signaux (2)

# 📘 Chapitre 28 – Détection de Pump + Stop Loss Dynamique

Ce module permet de détecter les situations de pump (hausse anormale et soudaine d’un ticker) et d’appliquer une gestion dynamique du stop loss via un gestionnaire de trailing stop (suivi de prix). Il améliore la sécurité des positions et l’automatisation des prises de bénéfices.

---

## 🎯 Objectif du module

- Détecter automatiquement les situations de pump (hausse brutale + volume anormal)
- Appliquer un stop loss évolutif basé sur la performance en temps réel
- Automatiser la prise de bénéfices ou sortie préventive
- Intégrer un moteur intelligent de gestion du risque (TrailingManager)

---

## 🚀 Détection de Pump – Logique métier

| Critère             | Condition Python                                 | Justification                              |
| ------------------- | ------------------------------------------------ | ------------------------------------------ |
| Gain instantané     | `(price_now - price_5s_ago)/price_5s_ago > 0.03` | Hausse > 3% en quelques secondes           |
| Volume minute élevé | `volume_1m > 500000`                             | Preuve d’un engouement ou flux soudain     |
| Float bas           | `float < 100_000_000`                            | Sensibilité accrue des petits flottants    |
| Catalyseur détecté  | `score_catalyseur > 0.5`                         | Événement externe favorable (news, FDA...) |

---

## 🧠 Exemple de code : pump detector

```python
from execution.utils_indicateurs import get_last_price, get_price_5s_ago, get_volume, get_float, get_catalyseur_score

def is_pump_candidate(ticker):
    p_now = get_last_price(ticker)
    p_old = get_price_5s_ago(ticker)
    v1m = get_volume(ticker, '1m')
    fl = get_float(ticker)
    score = get_catalyseur_score(ticker)
    return (
        (p_now - p_old) / p_old > 0.03 and
        v1m > 500_000 and
        fl < 100_000_000 and
        score > 0.5
    )
```

---

## 🛡️ Stop Loss Dynamique – TrailingManager

Le module `TrailingManager` ajuste automatiquement le stop selon la performance :

| Condition d'évolution      | Nouvelle valeur de SL          | Description                 |
| -------------------------- | ------------------------------ | --------------------------- |
| Prix > +2% au-dessus achat | SL = prix d’achat (break-even) | Sécurisation immédiate      |
| Prix > +5%                 | SL = +3% au-dessus prix achat  | Protection du profit latent |
| Chute de prix              | Retour immédiat au SL          | Sortie automatique          |

### Implémentation

```python
class TrailingManager:
    def __init__(self, entry_price, stop_loss):
        self.entry_price = entry_price
        self.stop_loss = stop_loss

    def update(self, price):
        if price >= self.entry_price * 1.05:
            self.stop_loss = max(self.stop_loss, self.entry_price * 1.03)
        elif price >= self.entry_price * 1.02:
            self.stop_loss = max(self.stop_loss, self.entry_price)
        return self.stop_loss
```

---

## 🧩 Modules Python concernés

- `execution/pump_detector.py` → détection de pump
- `execution/strategie_scalping.py` → intègre le TrailingManager
- `execution/utils_indicateurs.py` → indicateurs nécessaires (prix, volume, float, catalyseur)

---

## 📊 Structure des résultats enrichis

| Champ              | Type  | Description                      |
| ------------------ | ----- | -------------------------------- |
| `symbol`           | TEXT  | Code du ticker                   |
| `pump_detected`    | BOOL  | True si pump détecté             |
| `entry_price`      | FLOAT | Prix d’entrée initial            |
| `stop_loss`        | FLOAT | Stop loss dynamique (mis à jour) |
| `gain_potentiel`   | FLOAT | Gain projeté à +5%               |
| `trailing_manager` | OBJ   | État interne du gestionnaire     |

---

## 📌 User Stories associées

- **US-PUMP-001** – En tant que bot, je veux détecter les situations de pump en temps réel.
- **US-PUMP-002** – En tant que bot, je veux appliquer un stop loss dynamique basé sur le comportement du prix.
- **US-PUMP-003** – En tant qu’utilisateur, je veux visualiser dans l’UI le SL actuel ajusté automatiquement.
- **US-PUMP-004** – En tant que système, je veux que la gestion de stop ne bloque pas l’interface (asynchrone).

---

## ✅ Cas de test

| Cas de test                            | Résultat attendu                         |
| -------------------------------------- | ---------------------------------------- |
| Pump détecté avec volume et catalyseur | `pump_detected = True`                   |
| Prix monte à +5%                       | SL mis à jour à `entry_price * 1.03`     |
| Prix chute en-dessous du SL            | Trade clôturé automatiquement            |
| Utilisateur visualise le SL en UI      | Valeur actualisée dans le panneau ticker |

---

## 🎯 Impact global

✅ Sécurise automatiquement les trades avec logique IA de sortie ✅ Prévient les pertes en cas de chute soudaine ✅ Favorise les gains dans les situations de pump ✅ Complément essentiel au moteur d’exécution intelligent

---


# 28_pump_detector_trailing_stop

# 📘 Chapitre 28 – Pump Detector & Trailing Stop

Ce module est dédié à la **surveillance en temps réel** des mouvements brutaux de prix (« pumps ») et à la gestion intelligente des sorties via un **Trailing Stop dynamique**.

Il s'agit d’un composant clé pour le **scalping sur penny stocks volatils** : il détecte les anomalies de prix et déclenche des simulations ou alertes avec sécurité automatisée.

---

## 🎯 Objectifs fonctionnels

- Détecter les hausses de prix brutales sur un court laps de temps.
- Confirmer la légitimité du mouvement par le volume.
- Exécuter (ou simuler) une entrée IA avec sortie via Trailing Stop.
- Notifier l’utilisateur en cas de signal confirmé (popup ou Telegram).

---

## 🔁 Surveillance temps réel : `pump_detector.py`

### 📥 Source de données

- Table `ticks` (ou `intraday_smart`) de la base `trades.db`
- Mise à jour via : `realtime/real_time_tick_collector.py`

### 🔎 Critères de détection (paramétrables)

Chargés depuis `config/rules_auto.json` :

| Paramètre           | Valeur par défaut | Rôle                                       |
| ------------------- | ----------------- | ------------------------------------------ |
| `price_spike_pct`   | 5.0               | Variation minimum (%) sur quelques minutes |
| `volume_ratio_min`  | 3.0               | Volume instantané / moyenne historique     |
| `trailing_stop_pct` | 2.5               | Pourcentage utilisé pour trailing stop     |

### 🔧 Exemple d'appel simplifié

```python
if price_change > price_spike_pct and volume_ratio > volume_ratio_min:
    envoyer_alerte_ia(ticker, motif="Pump détecté")
    simulate_trailing_trade(ticker)
```

---

## 🧠 Composant IA : `simulate_trailing_trade()`

Ce simulateur effectue un achat virtuel à l’instant du signal, puis laisse le **Trailing Stop** gérer la sortie en maximisant le gain sans retour brutal.

Fonctions clés :

- `TrailingStop(entry_price, stop_pct)`
- `update(price)` → met à jour dynamiquement le niveau de sortie

### Exemple illustratif :

```python
ts = TrailingStop(entry_price=1.0, stop_pct=0.025)

for price in [1.01, 1.03, 1.07, 1.05, 1.02]:
    new_sl = ts.update(price)
    print(f"New SL: {new_sl:.2f}")
```

🔁 Lors d’un retracement dépassant le SL calculé, la **vente est déclenchée automatiquement**.

---

## 💾 Enregistrement simulé : `simulate_trade_result.py`

Tous les résultats sont insérés dans :

| Table            | Champs utilisés                                                |
| ---------------- | -------------------------------------------------------------- |
| `trades_simules` | `symbol`, `entry`, `exit`, `gain`, `sl`, `strategy`, `comment` |

---

## 🔔 Notifications

| Méthode               | Description                         |
| --------------------- | ----------------------------------- |
| `envoyer_alerte_ia()` | Message Telegram ou popup Streamlit |
| `popup_trade.py`      | Fenêtre en overlay dans l'interface |

---

## ⚖️ Justification des paramètres

- **Variation de prix ≥ 5%** : seuil conservateur pour éviter les faux signaux
- **Ratio volume ≥ 3x** : filtre les mouvements faibles ou suspects
- **Trailing Stop 2.5%** : sécurisé mais assez large pour laisser courir un pump

Ces valeurs sont optimisées pour : **penny stocks entre 0.5\$ et 10\$, float faible, catalyst actif**.

---

## 🔗 Modules liés

| Module                                 | Fonction                              |
| -------------------------------------- | ------------------------------------- |
| `realtime/real_time_tick_collector.py` | Alimente `ticks` en live              |
| `simulate_trade_result.py`             | Calcule les résultats simulés         |
| `telegram_bot.py` / `popup_trade.py`   | Envoie les alertes                    |
| `ai_scorer.py`                         | Peut ajuster le score suite à un pump |

---

## 📌 User Stories associées

- **US-PUMP-001** – En tant qu’IA, je dois détecter rapidement les variations de prix brutales.
- **US-PUMP-002** – En tant que système, je dois vérifier si le volume valide le mouvement.
- **US-PUMP-003** – En tant qu’utilisateur, je veux être alerté immédiatement avec un message clair.
- **US-PUMP-004** – En tant que simulateur, je dois estimer le gain net avec trailing stop.

---

> ✅ Ce module est critique pour détecter des opportunités ultra-courtes en temps réel, tout en assurant une sortie intelligente sans stress manuel.

---


# 30_execution_reelle_et_journal (1)

# 📘 Chapitre 30 – Exécution des Ordres Réels & Journalisation

Ce module gère l’envoi réel des ordres d’achat ou de vente, que ce soit vers un courtier ou en mode simulation locale. Il est au cœur de la gestion de l’exécution sécurisée, traçable, et connectée à l’IA.

---

## 🎯 Objectifs du module

- Exécuter les ordres en respectant les règles de stratégie et de sécurité
- Journaliser chaque action dans la base (`real_trades`, `trade_logs`...)
- Confirmer l’exécution ou l’échec (avec détails)
- Gérer les erreurs et états (annulé, échoué, rempli partiellement, etc.)
- Déclencher les notifications (interface, son, Telegram)

---

## ⚙️ Logique d’exécution

```python
from execution.broker_api import envoyer_ordre
from db_model import enregistrer_trade_reel

def executer_ordre(ticker, prix, quantite, sens="buy", strategie="manual"):
    try:
        resultat = envoyer_ordre(ticker, prix, quantite, sens)
        if resultat["status"] == "filled":
            enregistrer_trade_reel(ticker, prix, quantite, sens, resultat, strategie)
        return resultat
    except Exception as e:
        logger.error(f"Erreur exécution: {e}")
        return {"status": "failed", "error": str(e)}
```

---

## 🧾 Table `real_trades`

| Champ      | Type  | Description                            |
| ---------- | ----- | -------------------------------------- |
| id         | INT   | Identifiant unique                     |
| symbol     | TEXT  | Ticker exécuté                         |
| date\_time | TEXT  | Timestamp de l’ordre                   |
| type       | TEXT  | buy / sell                             |
| prix       | FLOAT | Prix d’exécution                       |
| quantite   | INT   | Quantité exécutée                      |
| status     | TEXT  | filled / partial / failed              |
| courtier   | TEXT  | API utilisée (IBKR, Alpaca, Simulé...) |
| strategie  | TEXT  | Stratégie ayant généré l’ordre         |
| log\_id    | INT   | Référence vers la ligne de log         |

---

## 🗂️ Modules Python concernés

- `execution/broker_api.py` → interface avec API courtier ou simulateur
- `execution/strategie_scalping.py` → appel à `executer_ordre`
- `db_model.py` → gestion de la table `real_trades`
- `journal/journal.py` → enregistrement contextuel des logs
- `ui/pages/dashboard.py` → affichage des résultats et historiques
- `telegram/alertes.py` → notification si exécution réelle réussie ou échouée

---

## 📌 User Stories

- **US-EXEC-001** – En tant que système, je veux envoyer un ordre au courtier et obtenir une confirmation.
- **US-EXEC-002** – En tant qu’utilisateur, je veux voir mes ordres exécutés dans une interface claire.
- **US-EXEC-003** – En tant que bot, je veux enregistrer chaque ordre pour audit et apprentissage futur.
- **US-EXEC-004** – En tant que développeur, je veux pouvoir simuler l’exécution locale sans courtier.
- **US-EXEC-005** – En tant qu’analyste, je veux suivre l’état de chaque ordre (échec, partiel, rempli).

---

## ✅ Cas de test

| Cas de test                                      | Résultat attendu                               |
| ------------------------------------------------ | ---------------------------------------------- |
| Envoi d’un ordre d’achat à 1.00 pour 100 actions | Réponse `filled` avec données enregistrées     |
| Courtier non disponible                          | Réponse `failed` + erreur affichée/loguée      |
| Interface affiche la ligne                       | L’ordre apparaît dans l’historique utilisateur |
| Notification Telegram activée                    | Message envoyé avec détails de l’ordre         |
| Ordre partiellement rempli                       | Statut `partial` + quantité réelle enregistrée |

---

## 🔐 Aspects sécurité & robustesse

- Vérification du solde ou capital simulé
- Validation du ticker et de la stratégie
- Timeout automatique si pas de réponse du courtier
- Log complet en local (erreur + succès)
- Aucune répétition en cas d’échec sauf confirmation explicite

---

## 🧠 Impact global

✅ Centralise les décisions en un point unique d’exécution ✅ Traçabilité complète (backtest, audit, apprentissage IA) ✅ Sécurité renforcée contre les erreurs d’ordre ✅ Intégration multi-brokers ou mode déconnecté sans perte de logique

---


# 31_cloture_journaliere

# 📘 Chapitre 31 – Clôture Journalière Automatique & Résumé des Performances

Ce module permet de geler les activités de la journée, de sauvegarder les résultats, d’enrichir les indicateurs d’apprentissage, et de fournir un tableau de bord consolidé pour évaluer les performances.

---

## 🎯 Objectifs du module

- Arrêter proprement toutes les activités de trading à la fin de la journée
- Calculer les statistiques journalières : gains, pertes, nombre d’ordres, ratio de succès
- Archiver les données critiques dans la base (`daily_summary`, `indicateurs_ia`...)
- Mettre à jour les scores et les pondérations IA selon les résultats
- Envoyer un résumé automatique par mail, Telegram ou UI

---

## ⚙️ Logique de traitement

```python
from cloture import cloturer_journee
from dashboard import generer_resume

def cloture_auto():
    cloturer_journee()
    resume = generer_resume()
    notifier_resultats(resume)
```

---

## 🧾 Table `daily_summary`

| Champ            | Type  | Description                           |
| ---------------- | ----- | ------------------------------------- |
| id               | INT   | Identifiant                           |
| date             | TEXT  | Date de clôture (YYYY-MM-DD)          |
| nb\_trades       | INT   | Nombre total d’ordres exécutés        |
| gain\_total      | FLOAT | Gain ou perte net de la journée       |
| nb\_gagnants     | INT   | Ordres ayant généré un gain           |
| nb\_perdants     | INT   | Ordres perdants                       |
| taux\_reussite   | FLOAT | Pourcentage de réussite (0 à 1)       |
| max\_win         | FLOAT | Meilleur gain réalisé                 |
| max\_loss        | FLOAT | Plus grosse perte                     |
| moyenne\_holding | FLOAT | Durée moyenne de détention en minutes |

---

## 🧾 Table `indicateurs_ia`

| Champ          | Type  | Description                                 |
| -------------- | ----- | ------------------------------------------- |
| date           | TEXT  | Date d’entrée                               |
| param\_name    | TEXT  | Nom de l’indicateur (ex: score\_rsi)        |
| value          | FLOAT | Valeur moyenne observée ce jour-là          |
| trades\_winner | INT   | Nombre de trades gagnants avec ce paramètre |
| trades\_loser  | INT   | Nombre de trades perdants                   |
| poids\_ajuste  | FLOAT | Poids ajusté en fonction des résultats      |

---

## 🗂️ Modules Python concernés

- `cloture.py` → déclencheur du processus de fin de journée
- `dashboard.py` → résumé visuel, tableau, export CSV
- `journal.py` → collecte et nettoyage des journaux
- `utils.py` → fonctions d’agrégation, calculs de moyenne, ratio, etc.
- `telegram/alertes.py` → envoi du bilan en message
- `ia/learning_engine.py` → mise à jour pondérée des paramètres

---

## 📌 User Stories

- **US-CLOT-001** – En tant que bot, je veux sauvegarder proprement tous les résultats à 16h00.
- **US-CLOT-002** – En tant qu’utilisateur, je veux voir un tableau clair avec les gains et pertes du jour.
- **US-CLOT-003** – En tant que système IA, je veux adapter les pondérations selon la réussite des signaux.
- **US-CLOT-004** – En tant qu’analyste, je veux exporter un bilan journalier en CSV.
- **US-CLOT-005** – En tant qu’utilisateur, je veux recevoir un résumé des performances sur Telegram ou mail.

---

## ✅ Cas de test

| Cas de test                          | Résultat attendu                                   |
| ------------------------------------ | -------------------------------------------------- |
| Appel à `cloturer_journee()` à 16h00 | Données sauvegardées dans `daily_summary`          |
| IA met à jour les pondérations       | Changement visible dans `indicateurs_ia`           |
| UI affiche le résumé du jour         | Dashboard avec gains, pertes, ratio, top trades    |
| CSV exporté avec succès              | Fichier contenant tous les résultats de la journée |
| Alerte envoyée en fin de clôture     | Message Telegram avec les chiffres clés            |

---

## 🧠 Intérêt stratégique

✅ Permet d’avoir une trace quotidienne pour le backtest ✅ Nourrit le moteur IA avec des statistiques réelles ✅ Automatise les bilans et facilite la communication à l’utilisateur ✅ Sert de base pour l’évolution de la stratégie à long terme

---

## 🔐 Aspects sécurité & qualité

- Clôture bloquée si des ordres sont encore en cours
- Vérification de l’intégrité des journaux avant agrégation
- Sauvegarde redondante dans un fichier CSV + base
- Possibilité de rejouer les étapes si données absentes
- Archivage automatique hebdomadaire et mensuel

---


# 31_daily_workflow_detailed

# 📘 Chapitre 31 – Workflow Journalier Complet (Daily Workflow)

Ce chapitre détaille l’enchaînement **complet, structuré et justifié** des modules utilisés au quotidien dans WatchlistBot V7.03, depuis l’ouverture jusqu’à la clôture de session, incluant les indicateurs techniques utilisés, leurs valeurs seuils, les fonctions appelées, les tables mises à jour, et les raisons des choix techniques.

---

## 🧭 Vue d’ensemble du workflow journalier

```mermaid
graph TD
    Start[Lancement UI Streamlit] --> Import[Import Watchlist (manuel, Jaguar, fichier)]
    Import --> Analyse[Analyse IA + Scoring (indicateurs)]
    Analyse --> Affichage[Affichage des tickers + Interface interactive]
    Affichage --> Execution[Simulation ou Exécution de stratégie scalping]
    Execution --> Journal[Journalisation des trades (trades.db)]
    Journal --> Cloture[Clôture journalière + export + reset]
    Cloture --> End[Fin de session]
```

---

## 🔁 Étape 1 : Lancement de l’application

| Élément           | Description                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------- |
| Commande          | `streamlit run ui/app_unifie_watchlistbot.py`                                                 |
| Modules chargés   | `analyse_tickers_realtime.py`, `cloture_journee.py`, `checklist_import_affichage.py`, etc.    |
| Fonction critique | `charger_watchlist()` → charge `tickers_manuels.json`, `watchlist_jaguar.txt`, `meta_ia.json` |
| Précondition      | Connexion à `data/trades.db` avec toutes les tables initialisées                              |

---

## 📥 Étape 2 : Import ou ajout de tickers

| Source | Module Python                                        | Type           |
| ------ | ---------------------------------------------------- | -------------- |
| Manuel | `tickers_manuels.json`                               | JSON statique  |
| Jaguar | `scripts/scraper_jaguar.py` → `watchlist_jaguar.txt` | scraping texte |
| IA     | `meta_ia.json` généré par `learning_loop.py`         | pondérations   |

Fonction centrale : `fusion/module_fusion_watchlist.py`

```python
# Exemple de fusion des sources
sources = [tickers_manuels, jaguar, ia_meta]
watchlist_fusion = fusionner_watchlists(sources)
```

> 🎯 Objectif : obtenir une liste unifiée et filtrée de tickers pertinents à analyser.

---

## 🤖 Étape 3 : Analyse IA et Scoring

Module principal : `intelligence/ai_scorer.py`

### Indicateurs utilisés & valeurs typiques (ajustables)

| Indicateur | Fonction                       | Seuil / Poids                | Raison                                 |
| ---------- | ------------------------------ | ---------------------------- | -------------------------------------- |
| RSI        | `get_rsi(ticker)`              | 70 (surachat), 30 (survente) | Momentum                               |
| EMA        | `get_ema(ticker, [9,21])`      | Croisement EMA9 > EMA21      | Signal haussier                        |
| VWAP       | `get_vwap(ticker)`             | Prix > VWAP = force          | Volume moyen pondéré                   |
| MACD       | `get_macd(ticker)`             | MACD > 0 et > signal         | Accélération tendance                  |
| Volume     | `get_volume(ticker, '1m')`     | > 500 000                    | Activité confirmée                     |
| Float      | `get_float(ticker)`            | < 100M                       | Petite capitalisation → potentiel pump |
| Catalyseur | `get_catalyseur_score(ticker)` | > 0.7                        | News, FDA, fusion...                   |
| ATR        | `get_atr(ticker)`              | base pour SL/TP dynamiques   | Volatilité                             |

### Fonction critique

```python
def _compute_score(ticker):
    rsi = get_rsi(ticker)
    ema = get_ema(ticker, [9, 21])
    volume = get_volume(ticker)
    price = get_last_price(ticker)
    score = calculer_score_pondere(rsi, ema, volume, price, ...)
    return score
```

Résultat stocké dans : `scores` table (SQLite)

---

## 📊 Étape 4 : Affichage et interface utilisateur

- Interface : `ui/app_unifie_watchlistbot.py`
- Composants : boutons de scan, filtres, sliders score, mode debug
- Backend : `analyse_tickers_realtime.py`, `dashboard.py`

Fonctions :

- `afficher_watchlist()` → composants dynamiques
- `afficher_graphiques_indicateurs(ticker)`
- `streamlit.expander()` par ticker : score, graphique, indicateurs clés, bouton de simulation/exécution

---

## 📈 Étape 5 : Simulation ou Exécution réelle

| Mode       | Modules                                            | Base de données  |
| ---------- | -------------------------------------------------- | ---------------- |
| Simulation | `simulate_trade_result.py`, `execution_simulee.py` | `trades_simules` |
| Exécution  | `strategie_scalping.py`, `executer_ordre_reel()`   | `trades`         |

📌 Code clé dans stratégie :

```python
def executer_strategie_scalping(ticker):
    if enter_breakout(ticker, price, atr):
        ordre = executer_ordre_reel(ticker)
        enregistrer_trade_auto(ticker, ordre)
        envoyer_alerte_ia(ticker, ...)
```

---

## 📝 Étape 6 : Journalisation des trades

| Table concernée  | Colonnes                                                      |
| ---------------- | ------------------------------------------------------------- |
| `trades`         | `id`, `symbol`, `price`, `volume`, `pnl`, `type`, `timestamp` |
| `trades_simules` | `symbol`, `entry`, `exit`, `gain`, `stop_loss`, `comment`     |

🔁 Appelée via : `enregistrer_trade_auto()` ou `enregistrer_trade_simule()`

---

## 🛑 Étape 7 : Clôture de journée

| Module    | `cloture_journee.py` |
| --------- | -------------------- |
| Fonction  | `cloturer_journee()` |
| Actions : |                      |

- Calculs de PnL finaux
- Export JSON/Excel possible
- Nettoyage : reset watchlist, scores, tickers ignorés
- Envoi d’une alerte Telegram récapitulative

---

## 📌 User Stories associées

- **US-WF-001** – En tant qu’utilisateur, je veux pouvoir démarrer ma session avec les bons tickers chargés automatiquement.
- **US-WF-002** – En tant qu’IA, je veux scorer tous les tickers avec mes indicateurs pour prioriser les opportunités.
- **US-WF-003** – En tant que trader, je veux simuler ou exécuter une stratégie et voir mes résultats.
- **US-WF-004** – En tant qu’utilisateur, je veux pouvoir clôturer ma journée proprement avec tous les logs sauvegardés.

---

## 📂 Fichiers sources impliqués dans ce workflow

- `ui/app_unifie_watchlistbot.py`
- `fusion/module_fusion_watchlist.py`
- `intelligence/ai_scorer.py`
- `execution/strategie_scalping.py`
- `simulation/simulate_trade_result.py`
- `db/trades.py`, `db/scores.py`
- `notifications/telegram_bot.py`
- `ui/page_modules/cloture_journee.py`

---

## 📚 Notes complémentaires

- Les seuils d’indicateurs sont ajustables dans `config/rules_auto.json`
- Tous les résultats sont sauvegardés dans `data/trades.db` pour auditabilité
- L’apprentissage IA est renforcé à partir de la base `trades_simules` (voir `learning_loop.py`)

> ✅ Ce chapitre est indispensable pour comprendre le cycle de vie complet du bot pendant une session de trading.

---


# 32_logs_et_historique_audit (1)

# 📘 Chapitre 32 – Logs, Historique, Audit & Redondance

Ce module est au cœur de la fiabilité du bot. Il assure une traçabilité complète des actions, une supervision des anomalies, et une base d’audit pour les équipes techniques, légales ou analytiques.

---

## 🎯 Objectifs du module

- Enregistrer **chaque action importante** effectuée par le bot (scan, exécution, alerte...)
- Sauvegarder tous les messages d’erreur ou de debug dans des fichiers lisibles
- Conserver un historique structuré pour la **relecture ou le replay**
- Fournir un système de **traçabilité/audit** pour l’IA, les décisions et l’exécution
- Permettre une redondance locale (fichier) et distante (base SQL ou cloud)

---

## 🗃️ Répertoire de Logs (`logs/`)

| Fichier                   | Description                                     |
| ------------------------- | ----------------------------------------------- |
| `logs/system.log`         | Journal général des actions (niveau INFO)       |
| `logs/error.log`          | Journal des erreurs critiques                   |
| `logs/trading_{date}.log` | Journal de chaque jour de trading (exécution)   |
| `logs/ia_learning.log`    | Activités du moteur IA (pondérations, feedback) |
| `logs/audit.log`          | Trace complète des décisions, avec horodatage   |

Tous les logs utilisent le format suivant :

```
[2025-06-21 15:05:33] INFO - Exécution de trade sur $CAMP à 3.12$ réussie
[2025-06-21 15:05:34] ERROR - Erreur API Finnhub : Timeout
```

Rotation automatique tous les 7 jours, avec compression des anciens fichiers (`.gz`).

---

## 🧾 Table `journal_execution`

| Champ     | Type | Description                                |
| --------- | ---- | ------------------------------------------ |
| id        | INT  | Identifiant                                |
| timestamp | TEXT | Date/heure de l’action (UTC)               |
| module    | TEXT | Nom du module (`execution`, `ia`, etc.)    |
| action    | TEXT | Action réalisée (`order_executed`, etc.)   |
| details   | TEXT | Détail structuré en JSON (données, params) |

## 🧾 Table `error_log`

| Champ     | Type | Description                               |
| --------- | ---- | ----------------------------------------- |
| id        | INT  | Identifiant                               |
| timestamp | TEXT | Date/heure                                |
| source    | TEXT | Module ou service à l’origine de l’erreur |
| niveau    | TEXT | `WARNING`, `ERROR`, `CRITICAL`            |
| message   | TEXT | Message d’erreur                          |

## 🧾 Table `audit_trail`

| Champ       | Type | Description                            |
| ----------- | ---- | -------------------------------------- |
| id          | INT  | Identifiant                            |
| horodatage  | TEXT | Datetime complet UTC                   |
| event\_type | TEXT | `DECISION_IA`, `OVERRIDE_MANUAL`, etc. |
| user\_id    | TEXT | (optionnel) identifiant utilisateur    |
| payload     | TEXT | Données brutes liées à l’événement     |

---

## 🧠 Modules Python concernés

- `utils/logger.py` – Initialisation des fichiers et niveaux de log
- `journal.py` – Insertion dans les tables SQL et consolidation
- `error_handler.py` – Catch et enrichissement des erreurs
- `audit.py` – Génération de traces pour chaque événement critique

---

## 🧩 Intégration avec le système IA

Chaque décision d’achat/vente, chaque apprentissage ou chaque ajustement est loggé avec :

- Score IA
- Paramètres déclencheurs
- Source (news, algo, manuel)
- Résultat final (succès, échec, rejet)

Permet de **tracer les biais**, **justifier les actions IA**, et **alimenter la courbe de confiance IA**.

---

## 📌 User Stories

- **US-LOG-001** – En tant qu’analyste, je veux accéder à tous les événements du bot pour relecture.
- **US-LOG-002** – En tant qu’admin, je veux être alerté immédiatement en cas d’erreur critique.
- **US-LOG-003** – En tant que responsable IA, je veux voir toutes les décisions et leurs justifications.
- **US-LOG-004** – En tant qu’architecte, je veux que les logs soient compressés, redondants et historisés.
- **US-LOG-005** – En tant que développeur, je veux injecter les logs dans un dashboard de monitoring.

---

## ✅ Cas de test

| Cas de test                                | Résultat attendu                               |
| ------------------------------------------ | ---------------------------------------------- |
| Ajout d’une ligne dans `journal_execution` | Visible immédiatement en SQL et fichier `.log` |
| Génération d’un message d’erreur           | Ajout dans `error_log` avec message horodaté   |
| Clôture journalière                        | Regroupement de tous les logs dans un seul ZIP |
| Lancement IA                               | Trace des poids IA avant/après visibles        |
| Crash système                              | Sauvegarde des logs persistée (aucune perte)   |

---

## 🛡️ Sécurité, audit, conformité

- Accès restreint aux fichiers `.log` en écriture uniquement via le bot
- Contrôle via hash d’intégrité SHA256 pour `audit.log`
- Surveillance par script cron toutes les 24h pour anomalie dans les logs
- Possibilité de remontée dans un ELK Stack (ElasticSearch, Kibana...)

---

## 🧠 Intérêt stratégique

✅ Reproductibilité des bugs et des trades ✅ Preuve légale d’exécution ou d’alerte IA ✅ Diagnostic rapide en cas de crash ou dérive comportementale ✅ Pilier de l’observabilité dans l’écosystème WatchlistBot

Souhaites-tu que je passe au chapitre suivant : **33 – Interface UI, Panneaux Dynamiques & Tableaux** ?

---


# 33_interface_ui_et_panneaux_dynamiques

# 📘 Chapitre 33 – Interface UI, Panneaux Dynamiques & Tableaux

Ce chapitre présente l’interface principale de WatchlistBot, développée avec Streamlit. Elle sert à visualiser les données critiques des tickers, interagir avec les modules IA, simuler des ordres, et piloter le bot.

---

## 🎯 Objectifs de l’interface

- Offrir une **navigation claire et fluide** entre les étapes du processus (scan → analyse → simulation → exécution → journal)
- Permettre une **visualisation détaillée** de chaque ticker, avec **graphique, score, indicateurs clés**
- Autoriser les utilisateurs à **simuler ou exécuter un ordre** directement depuis l’écran
- Afficher dynamiquement les données de l’IA, avec **valeurs apprises**, **score actuel**, **alerte visuelle/sonore**
- Offrir un tableau récapitulatif avec **pagination** pour garder une vue globale sans surcharger l’écran

---

## 🧩 Modules Python concernés

- `ui/app_unifie_watchlistbot.py` – Point d’entrée principal
- `ui/pages/` – Pages dynamiques modulaires (watchlist, IA, paramètres...)
- `ui/components/panneau_ticker.py` – Affichage détaillé d’un ticker (score, graph, infos)
- `execution/strategie_scalping.py` – Appelé pour la simulation/exécution depuis l’interface
- `intelligence/modeles_dynamiques.py` – Récupération des paramètres IA appris

---

## 🖼️ Structure visuelle

- **Sidebar** :
  - Filtres (score min, float, penny stocks…)
  - Boutons : Lancer analyse, Stopper, Importer, Clôturer
  - Options debug, affichage valeurs IA, logs

- **Corps principal** :
  - **Liste paginée de tickers** (10 à 20 par page)
  - Chaque ticker = **panneau Streamlit dépliable** avec :
    - Score global + source
    - Prix actuel, variation, volume, float
    - Graphique dynamique (via `utils_graph.py` ou yfinance)
    - Formulaire : prix d’achat, quantité, frais, SL, TP
    - Bouton : `Exécuter ordre`
    - Résultat affiché immédiatement après simulation

---

## 📊 Tableaux utilisés

- `watchlist_enrichie` : liste des tickers avec toutes les colonnes IA
- `trades_simules` : résultats des simulations en base
- `parametres_dynamiques` : stockage des valeurs apprises (mise à jour live)

---

## ⚙️ Champs affichés dans les panneaux

| Champ              | Source                  | Exemple | Description                                         |
|--------------------|--------------------------|---------|-----------------------------------------------------|
| `score`            | IA (modèle composite)    | 87      | Score agrégé basé sur les indicateurs pondérés      |
| `prix_actuel`      | Finnhub Live             | 3.21    | Dernier prix                                         |
| `volume_1m`        | Finnhub Live             | 890000  | Volume sur la dernière minute                       |
| `variation_pct`    | Finnhub / calcul interne | +23.4%  | Variation depuis l’ouverture                         |
| `float`            | Finnhub Fundamentals     | 47M     | Nombre d’actions disponibles à la vente             |
| `source`           | Watchlist import         | Jaguar  | Origine du ticker (manuel, news, IA...)             |
| `stop_loss`        | Formule dynamique        | 3.00    | SL proposé (ATR ou pourcentage)                     |
| `take_profit`      | Formule dynamique        | 3.50    | TP proposé                                           |
| `gain_potentiel`   | Calcul automatique       | +12.5%  | Différence entre prix actuel et TP - frais          |

---

## 🧠 Intégration IA – UI

L’interface permet de :
- Voir en temps réel les valeurs apprises par l’IA
- Afficher les coefficients d’importance des indicateurs (heatmap)
- Simuler une évolution de marché pour tester la robustesse du modèle IA
- Notifier l’utilisateur si une décision IA diverge du comportement habituel

---

## 📌 User Stories

- **US-UI-001** – En tant qu’utilisateur, je veux visualiser les tickers avec les scores et graphiques en un seul écran
- **US-UI-002** – En tant qu’analyste, je veux modifier le prix d’achat/vente et simuler un ordre en temps réel
- **US-UI-003** – En tant qu’admin, je veux accéder aux logs ou à l’état IA depuis l’interface sans changer de page
- **US-UI-004** – En tant qu’investisseur, je veux savoir d’où provient un ticker (manuel, IA, news)
- **US-UI-005** – En tant que testeur, je veux voir les ordres simulés s’afficher dynamiquement après clic

---

## ✅ Cas de test

| Cas de test                                 | Résultat attendu                                           |
|---------------------------------------------|------------------------------------------------------------|
| Clic sur ticker                             | Déploiement du panneau avec données                        |
| Simulation d’ordre                          | Ajout dans DB `trades_simules` + affichage dans UI        |
| Modification de paramètres IA dans backend  | Changement visible immédiatement dans l’interface          |
| Changement de filtre dans sidebar           | Rafraîchissement automatique de la liste                   |
| Importation Watchlist (fichier ou Jaguar)   | Affichage des nouveaux tickers en temps réel              |

---

## 🎨 Accessibilité et ergonomie

- Contrastes couleurs validés WCAG (Dark/Light)
- Icônes explicites pour les boutons (exécution, alerte...)
- UI multilingue prévu (FR/EN)
- Navigation fluide sans rechargement inutile (optimisation Streamlit caching)

---

## 📌 Enjeux stratégiques

- Clarté des données pour prise de décision rapide
- Intégration étroite IA–utilisateur final
- Évolutivité pour des interfaces spécialisées par rôle
- Gain de temps journalier pour l’opérateur humain
- Simulation d’ordres avant passage réel pour test en conditions réelles

---


# 34_generateur_watchlists_automatique (1)

# 📘 Chapitre 35 – Moteur de Scoring IA et Pondération Dynamique des Indicateurs

Ce module est responsable de l’évaluation des tickers identifiés, en attribuant un **score de pertinence** basé sur des indicateurs techniques, fondamentaux, et contextuels. Ce score guide ensuite les modules d’exécution, de simulation, et d’alerte.

---

## 🎯 Objectifs du moteur de scoring

- Calculer un **score unique et standardisé (sur 100)** pour chaque ticker détecté
- Pondérer dynamiquement les **indicateurs techniques et catalyseurs** selon le contexte
- Exploiter un système IA qui **apprend des trades passés** et ajuste les pondérations
- Fournir des données exploitables en priorité pour les modules d’exécution

---

## 📦 Modules Python concernés

- `intelligence/scoring_engine.py` – Calcul du score global
- `intelligence/indicateurs.py` – Récupération des indicateurs techniques
- `intelligence/model_ia.py` – Pondération dynamique et auto-ajustement
- `data/stream_data_manager.py` – Données de marché en temps réel (float, prix, volume...)
- `utils_finnhub.py` – Données fondamentales et catalyseurs externes

---

## 📊 Indicateurs utilisés dans le scoring

| Indicateur       | Rôle dans la stratégie           | Seuils critiques       | Pondération (%) par défaut |
| ---------------- | -------------------------------- | ---------------------- | -------------------------- |
| RSI (14)         | Surachat/survente                | RSI > 70 (risque pump) | 10 %                       |
| EMA 9 / EMA 21   | Confirmation de tendance         | EMA9 > EMA21           | 15 %                       |
| VWAP             | Niveau clé intraday              | Prix > VWAP            | 10 %                       |
| MACD             | Momentum court/moyen terme       | MACD > 0               | 10 %                       |
| Volume 1m / 5m   | Activité récente                 | > 500 000              | 20 %                       |
| Gap d’ouverture  | Volatilité intraday              | > 10 %                 | 10 %                       |
| Float            | Potentiel de pump                | < 200M                 | 10 %                       |
| Score catalyseur | FDA, IPO, uplisting, etc.        | > 0.7                  | 10 %                       |
| Support IA       | Résultat d’analyse IA précédente | > 0.6                  | 5 %                        |

---

## 🧠 Logique de calcul du score

```python
score = (
    poids_rsi * get_rsi_score(ticker) +
    poids_ema * get_ema_score(ticker) +
    poids_vwap * get_vwap_score(ticker) +
    poids_macd * get_macd_score(ticker) +
    poids_volume * get_volume_score(ticker) +
    poids_gap * get_gap_score(ticker) +
    poids_float * get_float_score(ticker) +
    poids_catalyseur * get_catalyseur_score(ticker) +
    poids_ia * get_meta_ia_score(ticker)
)
```

---

## 🤖 Pondération dynamique par IA

Le moteur IA ajuste automatiquement les pondérations à partir :

- Des **résultats des trades précédents (gains réels vs estimés)**
- Du type de catalyseur (ex : FDA augmente le poids du volume)
- De la configuration du marché (volatilité générale mesurée par VIX)
- Des préférences utilisateur (scalping vs swing)

Un historique est conservé dans `learning_weights.json` et mis à jour quotidiennement.

---

## 🧪 Exemples concrets de scoring

| Ticker | RSI | EMA9>21 | VWAP | Volume | Float | Score Catalyseur | Score IA | Total  |
| ------ | --- | ------- | ---- | ------ | ----- | ---------------- | -------- | ------ |
| AVTX   | 72  | Oui     | Oui  | 1.2M   | 50M   | 0.9              | 0.65     | 96/100 |
| GNS    | 60  | Non     | Oui  | 600K   | 120M  | 0.8              | 0.5      | 76/100 |

---

## 🗃️ Tables & fichiers associés

| Fichier / Table         | Description                                     |
| ----------------------- | ----------------------------------------------- |
| `meta_ia.json`          | Résultats IA préalables à la détection          |
| `learning_weights.json` | Pondérations IA mises à jour quotidiennement    |
| `historique_trades.db`  | Résultats des simulations et exécutions réelles |
| `scoring_log.csv`       | Logs des scores journaliers pour audit          |

---

## 📌 User Stories

- **US-SCORE-001** – En tant que bot, je veux attribuer un score unique à chaque ticker pour décider de l’exécution
- **US-SCORE-002** – En tant qu’IA, je veux adapter les poids des indicateurs en fonction de mes apprentissages
- **US-SCORE-003** – En tant qu’analyste, je veux comprendre pourquoi un ticker a eu un score élevé
- **US-SCORE-004** – En tant qu’utilisateur, je veux afficher le score final et les composantes dans l’interface

---

## ✅ Cas de test

| Cas de test                              | Résultat attendu                        |
| ---------------------------------------- | --------------------------------------- |
| Calcul d’un score normal                 | Score entre 0 et 100, valeur cohérente  |
| Ticker avec volume nul                   | Score faible ou exclu du processus      |
| Poids IA ajusté après 10 trades gagnants | Pondération volume/catalyseur augmentée |
| Enregistrement dans scoring\_log.csv     | Score sauvegardé avec horodatage        |

---

## 🛡️ Sécurité & robustesse

- Protection contre division par zéro ou absence de données
- Exclusion des tickers avec données manquantes (float ou prix ≤ 0)
- Pondération IA limitée entre 0 % et 30 % pour éviter les dérives
- Journalisation complète des scores et poids

---

## 📈 Impact stratégique

- Filtrage automatisé des meilleures opportunités
- Renforcement de la logique IA dans le processus décisionnel
- Réduction des faux positifs grâce au contexte dynamique
- Transparence et auditabilité complète du modèle IA utilisé

Ce module est **au cœur de l'intelligence décisionnelle du bot WatchlistBot**, car il permet d’ordonner objectivement les tickers à analyser, simuler ou exécuter.

---


# 34_generateur_watchlists_automatique - Copie

# 📘 Chapitre 34 – Générateur de Watchlists Automatique

Ce module constitue la première étape du workflow quotidien. Il est chargé de générer, enrichir et fusionner les différentes sources de tickers pour créer une **watchlist pertinente et exploitable** pour le day trading algorithmique.

---

## 🎯 Objectifs du générateur

- Fusionner plusieurs sources de tickers : **manuelle**, **IA**, **Jaguar**, **news Finnhub**, **FDA**, **uplisting**, **IPO**, etc.
- Scanner les marchés **avant ouverture** (Pre-Market) et **après clôture** (Post-Market)
- Détecter automatiquement les **hausses >50 %**, **volumes >500K**, **float < 200M**, et **anomalies carnet d’ordre**
- Générer un **fichier JSON ou DataFrame** prêt à être analysé et scoré
- Déclencher des **alertes Telegram, alarmes sonores, et affichage UI**

---

## 📦 Modules Python concernés

- `data_sources/manual_loader.py` – Lecture du fichier `tickers_manuels.json`
- `data_sources/jaguar_scraper.py` – Scraping et parsing de la watchlist Jaguar
- `data_sources/news_scanner.py` – Scan des news Finnhub sur catalyseurs (FDA, IPO, fusion, uplisting)
- `data_sources/market_screener.py` – Détection automatique via variation/volume/float
- `utils/merge_watchlists.py` – Fusion, nettoyage et normalisation des sources
- `utils_finnhub.py` – Appels API pour données fondamentales

---

## 🔎 Critères de détection Pre-Market / Post-Market

| Critère                | Valeur cible | Justification métier                              |
| ---------------------- | ------------ | ------------------------------------------------- |
| Variation (%)          | > +50 %      | Signal fort de momentum, potentiel pump           |
| Volume PreMarket       | > 500 000    | Confirmation d’intérêt massif avant marché        |
| Float                  | < 200M       | Petit float = plus de volatilité                  |
| News FDA/IPO/Uplisting | Obligatoire  | Catalyseurs puissants validés par études          |
| Anomalie carnet ordre  | Oui          | Détection optionnelle si carnet trop déséquilibré |

---

## 🧠 Exemple de fusion des sources

```json
[
  {"symbol": "HLBZ", "source": "Jaguar", "score": null},
  {"symbol": "GNS", "source": "News_FDA", "score": null},
  {"symbol": "AVTX", "source": "PostMarketScanner", "score": null},
  {"symbol": "CNSP", "source": "Manuel", "score": null}
]
```

Chaque entrée est ensuite enrichie par les modules d’analyse technique avant scoring IA.

---

## 🗃️ Tables de données utilisées

| Table                   | Description                                  |
| ----------------------- | -------------------------------------------- |
| `tickers_manuels.json`  | Liste définie manuellement par l’utilisateur |
| `jaguar_watchlist.json` | Résultat du scraping journalier              |
| `meta_ia.json`          | Résultats IA des dernières analyses          |
| `watchlist_fusionnee`   | Watchlist globale, nettoyée et triée         |

---

## 📌 User Stories

- **US-WL-001** – En tant qu’utilisateur, je veux que mes tickers manuels soient toujours inclus dans la watchlist
- **US-WL-002** – En tant que trader, je veux détecter automatiquement les tickers ayant >50 % de variation Pre-Market
- **US-WL-003** – En tant qu’analyste, je veux ajouter automatiquement les tickers contenant des news FDA ou IPO
- **US-WL-004** – En tant qu’utilisateur, je veux recevoir une alerte Telegram dès qu’un nouveau ticker est détecté Post-Market
- **US-WL-005** – En tant qu’admin, je veux voir la provenance de chaque ticker pour justifier son ajout

---

## ✅ Cas de test

| Cas de test                       | Résultat attendu                                           |
| --------------------------------- | ---------------------------------------------------------- |
| Chargement manuel                 | Les tickers dans `tickers_manuels.json` sont intégrés      |
| Détection Pre-Market à 6h00       | Tous les tickers >50 % + volume >500k sont détectés        |
| Scraping Jaguar réussi            | Les tickers extraits sont visibles dans la fusion          |
| Watchlist fusionnée               | Pas de doublons, triée par priorité ou score               |
| Affichage dans l’interface        | Tous les tickers apparaissent dans les panneaux dynamiques |
| Détection d’un nouveau ticker FDA | Envoi alerte Telegram et popup dans l’UI                   |

---

## 📣 Intégrations et alertes

- 📱 **Telegram Bot** : envoi de messages automatiques avec ticker + raison + lien graph
- 🔊 **Alarme sonore locale** : bip en cas de détection Pre/Post-Market
- 📺 **Popup Streamlit** : message coloré + focus sur ticker détecté

---

## 🧠 Stratégie IA appliquée en post-détection

Après la génération, chaque ticker est :

1. Vérifié via `valider_ticker_finnhub()` (prix > 0, données existantes)
2. Enrichi avec les indicateurs techniques principaux (RSI, EMA, VWAP, etc.)
3. Transmis au module IA pour scoring (`scorer_ticker()`) et priorisation

---

## 🛠️ Robustesse & fallback

- Si une source échoue (API, scraping), les autres sources restent actives
- Un log est généré pour chaque phase (manuelle, IA, Jaguar, news)
- L'utilisateur est alerté si une source est manquante ou désactivée

---

## 🔒 Enjeux techniques

- Ne jamais manquer un ticker pertinent, surtout avec catalyseur FDA
- Éviter les doublons, les penny stocks indésirables (si filtre activé)
- Maintenir un pipeline stable même avec des interruptions API
- Offrir une lisibilité maximale aux opérateurs avant ouverture

---

## 📈 Impact stratégique

- Gain de temps chaque matin (watchlist prête à 9h)
- Réduction des erreurs humaines (filtres automatisés)
- Alignement sur les meilleures pratiques de scalping (momentum + news)
- Amélioration continue grâce à la boucle IA

---

Ce générateur constitue la **colonne vertébrale de la détection de trades potentiels**. Sans lui, le pipeline ne peut démarrer efficacement. C’est pourquoi il est testé en priorité dans toutes les versions du bot.

---


# 34_generateur_watchlists_automatique

# 📘 Chapitre 34 – Générateur de Watchlists Automatique

Ce module constitue la première étape du workflow quotidien. Il est chargé de générer, enrichir et fusionner les différentes sources de tickers pour créer une **watchlist pertinente et exploitable** pour le day trading algorithmique.

---

## 🎯 Objectifs du générateur

- Fusionner plusieurs sources de tickers : **manuelle**, **IA**, **Jaguar**, **news Finnhub**, **FDA**, **uplisting**, **IPO**, etc.
- Scanner les marchés **avant ouverture** (Pre-Market) et **après clôture** (Post-Market)
- Détecter automatiquement les **hausses >50 %**, **volumes >500K**, **float < 200M**, et **anomalies carnet d’ordre**
- Générer un **fichier JSON ou DataFrame** prêt à être analysé et scoré
- Déclencher des **alertes Telegram, alarmes sonores, et affichage UI**

---

## 📦 Modules Python concernés

- `data_sources/manual_loader.py` – Lecture du fichier `tickers_manuels.json`
- `data_sources/jaguar_scraper.py` – Scraping et parsing de la watchlist Jaguar
- `data_sources/news_scanner.py` – Scan des news Finnhub sur catalyseurs (FDA, IPO, fusion, uplisting)
- `data_sources/market_screener.py` – Détection automatique via variation/volume/float
- `utils/merge_watchlists.py` – Fusion, nettoyage et normalisation des sources
- `utils_finnhub.py` – Appels API pour données fondamentales

---

## 🔎 Critères de détection Pre-Market / Post-Market

| Critère                | Valeur cible | Justification métier                              |
| ---------------------- | ------------ | ------------------------------------------------- |
| Variation (%)          | > +50 %      | Signal fort de momentum, potentiel pump           |
| Volume PreMarket       | > 500 000    | Confirmation d’intérêt massif avant marché        |
| Float                  | < 200M       | Petit float = plus de volatilité                  |
| News FDA/IPO/Uplisting | Obligatoire  | Catalyseurs puissants validés par études          |
| Anomalie carnet ordre  | Oui          | Détection optionnelle si carnet trop déséquilibré |

---

## 🧠 Exemple de fusion des sources

```json
[
  {"symbol": "HLBZ", "source": "Jaguar", "score": null},
  {"symbol": "GNS", "source": "News_FDA", "score": null},
  {"symbol": "AVTX", "source": "PostMarketScanner", "score": null},
  {"symbol": "CNSP", "source": "Manuel", "score": null}
]
```

Chaque entrée est ensuite enrichie par les modules d’analyse technique avant scoring IA.

---

## 🗃️ Tables de données utilisées

| Table                   | Description                                  |
| ----------------------- | -------------------------------------------- |
| `tickers_manuels.json`  | Liste définie manuellement par l’utilisateur |
| `jaguar_watchlist.json` | Résultat du scraping journalier              |
| `meta_ia.json`          | Résultats IA des dernières analyses          |
| `watchlist_fusionnee`   | Watchlist globale, nettoyée et triée         |

---

## 📌 User Stories

- **US-WL-001** – En tant qu’utilisateur, je veux que mes tickers manuels soient toujours inclus dans la watchlist
- **US-WL-002** – En tant que trader, je veux détecter automatiquement les tickers ayant >50 % de variation Pre-Market
- **US-WL-003** – En tant qu’analyste, je veux ajouter automatiquement les tickers contenant des news FDA ou IPO
- **US-WL-004** – En tant qu’utilisateur, je veux recevoir une alerte Telegram dès qu’un nouveau ticker est détecté Post-Market
- **US-WL-005** – En tant qu’admin, je veux voir la provenance de chaque ticker pour justifier son ajout

---

## ✅ Cas de test

| Cas de test                       | Résultat attendu                                           |
| --------------------------------- | ---------------------------------------------------------- |
| Chargement manuel                 | Les tickers dans `tickers_manuels.json` sont intégrés      |
| Détection Pre-Market à 6h00       | Tous les tickers >50 % + volume >500k sont détectés        |
| Scraping Jaguar réussi            | Les tickers extraits sont visibles dans la fusion          |
| Watchlist fusionnée               | Pas de doublons, triée par priorité ou score               |
| Affichage dans l’interface        | Tous les tickers apparaissent dans les panneaux dynamiques |
| Détection d’un nouveau ticker FDA | Envoi alerte Telegram et popup dans l’UI                   |

---

## 📣 Intégrations et alertes

- 📱 **Telegram Bot** : envoi de messages automatiques avec ticker + raison + lien graph
- 🔊 **Alarme sonore locale** : bip en cas de détection Pre/Post-Market
- 📺 **Popup Streamlit** : message coloré + focus sur ticker détecté

---

## 🧠 Stratégie IA appliquée en post-détection

Après la génération, chaque ticker est :

1. Vérifié via `valider_ticker_finnhub()` (prix > 0, données existantes)
2. Enrichi avec les indicateurs techniques principaux (RSI, EMA, VWAP, etc.)
3. Transmis au module IA pour scoring (`scorer_ticker()`) et priorisation

---

## 🛠️ Robustesse & fallback

- Si une source échoue (API, scraping), les autres sources restent actives
- Un log est généré pour chaque phase (manuelle, IA, Jaguar, news)
- L'utilisateur est alerté si une source est manquante ou désactivée

---

## 🔒 Enjeux techniques

- Ne jamais manquer un ticker pertinent, surtout avec catalyseur FDA
- Éviter les doublons, les penny stocks indésirables (si filtre activé)
- Maintenir un pipeline stable même avec des interruptions API
- Offrir une lisibilité maximale aux opérateurs avant ouverture

---

## 📈 Impact stratégique

- Gain de temps chaque matin (watchlist prête à 9h)
- Réduction des erreurs humaines (filtres automatisés)
- Alignement sur les meilleures pratiques de scalping (momentum + news)
- Amélioration continue grâce à la boucle IA

---

Ce générateur constitue la **colonne vertébrale de la détection de trades potentiels**. Sans lui, le pipeline ne peut démarrer efficacement. C’est pourquoi il est testé en priorité dans toutes les versions du bot.

---


# 36_moteur_execution_ordres

# Chapitre 36 – Moteur d’Exécution des Ordres Simulés & Réels

## 🎯 Objectifs du module

Permettre au bot d’exécuter automatiquement des ordres d’achat et de vente, en prenant en compte :

- les frais réels (Moomoo Canada par défaut),
- les paramètres IA (stop loss, take profit, trailing stop),
- les décisions de l’utilisateur ou du système IA,
- la journalisation dans la base de données,
- le suivi des ordres pour apprentissage futur.

## 🧱 Modules Python concernés

- `execution/strategie_scalping.py`
- `db_model.py`
- `execution/ordre_utils.py`
- `simulation/simulateur_execution.py`

## 🗂️ Tables utilisées

### Table : `trades_simules`

| Colonne         | Type    | Description                           |
| --------------- | ------- | ------------------------------------- |
| id              | INTEGER | Clé primaire                          |
| symbole         | TEXT    | Symbole de l’action                   |
| type\_ordre     | TEXT    | 'achat' ou 'vente'                    |
| prix\_execution | REAL    | Prix payé ou reçu                     |
| quantite        | INTEGER | Quantité échangée                     |
| frais\_total    | REAL    | Frais déduits                         |
| pnl\_estime     | REAL    | Gain/perte estimé                     |
| strategie       | TEXT    | Nom de la stratégie utilisée          |
| horodatage      | TEXT    | Date et heure UTC                     |
| gain\_reel      | REAL    | Si fourni plus tard par l’utilisateur |
| source          | TEXT    | 'IA', 'Utilisateur', 'Test'           |

### Table : `trades_reels`

(mêmes colonnes + statut et courtier)

## ⚙️ Logique d’exécution

```python
# Exemple simplifié d'exécution simulée avec frais Moomoo Canada
COMMISSION = max(0.0049 * quantite, 0.99)
PLATFORM_FEE = min(max(0.005 * quantite, 1.0), 0.01 * (prix * quantite))
frais_total = round(COMMISSION + PLATFORM_FEE, 2)
```

### Étapes générales

1. Vérification des fonds simulés disponibles (si applicable)
2. Calcul des frais selon profil de courtier (modifiable via config)
3. Simulation ou exécution réelle de l’ordre
4. Enregistrement dans la base (`trades_simules` ou `trades_reels`)
5. Notification IA + enregistrement apprentissage (pour IA dynamique)

## 🧠 Fonctions IA intégrées

- Calcul du **gain projeté**
- Comparaison avec le **gain simulé réel**
- Ajustement automatique des paramètres : stop loss, taille, momentum
- Suivi des ordres IA dans `journal_apprentissage`

## 🧪 User Stories

### US-EXE-01 – Simulation avec frais dynamiques

**En tant que** Trader, **je veux** simuler l’achat d’une action en prenant en compte les frais réels, **afin de** valider la rentabilité d’une stratégie IA.

**Critères d’acceptation :**

- L’ordre simulé est enregistré dans `trades_simules`
- Les frais affichés respectent les règles du courtier
- Le résultat est affiché dans l’interface utilisateur

### US-EXE-02 – Ordre réel avec retour IA

**En tant que** Utilisateur IA, **je veux** exécuter un ordre via mon courtier réel (Moomoo, IBKR), **afin de** suivre les performances de mon modèle en production.

**Critères d’acceptation :**

- L’ordre est envoyé via l’API réelle (mockée pour test)
- Le statut (`filled`, `rejected`) est journalisé
- Une alerte est envoyée si le trade est exécuté avec succès

## 🔁 Cas d’utilisation spéciaux

- Ordre conditionnel (trigger sur prix ou volume)
- Ordre annulé (latence ou timeout IA)
- Exécution en backtest historique (module simulateur)

## 🔒 Journalisation et Sécurité

Chaque ordre (simulé ou réel) est lié à :

- l’utilisateur ou IA qui l’a généré,
- l’algorithme ayant pris la décision,
- les données de contexte (score, catalyseur, etc.)

Les logs sont stockés dans :

- `logs/orders/YYYY-MM-DD.log`
- Base de données pour réutilisation en IA ou analyse manuelle

## 🧪 Tests unitaires

- `test_execution_orders.py`
  - test\_frais\_calculés\_correctement
  - test\_enregistrement\_bdd\_simulée
  - test\_exécution\_mock\_réelle
  - test\_alerte\_post\_trade
  - test\_gain\_estime\_vs\_reel

## ✅ Résumé

Ce module centralise l'exécution automatique sécurisée d'ordres dans le bot. Il garantit la cohérence entre simulation, IA et interface, tout en assurant traçabilité, apprentissage et adaptation continue.

---

⏭️ Suivant : **Chapitre 37 – Module d’Apprentissage Automatique post-trade** ?

---


# 38_suivi_performances_dashboard

# Chapitre 38 – Suivi des Performances & Dashboard IA

## 🎯 Objectif du module

Offrir un tableau de bord complet de suivi des performances du bot de trading IA, permettant une évaluation claire, visuelle et temps réel de l’efficacité des stratégies exécutées, des scores IA et des résultats simulés ou réels.

---

## 🧱 Modules Python concernés

- `dashboard.py`
- `simulation/stats_kpi.py`
- `db_model.py`
- `utils_graph.py`
- `streamlit_pages/dashboard_performance.py`

---

## 🗂️ Tables utilisées

### Table : `trades_simules`

| Colonne      | Type | Description                            |
| ------------ | ---- | -------------------------------------- |
| symbole      | TEXT | Nom du ticker                          |
| date\_trade  | TEXT | Date UTC de la simulation              |
| gain\_simule | REAL | Gain ou perte estimé                   |
| strategie    | TEXT | Breakout, Pullback, etc.               |
| score\_ia    | REAL | Score IA au moment du trade            |
| statut       | TEXT | Statut du trade : success, échec, skip |

### Table : `trades_reels`

| Colonne     | Type | Description            |
| ----------- | ---- | ---------------------- |
| symbole     | TEXT | Titre du trade réel    |
| date\_trade | TEXT | Date UTC               |
| gain\_reel  | REAL | Gain ou perte constaté |
| sl\_price   | REAL | Stop loss utilisé      |
| tp\_price   | REAL | Take profit utilisé    |

---

## 📊 Indicateurs de performance

- ✅ Nombre de trades exécutés (par jour, semaine, mois)
- 💰 Profit net cumulé
- 📉 Maximum drawdown (max perte en %)
- 📈 Taux de réussite global et par stratégie
- 🔍 Moyenne du gain par trade
- 🧠 Score IA moyen des trades gagnants
- ⚖️ Ratio gain/perte (Risk Reward)

---

## 🧠 Visualisation (Streamlit)

- Graphiques `Plotly` :
  - Barres pour gain journalier
  - Courbe cumulée du capital
  - Pie chart répartition stratégie gagnante
- Filtres : par période, par stratégie, par score IA
- Section : "Top 5 des gains" / "Top 5 des pertes"

---

## 🧾 Exports et archivage

- 📁 Export CSV des performances quotidiennes (`performance_YYYYMMDD.csv`)
- 📄 Export PDF du dashboard à la clôture journalière

---

## ⚙️ Fichiers de configuration et fonctions clés

```python
# simulation/stats_kpi.py

def calculer_kpi(trades):
    taux_reussite = ...
    profit_total = ...
    drawdown = ...
    return {"success_rate": taux_reussite, "profit": profit_total, "max_drawdown": drawdown}

# dashboard.py

def generer_dashboard(df):
    fig1 = generer_courbe_capital(df)
    fig2 = generer_repartition_strategie(df)
    ...
```

---

## 📌 KPI Suivis par IA

- Impact moyen de chaque stratégie
- Gain moyen selon score IA [<70, 70-90, >90]
- Historique des versions de `meta_ia.json` utilisées

---

## 🧪 User Stories

### US-DASH-01 – Visualiser les performances quotidiennes

**En tant que** trader IA, **je veux** visualiser mes gains et pertes par jour, **afin de** piloter mon activité.

**Critères :**

- Accès direct à la performance du jour
- Filtrage par type de trade (IA / manuel / simulateur)

### US-DASH-02 – Calcul automatique des KPI

**En tant que** développeur IA, **je veux** automatiser le calcul des KPI de performance, **afin de** détecter toute dérive de stratégie.

**Critères :**

- Taux de réussite < 50% = alerte
- Drawdown > 10% = alerte IA

### US-DASH-03 – Export et archivage des performances

**En tant que** analyste, **je veux** exporter les résultats en CSV et PDF, **afin de** conserver une trace documentaire.

**Critères :**

- Génération quotidienne automatique du CSV à la clôture
- Export PDF disponible dans l’interface

---

## ✅ Résumé

Le module de dashboard et suivi de performance permet un pilotage global du bot de trading. Il consolide les résultats, détecte les dérives, alimente l’apprentissage IA, et fournit des rapports visuels à forte valeur pour les traders, les analystes, et les développeurs IA.

---


# 39_journalisation_et_rapports

# Chapitre 39 – Journalisation Complète & Rapports Quotidiens

## 🎯 Objectif du module

Assurer la traçabilité complète de toutes les actions du bot IA (exécution, erreurs, IA, utilisateur), générer des rapports quotidiens exploitables par tous les intervenants (traders, devs, DBA, responsables sécurité) et permettre l’audit, le support et l’analyse post-mortem.

---

## 📚 Modules Python concernés

- `utils_logger.py`
- `db_model.py`
- `rapport/generateur_rapport.py`
- `journal.py`
- `cloture.py`

---

## 📁 Fichiers de journalisation générés

- `journal_execution.csv` : ordres simulés/réels exécutés, détails complet
- `journal_erreurs.log` : erreurs critiques ou exception capturées
- `journal_apprentissage.json` : ajustements IA post-trade
- `journal_user.json` : actions manuelles utilisateur dans l’interface
- `rapport_cloture_YYYYMMDD.pdf` : synthèse quotidienne multi-source

---

## 🗂️ Tables SQLite concernées

### `journal_execution`

| Colonne     | Type    | Description                        |
| ----------- | ------- | ---------------------------------- |
| id          | INTEGER | ID unique                          |
| symbole     | TEXT    | Ticker concerné                    |
| type\_ordre | TEXT    | achat / vente / simulation / rejet |
| date\_exec  | TEXT    | Date UTC                           |
| prix\_exec  | REAL    | Prix exécuté                       |
| quantite    | INTEGER | Volume                             |
| strategie   | TEXT    | Stratégie utilisée                 |
| statut      | TEXT    | success / échec / pending          |

### `journal_erreurs`

| Colonne   | Type | Description                       |
| --------- | ---- | --------------------------------- |
| id        | INT  | Clé primaire                      |
| timestamp | TEXT | Heure UTC                         |
| module    | TEXT | Nom du fichier concerné           |
| message   | TEXT | Stacktrace ou message utilisateur |

### `journal_user`

| Colonne  | Type | Description                     |
| -------- | ---- | ------------------------------- |
| id       | INT  | Clé primaire                    |
| user\_id | TEXT | Identifiant utilisateur         |
| action   | TEXT | Ajout ticker, changement filtre |
| valeur   | TEXT | Valeur de l’action              |
| date     | TEXT | Date de l’action                |

---

## 🧾 Formats d’export automatique

- `.csv` pour journal lecture rapide et tableur
- `.json` pour usage technique ou API
- `.pdf` pour archivage quotidien avec synthèse visuelle

```python
# Extrait simplifié - cloture.py

def generer_rapport_pdf(date):
    data = lire_journaux_du_jour(date)
    render_pdf(data, output=f"rapport_cloture_{date}.pdf")
```

---

## 📈 Données intégrées dans le rapport PDF journalier

- Nombre total de trades (réussis, échoués)
- Performance globale (PnL du jour)
- Liste des erreurs critiques
- Liste des symboles à haut score IA
- Ajustements IA effectués ce jour
- Actions manuelles utilisateur

---

## 🧪 User Stories

### US-LOG-01 – Journalisation des actions système

**En tant que** développeur, **je veux** enregistrer chaque ordre exécuté, **afin de** pouvoir le relire en cas d’erreur ou de débogage.

**Critères :**

- Chaque ordre déclenche une écriture dans `journal_execution`
- Le statut (success / fail) est toujours renseigné

### US-LOG-02 – Suivi des erreurs critiques

\*\*En tant qu’\*\*administrateur, **je veux** consulter facilement les erreurs, **afin de** anticiper les crashs ou corriger les bugs.

**Critères :**

- Le fichier `journal_erreurs.log` est généré en temps réel
- Les erreurs contiennent timestamp, stacktrace et module

### US-LOG-03 – Génération de rapport PDF quotidien

**En tant que** responsable IA, **je veux** recevoir un PDF récapitulatif journalier, **afin de** suivre les résultats, incidents et ajustements IA.

**Critères :**

- Le PDF contient les 6 sections listées ci-dessus
- Il est automatiquement sauvegardé dans `rapports/`

---

## ✅ Résumé

Le système de journalisation et de génération de rapports est un pilier de traçabilité du bot. Il permet à chaque acteur (développeur, trader, support, analyste IA) de suivre, comprendre et corriger le comportement du système en toute transparence. Chaque donnée est horodatée, centralisée et exportable pour archivage, audit ou post-analyse.

---


# Chapitre_40_Securite

# Chapitre 40 – Sécurité, Authentification et Contrôle d’Accès

## 🎯 Objectif du module

Garantir un accès sécurisé à toutes les fonctionnalités critiques du bot WatchlistBot en intégrant un système de **login**, de **gestion des rôles**, de **journalisation des connexions** et de **contrôle dynamique des permissions** dans l’interface.

...

## ✅ Résumé

Ce module apporte une base solide de sécurité, extensible vers des systèmes professionnels.

---


# chapitre_41_assistant_vocal

# 🧠 Chapitre 41 — Intégration IA vocale ou assistant intelligent

## 🎯 Objectif
Permettre une interaction vocale intuitive entre l'utilisateur et le bot WatchlistBot, facilitant l'exécution d'ordres, l'interrogation de l'IA, la consultation de scores, et l'automatisation de tâches journalières.

---

## 🧩 User Stories associées

| ID | User Story | Rôle | Critères d’acceptation |
|----|------------|------|-------------------------|
| US-041-01 | En tant qu’utilisateur, je veux interagir vocalement avec le bot pour obtenir des informations ou exécuter des actions. | Utilisateur | Une commande vocale est interprétée et une réponse vocale est donnée. |
| US-041-02 | En tant qu’utilisateur, je veux consulter la liste des tickers disponibles par commande vocale. | Utilisateur | La commande « liste des tickers » renvoie une réponse parlée avec les symboles. |
| US-041-03 | En tant qu’utilisateur, je veux exécuter un achat simulé vocalement pour un ticker donné. | Utilisateur | La commande « exécute achat de XYZ » déclenche une insertion en base. |
| US-041-04 | En tant qu’utilisateur, je veux connaître les meilleurs scores IA par commande vocale. | Utilisateur | La commande « meilleurs scores IA » retourne les 3 tickers avec score élevé. |
| US-041-05 | En tant qu’utilisateur, je veux pouvoir demander n’importe quelle question à l’IA et recevoir une réponse orale. | Utilisateur | Toute autre question est envoyée à GPT et une réponse vocale est donnée. |
| US-041-06 | En tant qu’utilisateur, je veux déclencher la clôture journalière via une commande vocale. | Utilisateur | La commande « ferme la journée » exécute la fonction `cloturer_journee()`. |

---

## 🧠 Modules Python concernés
- `assistant_vocal.py` → cœur du module vocal, boucle d’écoute, traitement, réponse
- `config/config_manager.py` → paramètre `use_voice_assistant`
- `tests/test_assistant_vocal.py` → tests unitaires (commande + DB)

---

## 🔧 Pré-requis techniques

### Fichiers
- `assistant_vocal.py`
- `config/config_manager.py`
- `tests/test_assistant_vocal.py`
- `.env` avec clé `USE_VOICE_ASSISTANT=True`

### Librairies requises
```txt
SpeechRecognition
pyttsx3
pyaudio
```

### Paramètre de configuration
```ini
USE_VOICE_ASSISTANT=True
```

---

## 🧪 Fonctions principales

| Fonction | Rôle | Paramètres | Retour |
|---------|------|------------|--------|
| `lancer_assistant_vocal()` | Lance la boucle continue de l’assistant | `timeout=5` | None |
| `_recognize()` | Interprète un signal vocal via micro | `timeout` | Texte reconnu (str) |
| `interpret_command(text)` | Décode une commande en action + param | `text` | `(action, param)` |
| `handle(text)` | Exécute une action selon l’intention | `text` | Résultat (str) |
| `_ask_openai(text)` | Appelle GPT via l’API | `text` | Réponse (str) |
| `_simulate_buy(ticker)` | Simule un achat dans la base | `ticker` | Résultat vocal |
| `_close_day()` | Déclenche la clôture journalière |  | Résultat vocal |

---

## 🗂️ Base de données

- Table `watchlist` : utilisée pour lister les tickers
- Table `trades_simules` : utilisée pour simuler les achats
- Table `journal_vocal.csv` : log de toutes les interactions vocales (timestamp, input, action, résultat)

---

## 🔄 Flux utilisateur simplifié (mode vocal)

```
Utilisateur → 🎤 → Micro → Reconnaissance → Interprétation → Action → 📣 Réponse vocale + Log CSV
```

---

## ✅ Résultat attendu
- Assistant vocal fonctionnel avec retour vocal
- Commandes simples interprétées et exécutées
- Intégration testée et activable via paramètre de configuration

---

## 📂 Fichiers produits
- `assistant_vocal.py`
- `journal_vocal.csv`
- `.env` (avec `USE_VOICE_ASSISTANT=True`)
- `test_assistant_vocal.py`

---

## 🧪 Tests & Couverture
- Couverture unitaire OK : `tests/test_assistant_vocal.py`
- Reconnaissance vocale testée uniquement si micro disponible
- Résistance aux erreurs (API non disponible, micro absent, etc.)

---


# chapitre_42_agent_autonome

# Chapitre 42 — Agent autonome local d’amélioration IA (Self-Improver Bot)

## Objectif

Mettre en place un agent IA autonome capable d'analyser les performances du bot de trading, d'identifier les faiblesses, de proposer des ajustements aux stratégies, et d'implémenter automatiquement des optimisations en mode local.

## User Stories associées

- **US812** : En tant qu'IA, je veux analyser les trades simulés pour comprendre les erreurs fréquentes.
- **US813** : En tant qu'utilisateur, je veux que l'IA propose automatiquement des améliorations.
- **US814** : En tant qu'IA, je veux ajuster les paramètres dynamiquement selon les tendances du marché.
- **US815** : En tant qu'utilisateur, je veux pouvoir visualiser les suggestions de l'IA avant application.

## Modules Python concernés

- `intelligence/self_improver_agent.py`
- `simulations/analyse_trades.py`
- `tests/test_self_improver_agent.py`

## Prérequis techniques

- Historique des trades dans `trades_simules`
- Scores IA et journaux accessibles
- Dépendance à `scikit-learn`, `joblib`, `pandas`, `numpy`

## Tables de base de données

- `trades_simules(id, ticker, date, resultat, gain, duree, score, pattern_detecte)`
- `recommandations_ia(id, date, type, details, appliquee)`

## Fonctions clés

### `analyser_trades_passes()`

- Rôle : Scanner les trades passés et identifier les récurrences de pertes
- Entrée : Date de départ, limite de profondeur
- Sortie : Liste des faiblesses identifiées

### `proposer_améliorations(faiblesses)`

- Rôle : Utiliser un modèle IA pour suggérer des paramètres ou règles
- Entrée : Faiblesses identifiées
- Sortie : Liste de suggestions précises avec score de confiance

### `appliquer_suggestions(suggestions)`

- Rôle : Appliquer en local les suggestions validées par l'utilisateur
- Entrée : Suggestions filtrées et validées
- Sortie : Mise à jour des fichiers de config ou stratégies

## Variables par défaut

- `MIN_GAIN_CIBLE = 3.0`
- `MAX_LOSS_AUTORISE = -2.0`
- `NOMBRE_TRADES_ANALYSES = 100`
- `AUTO_APPLY = False`

## Exemple de suggestion auto

```json
{
  "type": "ajustement_parametre",
  "details": "Baisser le stop loss de 3% à 2% pour les tickers avec forte volatilité",
  "confiance": 0.91
}
```

## Affichage dans l'interface

- Onglet : "IA Auto-Améliorante"
- Éléments visibles :
  - Liste des recommandations avec score de confiance
  - Bouton "Appliquer"
  - Log de l'amélioration

## Tests

- Simulation sur des trades perdants : l’IA propose un ajustement
- Simulation sur des gains constants : l’IA propose de maintenir la stratégie

## KPI et suivi

- Nombre de recommandations appliquées
- Gain moyen à +N jours après application
- Nombre de modèles IA entrainés automatiquement

## Remarques

- Le module peut être connecté ultérieurement à un moteur de reinforcement learning
- L’objectif est une boucle locale 100% offline de suggestion + validation + application

---


# final_documentation_combined

# 00_intro_watchlistbot

# 📘 Chapitre 00 – Introduction Générale au Projet WatchlistBot V7.03

## 🎯 Objectif du document
Ce chapitre introduit le projet WatchlistBot V7.03, une solution unifiée de **trading algorithmique spécialisé dans les penny stocks à forte volatilité**, conçue pour une utilisation par des traders, analystes IA, développeurs, DBA et architectes techniques.

Il sert de **point d'entrée officiel** pour toute la documentation, avec une vision complète de l’écosystème du bot, les motivations, les rôles impliqués, et les fondements nécessaires pour maintenir ou faire évoluer le projet.

---

## 🧠 Contexte et Motivation
WatchlistBot a été conçu pour répondre aux problématiques suivantes :
- Détection en temps réel d’opportunités sur des titres très volatils (biotech, pharma, small caps US).
- Prise de décision assistée par IA basée sur des indicateurs techniques, fondamentaux, et catalyseurs externes.
- Exécution simulée ou réelle avec journalisation, calculs de PnL et alertes dynamiques.
- Architecture modulaire, adaptée à l’échelle locale ou cloud.

---

## 🔍 Utilisateurs cibles
| Rôle                     | Objectifs clés |
|--------------------------|----------------|
| **Trader / utilisateur**      | Interface simple, rapide, signaux IA, exécution ou simulation |
| **Développeur Python**       | Modules testables, logique claire, code modulaire |
| **Architecte logiciel**      | Structure scalable, traçabilité des flux, IA intégrée |
| **Responsable IA**           | Ajustement des modèles, retrain, analyse de performance |
| **Administrateur BDD**       | Migration, sauvegarde, surveillance des tables SQLite |
| **Testeur / QA**             | Couverture des cas, stratégie de non-régression |

---

## 🧩 Modules techniques clés
Le projet se compose de plusieurs **EPICs** décrits dans la documentation (voir `project_structure.md`). Parmi les modules critiques :

- `intelligence/ai_scorer.py` – Scoring IA multi-paramètres
- `execution/strategie_scalping.py` – Stratégie d’entrée/sortie avec trailing stop
- `simulation/simulate_trade_result.py` – Simulation avec frais réels
- `realtime/pump_detector.py` – Détection en direct de pumps
- `ui/app_unifie_watchlistbot.py` – Interface centralisée Streamlit
- `db/scores.py`, `db/trades.py` – Persistance des scores & journaux de trades
- `fusion/module_fusion_watchlist.py` – Agrégation des sources (manuel, IA, scrapping)

---

## 🛠️ Prérequis techniques
| Élément                 | Détail |
|-------------------------|--------|
| **Python**              | Version 3.8+ (recommandé : 3.10) |
| **Dépendances**         | Listées dans `requirements.txt` (Streamlit, pandas, yfinance, openai...) |
| **Base de données**     | SQLite – fichier `data/trades.db` |
| **API externes**        | Finnhub (clé requise), yfinance, OpenAI (optionnelle pour GPT) |
| **Système de fichiers** | Organisation en modules / sous-dossiers décrits dans `project_structure.md` |

---

## 🗃️ Tables et données principales
| Table SQLite           | Colonnes clés |
|------------------------|----------------|
| `watchlist`            | `symbol`, `source`, `score`, `timestamp` |
| `trades`               | `id`, `symbol`, `price`, `volume`, `type`, `pnl`, `date_exec` |
| `trades_simules`       | `symbol`, `entry`, `exit`, `gain`, `stop_loss`, `comment` |
| `ticks` / `intraday_smart` | `symbol`, `price`, `volume`, `timestamp` |
| `scores`               | `symbol`, `score`, `details`, `timestamp` |
| `news_score`           | `symbol`, `score_news`, `gpt_label`, `text` |

---

## 🧾 User Stories associées
- **US-GEN-001** – En tant qu’utilisateur, je souhaite avoir un point d’entrée unique pour accéder à la logique du bot.
- **US-GEN-002** – En tant que développeur, je veux comprendre l’organisation technique du projet.
- **US-GEN-003** – En tant qu’architecte, je veux pouvoir cartographier tous les modules pour garantir leur évolutivité.
- **US-GEN-004** – En tant qu’administrateur BDD, je veux pouvoir visualiser toutes les tables utilisées et leurs champs.

---

## 🔄 Liens de navigation vers les chapitres suivants
- [31 – Daily Workflow](31_daily_workflow.md)
- [05 – Import Watchlist](05_watchlist_import.md)
- [09 – Analyse IA](09_analyse_ia.md)
- [23 – Daily Closure](23_daily_closure.md)
- [28 – Pump Detector & Trailing Stop](28_pump_detector_trailing_stop.md)

---

## 📌 Notes importantes
- Tous les scripts sont interopérables via `app_unifie_watchlistbot.py`
- Le projet est conçu pour fonctionner **sans dépendance cloud critique**, à l’exception des API publiques (Finnhub, yfinance)
- Les tests unitaires sont disponibles dans `tests/`, avec un coverage partiel pour les modules IA & exécution
- Le système de `meta_ia.json` stocke les pondérations apprises automatiquement par le moteur IA

---

> 📘 **À retenir** : ce chapitre est à lire impérativement avant toute modification de code ou reprise technique du projet.

---


# 05_watchlist_import

# 📘 Chapitre 05 – Import de Watchlist (manuel, fichier, Jaguar, IA)

Ce module permet d'importer, fusionner, filtrer et enrichir une liste de tickers à analyser dans la journée. Il centralise plusieurs sources (manuel, fichier `.txt`, scraping Jaguar, scoring IA) dans une **watchlist unifiée**.

Il constitue le point d’entrée **initial** de toute session de trading IA.

---

## 🎯 Objectifs fonctionnels

- Permettre à l’utilisateur d’ajouter ou d’importer des tickers.
- Scraper automatiquement la watchlist postée par Jaguar sur StockTwits.
- Ajouter dynamiquement les tickers issus de l’IA (`meta_ia.json`).
- Générer une **watchlist fusionnée**, prête à être scorée et analysée.

---

## 📂 Sources de données watchlist

| Source          | Format / Support                | Module impliqué             |
| --------------- | ------------------------------- | --------------------------- |
| Manuel          | Interface utilisateur Streamlit | `tickers_manuels.json`      |
| Fichier externe | `.txt` simple                   | `watchlist_jaguar.txt`      |
| Scraping Jaguar | Texte posté quotidiennement     | `scripts/scraper_jaguar.py` |
| Résultats IA    | Pondérations IA pré-apprises    | `meta_ia.json`              |

---

## 🔧 Fonction de fusion centrale : `fusionner_watchlists(...)`

Localisation : `fusion/module_fusion_watchlist.py`

### Logique simplifiée :

```python
watchlist = set()
watchlist.update(lire_json("tickers_manuels.json"))
watchlist.update(charger_txt("watchlist_jaguar.txt"))
watchlist.update(extraire_tickers_meta("meta_ia.json"))
return list(sorted(watchlist))
```

---

## 🧪 Déclencheurs dans l’interface UI

- **Bouton “Importer fichier Jaguar”** : permet de charger manuellement un fichier `.txt`.
- **Scraping automatique toutes les 15 min** : déclenché en arrière-plan.
- **Ajout manuel** : champ texte + bouton “Ajouter” en Streamlit.

---

## 🧠 Filtres appliqués avant analyse IA

| Filtre           | Valeur par défaut | Raison                       |
| ---------------- | ----------------- | ---------------------------- |
| Prix minimum     | 0.5 \$            | Exclure microcaps illiquides |
| Penny stock ?    | configurable      | Permet d’exclure les < 1\$   |
| Float maximum    | 200M              | Sensibilité au pump          |
| Existence réelle | API Finnhub       | Vérification de validité     |

---

## 🗃️ Données enregistrées

Les tickers fusionnés sont insérés dans :

| Table       | Colonnes                        |
| ----------- | ------------------------------- |
| `watchlist` | `symbol`, `source`, `timestamp` |

> Chaque ligne indique la provenance : `manuel`, `fichier`, `IA`, `Jaguar`, `scraper`, etc.

---

## 🔗 Modules liés

| Module                       | Usage                                           |
| ---------------------------- | ----------------------------------------------- |
| `check_tickers.py`           | Valide que le ticker existe vraiment via API    |
| `app_unifie_watchlistbot.py` | UI Streamlit : boutons d'import, d’ajout manuel |
| `db/watchlist.py`            | Insère les tickers validés                      |
| `ai_scorer.py`               | Analyse la watchlist générée                    |

---

## 📌 User Stories associées

- **US-WL-001** – En tant qu’utilisateur, je veux ajouter manuellement un ticker.
- **US-WL-002** – En tant qu’utilisateur, je veux importer un fichier `.txt` de tickers.
- **US-WL-003** – En tant que bot, je veux scraper automatiquement la watchlist de Jaguar.
- **US-WL-004** – En tant que moteur IA, je veux fusionner toutes les sources et analyser la liste proprement.

---

> ✅ Ce module constitue le socle de départ du processus IA. Il garantit que seuls les tickers valides et intéressants passent à l'étape d’analyse.

---


# 06_simulation_engine

# 📘 Chapitre 06 – Moteur de Simulation (Simulation Engine)

Ce module est au cœur des tests de stratégie et de l’apprentissage IA : il permet de simuler des ordres d’achat et de vente avec gestion des frais, journalisation, et analyse des gains ou pertes. Il s’appuie sur une logique proche de l’exécution réelle tout en conservant une séparation claire (pas d’ordre vers broker).

---

## 🎯 Objectifs du moteur de simulation

- Simuler un achat/vente avec paramètres réels (frais, prix, quantité).
- Tester une stratégie (SL, TP, trailing, etc.).
- Enregistrer les résultats dans la base `trades.db`.
- Servir de feedback pour l’IA (modèle d’apprentissage).

---

## 📁 Modules principaux

| Fichier                    | Rôle                                          |
| -------------------------- | --------------------------------------------- |
| `simulate_trade_result.py` | Simulation principale IA + calculs            |
| `execution_simulee.py`     | Enregistrement SQL dans `trades_simules`      |
| `simulation_achat.py`      | Interface manuelle pour ajout de trade (JSON) |
| `simulation_vente.py`      | Interface manuelle pour vente simulée (JSON)  |

---

## 🧠 Fonction centrale : `executer_trade_simule()`

### Paramètres :

- `ticker`: symbole analysé
- `prix_achat`, `prix_vente`: prix de la simulation
- `quantite`: volume simulé
- `frais`: calculés automatiquement (plateforme Moomoo par défaut)
- `stop_loss`, `take_profit`, `strategie`, `commentaire`

### Logique (extrait simplifié) :

```python
def executer_trade_simule(ticker, prix_achat, prix_vente, quantite):
    frais = max(1.0, 0.005 * quantite)  # frais plateforme Moomoo
    gain = (prix_vente - prix_achat) * quantite - frais
    trade = {
        'symbol': ticker,
        'entry': prix_achat,
        'exit': prix_vente,
        'gain': round(gain, 2),
        'strategy': 'simu_trailing',
        'comment': 'test auto'
    }
    enregistrer_trade_simule(conn, trade)
    return trade
```

---

## 🧮 Modèle de frais utilisé (Moomoo Canada)

| Type de frais                | Montant                                |
| ---------------------------- | -------------------------------------- |
| Commission                   | 0.0049\$/action (min 0.99\$ par ordre) |
| Frais plateforme             | 0.005\$/action (min 1\$, max 1%)       |
| Exemple (1000 actions à 1\$) | ≈ 9.9\$ + 5\$ = 14.9\$ (en simulation) |

Les frais sont configurables dans un fichier `config/frais.json`.

---

## 💾 Table utilisée : `trades_simules`

| Colonne       | Type     | Description                         |
| ------------- | -------- | ----------------------------------- |
| `symbol`      | TEXT     | Ticker simulé                       |
| `entry`       | REAL     | Prix d’achat                        |
| `exit`        | REAL     | Prix de sortie                      |
| `gain`        | REAL     | Résultat net (après frais)          |
| `stop_loss`   | REAL     | Niveau de SL simulé (si applicable) |
| `take_profit` | REAL     | Niveau de TP simulé (si applicable) |
| `strategy`    | TEXT     | Nom de la stratégie testée          |
| `comment`     | TEXT     | Remarque IA ou utilisateur          |
| `timestamp`   | DATETIME | Horodatage du trade                 |

---

## 🔗 Intégration avec autres modules

| Module                       | Usage de la simulation |
| ---------------------------- | ---------------------- |
| `learning_loop.py`           | Apprentissage IA       |
| `ai_backtest.py`             | Validation offline     |
| `app_unifie_watchlistbot.py` | Affichage dans UI      |
| `dashboard.py`               | Résumé des gains/pnls  |

---

## 📌 User Stories associées

- **US-SIMU-001** – En tant que trader, je veux tester une idée avant de passer un ordre réel.
- **US-SIMU-002** – En tant qu’IA, je veux simuler un trade pour apprendre à ajuster mes seuils.
- **US-SIMU-003** – En tant qu’utilisateur, je veux voir mes trades simulés dans l’interface.
- **US-SIMU-004** – En tant que testeur, je veux vérifier que la logique de frais est bien prise en compte.

---

> ✅ Ce moteur permet d'itérer rapidement sur des stratégies en limitant le risque. Il est la base du module de backtest et du renforcement IA.

---


# 07_news_detection

# 📘 Chapitre 07 – Détection de News & Catalyseurs (FDA, IPO, Fusions)

Ce module identifie les catalyseurs externes (news) ayant un impact direct sur le comportement des tickers : annonces FDA, uplisting, IPO, fusions, acquisitions, etc.

Il permet de repérer en amont les titres susceptibles de connaître une forte volatilité intraday.

---

## 🎯 Objectifs fonctionnels

- Récupérer automatiquement les news liées aux tickers de la watchlist.
- Détecter des **mots-clés critiques** dans les titres et descriptions.
- Générer un **score de catalyseur** utilisé par le moteur IA.
- Afficher les événements détectés dans l’interface utilisateur.

---

## 📁 Modules & Fichiers impliqués

| Fichier                          | Rôle                                     |
| -------------------------------- | ---------------------------------------- |
| `news/finnhub_news_collector.py` | Récupération via API Finnhub             |
| `intelligence/news_scoring.py`   | Attribution d’un score `score_news`      |
| `db/news_score.py`               | Insertion dans table `news_score`        |
| `ai_scorer.py`                   | Utilise `score_news` dans le score final |

---

## 🌐 Source de données : API Finnhub

- Endpoint : `https://finnhub.io/api/v1/company-news?symbol={ticker}`
- Requête faite pour chaque ticker de la watchlist
- Fenêtre temporelle : 2 derniers jours (configurable)

---

## 🧠 Détection des catalyseurs

| Mot-clé détecté     | Pondération | Exemples                  |
| ------------------- | ----------- | ------------------------- |
| "FDA", "approval"   | +0.4        | FDA approval, drug review |
| "IPO", "listing"    | +0.3        | IPO announced, uplisting  |
| "merger", "acquire" | +0.3        | M&A, acquisition, fusion  |
| "earnings"          | +0.2        | quarterly report, revenue |
| "offering"          | -0.2        | dilution, shelf offering  |

Le score de catalyseur est **normalisé entre 0 et 1** (`score_news`).

---

## 💾 Table `news_score`

| Colonne      | Type     | Description                    |
| ------------ | -------- | ------------------------------ |
| `symbol`     | TEXT     | Ticker concerné                |
| `score_news` | REAL     | Score basé sur les news        |
| `text`       | TEXT     | Texte de la news (résumé)      |
| `gpt_label`  | TEXT     | Optionnel : validation par GPT |
| `timestamp`  | DATETIME | Date d’analyse                 |

---

## 🔁 Cycle de traitement

1. Lecture des tickers de la `watchlist`
2. Appel API Finnhub pour chaque ticker
3. Parsing des titres et résumés des news
4. Calcul d’un `score_news` entre 0 et 1
5. Enregistrement dans `news_score`
6. Utilisation dans le module `ai_scorer`

---

## 🧪 Exemple de score appliqué dans le scorer IA

```python
if score_news > 0.7:
    score += 20  # Signal fort IA
elif score_news > 0.4:
    score += 10
```

---

## 📌 User Stories associées

- **US-NEWS-001** – En tant que moteur IA, je veux détecter automatiquement les catalyseurs pour ajuster le score d’un ticker.
- **US-NEWS-002** – En tant qu’utilisateur, je veux voir les raisons d’un score élevé basées sur les news.
- **US-NEWS-003** – En tant qu’analyste, je veux savoir si une dilution potentielle est présente.
- **US-NEWS-004** – En tant que développeur, je veux pouvoir configurer la période et les mots-clés utilisés.

---

> ✅ Ce module permet d’anticiper les mouvements liés à l’actualité en enrichissant le score IA de manière transparente et dynamique.

---


# 09_ai_scorer_analysis

# 📘 Chapitre 09 – Analyse IA & Scoring Avancé

Ce chapitre documente en profondeur le module `ai_scorer.py`, chargé de générer un **score global** pour chaque ticker analysé, basé sur des indicateurs techniques, fondamentaux et contextuels. Ce score guide ensuite les décisions de trading.

---

## 🎯 Objectif du module `ai_scorer.py`

- Fusionner plusieurs signaux en un **score global pondéré** (0 à 100).
- Identifier en priorité les tickers à fort potentiel.
- Offrir une base pour les modules de simulation, exécution et apprentissage IA.

---

## ⚙️ Fonctions principales

### `get_rsi(ticker)`

- **But** : détecter les zones de surachat/survente.
- Valeurs typiques : RSI > 70 = risque de retournement (ou continuation si catalyseur).

### `get_ema(ticker, periods=[9, 21])`

- **But** : détecter le croisement de moyennes mobiles.
- Logique : EMA9 > EMA21 = tendance haussière court terme.

### `get_vwap(ticker)`

- **But** : évaluer si le prix actuel est soutenu par le volume.
- Choix : prix > VWAP = confirmation d’un mouvement solide.

### `get_macd(ticker)`

- **But** : détecter des signaux de momentum.
- Signal positif si MACD > 0 et MACD > signal.

### `get_volume(ticker, interval='1m')`

- **But** : confirmer la liquidité et l’intérêt du marché.
- Seuil typique : > 500 000 en 1 min.

### `get_float(ticker)`

- **But** : identifier les low float stocks (< 100M) → forte réactivité au volume.

### `get_catalyseur_score(ticker)`

- **But** : mesurer l'impact des news (FDA, IPO, fusion...).
- Seuil de détection fort : > 0.7

### `get_atr(ticker)`

- **But** : mesurer la volatilité du ticker pour définir des SL/TP dynamiques.

---

## 🧠 Fonction centrale : `_compute_score()`

```python
def _compute_score(ticker):
    rsi = get_rsi(ticker)
    ema = get_ema(ticker, [9, 21])
    vwap = get_vwap(ticker)
    macd, signal = get_macd(ticker)
    volume = get_volume(ticker)
    float_val = get_float(ticker)
    catalyst = get_catalyseur_score(ticker)
    atr = get_atr(ticker)

    score = 0
    if ema[9] > ema[21]: score += 20
    if macd > signal: score += 15
    if rsi > 70: score += 5  # momentum positif
    if volume > 500_000: score += 20
    if float_val < 100_000_000: score += 10
    if catalyst > 0.7: score += 20
    if atr > 0.5: score += 10

    return {
        'symbol': ticker,
        'score': min(score, 100),
        'atr': atr,
        'source': 'WS'
    }
```

> 📌 Tous les scores sont arrondis à 100 max, sauf cas de désactivation IA.

---

## 🧾 Résultat enregistré

| Table `scores` | Description                  |
| -------------- | ---------------------------- |
| `symbol`       | Nom du ticker                |
| `score`        | Score calculé global (0-100) |
| `atr`          | Valeur d'ATR utilisée        |
| `source`       | Source d'analyse (ex: WS)    |
| `timestamp`    | Datetime d’analyse           |

---

## ⚖️ Justification des pondérations

- **EMA** : clé de tendance rapide → 20% poids
- **Volume** : nécessaire pour scalping → 20%
- **Catalyseur** : facteur exogène fort → 20%
- **MACD** : signal de tendance → 15%
- **Float** : sensible aux pumps → 10%
- **ATR** : important pour gestion du risque → 10%
- **RSI** : ajustement secondaire → 5%

Ces poids sont ajustables via `meta_ia.json` ou `config/rules_auto.json`.

---

## 🧬 Interaction avec les autres modules

| Module consommateur                   | Utilité                                           |
| ------------------------------------- | ------------------------------------------------- |
| `execution/strategie_scalping.py`     | Exécute la stratégie sur tickers avec score élevé |
| `simulation/simulate_trade_result.py` | Base de calcul de PnL attendu                     |
| `learning_loop.py`                    | Feedback IA sur la qualité du score               |
| `ui/app_unifie_watchlistbot.py`       | Affichage du score par ticker                     |

---

## 📌 User Stories associées

- **US-SCORE-001** – En tant que moteur IA, je dois produire un score global fiable pour chaque ticker.
- **US-SCORE-002** – En tant que développeur, je souhaite pouvoir comprendre et tester les poids appliqués à chaque signal.
- **US-SCORE-003** – En tant que trader, je veux voir des tickers avec des scores classés pour choisir rapidement les meilleurs.
- **US-SCORE-004** – En tant qu’administrateur, je veux savoir quand un score a été calculé et avec quelles valeurs.

---

> ✅ Ce chapitre est fondamental pour ajuster les performances du bot et interpréter les choix de trading IA.

---


# 12_ai_backtest_engine

# 📘 Chapitre 12 – Moteur de Backtest IA (Backtest Engine)

Ce module permet de rejouer les stratégies IA sur des données historiques pour évaluer leur performance dans le passé. C’est un outil de validation hors-ligne essentiel pour affiner les pondérations, tester les filtres et évaluer la robustesse des signaux IA.

---

## 🎯 Objectifs fonctionnels
- Reproduire le comportement du moteur IA sur une période historique.
- Tester les combinaisons d’indicateurs avec différentes pondérations.
- Générer des métriques globales (PnL, taux de réussite, Sharpe).
- Exporter les résultats pour analyse comparative.

---

## 🧪 Fonction principale : `run_backtest()`

| Fichier                          | Rôle principal                            |
|----------------------------------|--------------------------------------------|
| `backtest/ai_backtest_runner.py` | Lance le backtest sur tous les tickers     |
| `intelligence/ai_scorer.py`      | Utilisé pour recalculer les scores IA      |
| `simulation/simulate_trade_result.py` | Simule les trades sur données historiques |
| `utils/qlib_loader.py`           | Charge les données formatées pour IA       |

---

## 📁 Données utilisées
- Chemin : `qlib_data/daily/{symbol}.csv`
- Format attendu : OHLCV (Open, High, Low, Close, Volume)
- Sources compatibles : Yahoo Finance, Finnhub, données locales

---

## 🧠 Paramètres de simulation
| Paramètre             | Description                           | Valeur par défaut |
|-----------------------|---------------------------------------|-------------------|
| `threshold_score_min` | Score IA minimum pour entrer         | 70                |
| `sl_ratio`            | Stop Loss en %                       | 5%                |
| `tp_ratio`            | Take Profit en %                     | 10%               |
| `atr_multiplier`      | Utilisation de l’ATR pour SL/TP dyn. | 1.5               |

Tous ces paramètres sont configurables dans `config/backtest_config.json`.

---

## 📊 Résultats produits
- Fichier : `backtest_results_{date}.csv`
- Colonnes : `symbol`, `score`, `entry`, `exit`, `gain`, `sl_triggered`, `tp_triggered`, `comment`
- Tableau de synthèse : taux de réussite, PnL total, profit factor, Sharpe ratio

---

## 🔁 Intégration avec apprentissage IA
- Les meilleurs trades identifiés sont transférés vers le `learning_loop.py`
- Permet d’ajuster les pondérations `meta_ia.json`
- Sert aussi à tester les pondérations proposées par le module `ai_perf_maximizer.py`

---

## 📌 User Stories associées
- **US-BACKTEST-001** – En tant qu’analyste, je veux valider que mes stratégies auraient fonctionné dans le passé.
- **US-BACKTEST-002** – En tant qu’IA, je veux analyser les meilleures combinaisons passées pour apprendre.
- **US-BACKTEST-003** – En tant que développeur, je veux lancer un backtest massif sur 2 ans de données.
- **US-BACKTEST-004** – En tant qu’utilisateur, je veux visualiser les résultats dans le tableau de bord IA.

---

> ✅ Ce module permet d’évaluer objectivement la qualité des signaux IA et d’affiner les paramètres de trading avant tout déploiement réel.

---


# 13_ai_learning_loop

# 📘 Chapitre 13 – Apprentissage IA (Learning Loop)

Le module d’apprentissage IA (« learning loop ») permet à WatchlistBot d’ajuster ses décisions à partir des résultats passés (trades simulés et réels), en renforçant les critères ayant conduit à des gains significatifs.

Ce système crée une **amélioration continue** basée sur les performances historiques.

---

## 🎯 Objectifs fonctionnels

- Récupérer les résultats de trades passés.
- Identifier les patterns, combinaisons d’indicateurs ou conditions gagnantes.
- Mettre à jour les pondérations dans `meta_ia.json`.
- Renforcer les scores IA et prioriser les tickers similaires.

---

## 🧠 Principe du cycle d’apprentissage

```mermaid
graph TD
    A[Résultats des trades (simulés + réels)] --> B[Analyse des patterns gagnants]
    B --> C[Mise à jour des poids IA]
    C --> D[Réécriture de meta_ia.json]
    D --> E[Utilisation dans le scoring IA futur]
```

---

## 📁 Modules impliqués

| Fichier                           | Rôle                                       |
| --------------------------------- | ------------------------------------------ |
| `intelligence/learning_loop.py`   | Boucle principale d’apprentissage          |
| `intelligence/meta_ia.py`         | Gestion et écriture des pondérations       |
| `simulation/execution_simulee.py` | Fournit les données issues des simulations |
| `db/trades.py`                    | Récupération des trades réels              |

---

## 📄 Fichier cible : `meta_ia.json`

Contient les pondérations par indicateur ou paramètre :

```json
{
  "ema_cross_weight": 20,
  "macd_weight": 15,
  "volume_weight": 20,
  "float_weight": 10,
  "news_score_weight": 20,
  "rsi_weight": 5,
  "atr_weight": 10
}
```

---

## 🔎 Données analysées (features)

| Source           | Champ                   | Utilisation dans IA |
| ---------------- | ----------------------- | ------------------- |
| `trades_simules` | `gain`, `entry`, `exit` | Évalue la stratégie |
| `scores`         | `score`, `details`      | Corrèle score/gain  |
| `watchlist`      | `source`, `symbol`      | Suit la provenance  |

---

## 🔁 Méthode de renforcement

- Les stratégies gagnantes (> +5%) sont priorisées.
- Les indicateurs présents dans ces stratégies voient leur poids augmenté.
- Les stratégies perdantes réduisent le poids de certains facteurs.
- Le fichier `meta_ia.json` est régénéré à chaque boucle (quotidienne).

Extrait de code :

```python
if gain > 5.0:
    meta_ia['volume_weight'] += 1
else:
    meta_ia['volume_weight'] -= 1
```

---

## 🛡️ Sécurité et contrôle

- Les pondérations sont plafonnées entre 0 et 30.
- Un backup quotidien est sauvegardé dans `meta_ia_backup/{date}.json`
- Le module ne s’exécute que si la base contient > 20 trades.

---

## 📌 User Stories associées

- **US-LEARN-001** – En tant que moteur IA, je veux apprendre des trades passés pour ajuster mes critères.
- **US-LEARN-002** – En tant qu’administrateur, je veux voir comment les poids sont mis à jour.
- **US-LEARN-003** – En tant qu’utilisateur, je veux que le système devienne plus intelligent avec le temps.
- **US-LEARN-004** – En tant que développeur, je veux pouvoir ajuster manuellement les pondérations si besoin.

---

> ✅ Ce module rend le système adaptatif, capable d’évoluer au fil du temps pour détecter les meilleures configurations gagnantes.

---


# 14_meta_ia_config

# 📘 Chapitre 14 – Configuration IA Dynamique (`meta_ia.json`)

Ce module permet de **piloter dynamiquement le comportement du moteur IA** à partir d’un fichier centralisé `meta_ia.json`, contenant les pondérations et paramètres qui influencent le score attribué aux tickers.

C’est un mécanisme de configuration intelligent, mis à jour automatiquement par le moteur d’apprentissage, ou modifiable manuellement par un administrateur IA.

---

## 🎯 Objectifs fonctionnels

- Centraliser tous les **poids utilisés dans le scoring IA**.
- Permettre une mise à jour dynamique après apprentissage.
- Assurer une **traçabilité et auditabilité** des versions.
- Offrir un **point de tuning manuel** pour les analystes avancés.

---

## 📁 Fichier : `meta_ia.json`

Structure typique :

```json
{
  "ema_cross_weight": 20,
  "macd_weight": 15,
  "volume_weight": 20,
  "float_weight": 10,
  "news_score_weight": 20,
  "rsi_weight": 5,
  "atr_weight": 10
}
```

> Chaque clé représente un **indicateur IA**, chaque valeur un **poids entre 0 et 30**.

---

## 🧠 Modules consommateurs

| Module                       | Utilisation                                          |
| ---------------------------- | ---------------------------------------------------- |
| `ai_scorer.py`               | Application des pondérations dans `_compute_score()` |
| `learning_loop.py`           | Met à jour les pondérations en fonction des trades   |
| `meta_ia.py`                 | Lecture/écriture avec validation JSON                |
| `dashboard_apprentissage.py` | Affichage graphique des pondérations actuelles       |

---

## 🔁 Cycle de mise à jour automatique

1. Exécution d’un batch d’analyse ou d’un apprentissage.
2. Calcul de performance sur trades passés.
3. Pondérations ajustées (+/-) selon stratégie gagnante.
4. Écriture dans `meta_ia.json`
5. Sauvegarde backup dans `meta_ia_backup/YYYY-MM-DD.json`

---

## 🔒 Contrôles de sécurité

- **Validation de structure JSON** (types, bornes)
- **Limites de pondération** : entre 0 et 30 par défaut
- **Backup automatique** journalier
- **Verrouillage manuel** possible via clé `"editable": false`

---

## ⚙️ Exemple de code d’application dans le scorer

```python
weights = charger_meta_ia()
score = 0
if ema_cross: score += weights['ema_cross_weight']
if macd > signal: score += weights['macd_weight']
```

---

## 📌 User Stories associées

- **US-METAIA-001** – En tant qu’IA, je veux utiliser des poids optimisés pour noter les tickers.
- **US-METAIA-002** – En tant qu’analyste IA, je veux ajuster manuellement les pondérations si nécessaire.
- **US-METAIA-003** – En tant qu’administrateur, je veux sauvegarder un historique des changements.
- **US-METAIA-004** – En tant qu’utilisateur, je veux visualiser et comprendre les paramètres IA utilisés.

---

> ✅ Ce système rend le moteur IA personnalisable, traçable et optimisable sans modifier le code source.

---


# 15_ai_performance_maximizer (1)

# 📘 Chapitre 15 – Optimiseur de Performance IA (AI Performance Maximizer)

Le module **AI Performance Maximizer** est conçu pour tester automatiquement **des combinaisons alternatives de pondérations IA**, évaluer leur impact sur les performances simulées, et proposer des configurations optimisées.

Il complète la boucle d’apprentissage par une **approche d’optimisation proactive**.

---

## 🎯 Objectifs fonctionnels

- Générer des variantes de `meta_ia.json` (modification des pondérations).
- Exécuter des backtests sur chaque configuration générée.
- Évaluer la performance cumulée (PnL, taux de réussite, drawdown).
- Identifier et proposer la meilleure combinaison pondérée.

---

## 📁 Modules impliqués

| Fichier                             | Rôle                                         |
| ----------------------------------- | -------------------------------------------- |
| `intelligence/ai_perf_maximizer.py` | Génération et test des configurations IA     |
| `backtest/ai_backtest_runner.py`    | Lance les tests de validation                |
| `meta_ia.py`                        | Gère les fichiers `meta_ia.json` alternatifs |

---

## 🔧 Méthodologie d’optimisation

1. Charger la configuration actuelle `meta_ia.json`.
2. Générer X variantes : pondérations modifiées légèrement.
3. Pour chaque configuration :
   - Appliquer dans `ai_scorer.py`
   - Lancer `run_backtest()`
   - Enregistrer résultats dans `perf_logs.csv`
4. Comparer les configurations selon :
   - **PnL total**
   - **Taux de réussite (%)**
   - **Ratio gain/perte**
   - **Sharpe ratio**
5. Afficher la meilleure configuration et sa performance.

---

## 🧪 Exemple de variation générée

```json
{
  "ema_cross_weight": 22,
  "macd_weight": 14,
  "volume_weight": 18,
  "float_weight": 12,
  "news_score_weight": 21,
  "rsi_weight": 5,
  "atr_weight": 8
}
```

---

## 📊 Résultats stockés dans `perf_logs.csv`

| config\_id | ema | macd | pnl\_total | winrate | sharpe | path                     |
| ---------- | --- | ---- | ---------- | ------- | ------ | ------------------------ |
| 001        | 22  | 14   | 12,400\$   | 63%     | 1.35   | meta\_ia\_test\_001.json |
| 002        | 18  | 20   | 10,800\$   | 59%     | 1.10   | meta\_ia\_test\_002.json |

---

## 🔁 Intégration avec UI et apprentissage

- Les meilleures pondérations peuvent être **proposées à l’utilisateur dans l’interface**.
- Une version validée peut remplacer `meta_ia.json` manuellement ou automatiquement.

---

## 📌 User Stories associées

- **US-MAXIA-001** – En tant qu’IA, je veux tester plusieurs configurations pour maximiser ma rentabilité.
- **US-MAXIA-002** – En tant qu’utilisateur, je veux être informé si une meilleure combinaison a été trouvée.
- **US-MAXIA-003** – En tant qu’analyste IA, je veux auditer les essais passés et comprendre les écarts.
- **US-MAXIA-004** – En tant que développeur, je veux relancer l’optimiseur de manière batch ou planifiée.

---

> ✅ Ce module permet à l’IA de découvrir de nouvelles combinaisons gagnantes et de renforcer sa rentabilité sans supervision constante.

---


# 16_execution_scalping_strategy

# 📘 Chapitre 16/17 – Exécution Réelle & Stratégie Scalping

Ce module regroupe la **logique d’entrée en position réelle ou simulée** en fonction du score, des indicateurs techniques et de la fenêtre de volatilité identifiée.

La stratégie de scalping vise à profiter rapidement des mouvements sur des titres volatils à float faible, souvent liés à des catalyseurs (FDA, news, IPO, etc.).

---

## 🎯 Objectifs de la stratégie

- Entrer uniquement sur les opportunités validées par l’IA et les indicateurs techniques.
- Choisir le bon moment via un **breakout** ou un **pullback**.
- Calculer dynamiquement les niveaux de **Stop Loss (SL)**, **Take Profit (TP)** et **Trailing Stop (TS)**.
- Exécuter l’ordre (ou le simuler), puis le journaliser automatiquement.

---

## 📁 Modules concernés

| Fichier                           | Rôle                            |
| --------------------------------- | ------------------------------- |
| `execution/strategie_scalping.py` | Logique principale d’exécution  |
| `utils/order_executor.py`         | Envoi de l’ordre (réel ou mock) |
| `db/trades.py`                    | Enregistrement des ordres       |
| `notifications/telegram_bot.py`   | Alerte en temps réel            |

---

## ⚙️ Fonction centrale : `executer_strategie_scalping(ticker)`

### Logique complète :

```python
def executer_strategie_scalping(ticker):
    score = _compute_score(ticker)
    if score['score'] < 70:
        return {'status': 'ignored'}

    price = get_last_price(ticker)
    atr = score['atr']

    if enter_breakout(ticker, price, atr):
        ordre = executer_ordre_reel(ticker, price, atr)
        enregistrer_trade_auto(ticker, ordre)
        envoyer_alerte_ia(ticker, ordre)
        return {'ordre': ordre}
    return {'status': 'no_entry'}
```

---

## 🧠 Conditions d’entrée

| Type d’entrée               | Conditions                                 |
| --------------------------- | ------------------------------------------ |
| `enter_breakout(t, p, atr)` | Nouvelle cassure du plus haut avec support |
| `enter_pullback(t, p, atr)` | Rebond sur support après forte hausse      |

Ces fonctions analysent la bougie actuelle via `yfinance.download(...)` et les données `intraday_smart`.

---

## 📏 Gestion du risque (TP/SL/TS)

| Élément            | Calcul typique          | Explication                |
| ------------------ | ----------------------- | -------------------------- |
| SL (Stop Loss)     | `price - atr`           | Base sur volatilité locale |
| TP (Take Profit)   | `price + atr * 2`       | Objectif standard 2:1      |
| TS (Trailing Stop) | Suivi du plus haut - X% | Verrouille les gains       |

Le **TrailingManager** peut être utilisé pour ajuster dynamiquement la sortie.

```python
TM = TrailingManager(entry_price=2.0, stop_loss=1.9)
for p in [2.05, 2.15, 2.10]:
    TM.update(p)
```

---

## 🔁 Journalisation des ordres

Appel de : `enregistrer_trade_auto(ticker, ordre)`

| Table `trades` | Colonnes principales |
| -------------- | -------------------- |
| `symbol`       | Ticker               |
| `price`        | Prix d’entrée        |
| `volume`       | Volume               |
| `type`         | Réel / Simulé        |
| `pnl`          | Gain ou perte        |
| `timestamp`    | Date                 |

---

## 🔔 Notifications en temps réel

- Via `envoyer_alerte_ia(ticker, ordre)`
- Format : `📈 Achat exécuté AAA à 2.12$ - TP: 2.40$ / SL: 1.95$`

---

## 📌 User Stories associées

- **US-EXEC-001** – En tant que bot, je veux exécuter un trade quand le score et les conditions sont réunis.
- **US-EXEC-002** – En tant qu’utilisateur, je veux voir le résultat d’un ordre directement dans l’interface.
- **US-EXEC-003** – En tant qu’IA, je veux enregistrer chaque trade avec ses paramètres pour apprendre.
- **US-EXEC-004** – En tant qu’analyste, je veux être notifié quand un trade a lieu automatiquement.

---

> ✅ Ce module permet une exécution encadrée et optimisée des ordres IA. Il repose sur une logique robuste avec journalisation et alerte automatique.

---


# 16_stop_loss_manager

# 📘 Chapitre 16 – Stop Loss Manager & Sécurité Automatique

Le module **Stop Loss Manager** assure une gestion sécurisée des ordres en activant automatiquement des **mécanismes de protection** comme :

- stop loss fixe,
- trailing stop dynamique basé sur ATR,
- passage au point mort après un certain gain (breakeven),
- sécurisation partielle des profits.

C’est une brique essentielle pour garantir une protection constante du capital en trading algorithmique.

---

## 🎯 Objectifs fonctionnels

- Protéger les ordres ouverts automatiquement.
- Appliquer des règles adaptatives selon la volatilité (ATR).
- Encadrer les pertes et sécuriser progressivement les gains.
- Être réutilisable pour les ordres réels et les simulations.

---

## 📁 Modules concernés

| Fichier                            | Rôle                                        |
| ---------------------------------- | ------------------------------------------- |
| `execution/stop_manager.py`        | Gestion des seuils dynamiques               |
| `execution/strategie_scalping.py`  | Intégration dans les stratégies de scalping |
| `simulation/simulateur_trading.py` | Application dans le moteur de simulation    |

---

## ⚙️ Logique interne – TrailingManager

```python
class TrailingManager:
    def __init__(self, entry_price, stop_loss):
        self.entry = entry_price
        self.sl = stop_loss

    def update(self, current_price):
        if current_price >= self.entry * 1.02:
            self.sl = max(self.sl, self.entry)  # breakeven
        if current_price >= self.entry * 1.05:
            self.sl = max(self.sl, self.entry * 1.03)  # sécurisation
        return self.sl
```

> Le `TrailingManager` adapte le stop loss selon la progression du prix.

---

## 📊 Paramètres IA utilisés

- **ATR (Average True Range)** : mesure la volatilité → adapte la distance du stop.
- **Breakout détecté** : permet d'appliquer un trailing plus agressif.
- **Momentum** : peut désactiver le stop si le flux est trop instable.

---

## 📌 Valeurs typiques recommandées

| Indicateur | Utilisation                      | Valeur par défaut |
| ---------- | -------------------------------- | ----------------- |
| ATR        | Distance initiale du stop        | 1.5 x ATR         |
| Breakeven  | Seuil de passage au point mort   | +2%               |
| Secured TP | Sécurisation partielle des gains | +5% → SL à +3%    |

---

## 🔐 Sécurité & Robustesse

- Trailing toujours déclenché après passage d’un gain seuil.
- Réévaluation en temps réel toutes les X secondes.
- Historique des mises à jour stocké en mémoire ou journalisé.
- Peut fonctionner sans UI, en tâche de fond.

---

## 📌 User Stories associées

- **US-STPLS-001** – En tant qu’IA, je veux ajuster dynamiquement mon stop loss selon la volatilité.
- **US-STPLS-002** – En tant qu’utilisateur, je veux visualiser les niveaux de protection en cours.
- **US-STPLS-003** – En tant que bot, je veux passer à breakeven après un gain > 2%.
- **US-STPLS-004** – En tant que développeur, je veux pouvoir réutiliser le `TrailingManager` dans tous les modules.

---

> ✅ Ce module renforce la sécurité des stratégies et réduit l’exposition aux retournements brutaux.

---


# 17_ui_streamlit_interface

# 📘 Chapitre 17 – Interface Utilisateur (Streamlit App)

L’interface utilisateur développée avec **Streamlit** permet une interaction directe, claire et interactive avec l’ensemble des fonctionnalités du bot WatchlistBot V7.03. Elle est pensée pour :

- les traders (prise de décision rapide),
- les analystes IA (analyse des scores et signaux),
- les développeurs (debug visuel, affichage des logs),
- les chefs de projet (vue roadmap et user stories).

---

## 🎯 Objectifs fonctionnels de l’UI

- Afficher les tickers détectés en temps réel.
- Permettre le lancement et l’arrêt des analyses.
- Visualiser les graphiques et indicateurs clés.
- Exécuter des ordres simulés ou réels.
- Gérer les watchlists (manuel, IA, Jaguar).
- Afficher les logs, KPIs, scores IA et historiques.
- Naviguer entre modules via un menu clair.

---

## 📁 Fichiers Streamlit

| Fichier                         | Rôle                                         |
| ------------------------------- | -------------------------------------------- |
| `ui/app_unifie_watchlistbot.py` | Application principale, menu global          |
| `ui/pages/heatmap_realtime.py`  | Affichage de la heatmap des scores IA        |
| `ui/pages/simulation.py`        | Lancement d’ordres simulés + suivi           |
| `ui/pages/roadmap_tracker.py`   | Suivi des user stories et progression projet |
| `ui/pages/watchlist_manager.py` | Gestion des watchlists                       |

---

## 🧭 Structure du Menu UI

```txt
📊 Analyse & Watchlist
  └─ Lancer analyse 🔎
  └─ Arrêter analyse ✋
  └─ Résultats IA (heatmap, tableaux)

📈 Simulation & Ordres
  └─ Passer un ordre simulé ✅
  └─ Suivre les résultats 📉

🧠 IA & Apprentissage
  └─ Meta IA (paramètres dynamiques)
  └─ Résultats apprentissage
  └─ Optimiseur IA

📋 Roadmap & Stories
  └─ Suivi des tâches
  └─ Affichage par EPIC / Sprint

⚙️ Configuration
  └─ Paramètres utilisateur, Penny Stocks, Alerts
```

---

## 🧩 Composants visuels principaux

- **Boutons interactifs** : démarrage, stop, exécution d’ordres
- **Graphiques dynamiques** : avec `plotly`, `matplotlib`, `yfinance`
- **Tableaux filtrables** : watchlist IA, résultats simulation, journal
- **Checkboxes & sliders** : filtres IA, penny stocks, seuils de volume
- **Panneaux dépliables** : détails d’un ticker, debug, logs, trade info

---

## 🔄 Rafraîchissement temps réel

- Utilisation de `st.experimental_rerun()` pour forcer les mises à jour.
- Les heatmaps et graphiques sont recalculés à intervalle régulier (15 min).
- Support d’un **mode auto** pour les scans, et d’un **mode manuel** pour les tests ou analyses ponctuelles.

---

## 👥 Rôles utilisateurs cibles

| Rôle           | Utilisation UI                              |
| -------------- | ------------------------------------------- |
| Trader         | Watchlist, ordres, signaux et exécution     |
| Analyste IA    | Analyse des résultats IA, tuning des poids  |
| Architecte     | Navigation dans les modules, debug, journal |
| Chef de projet | Suivi roadmap, tests, EPICs et user stories |

---

## 📌 User Stories associées

- **US-UI-001** – En tant qu’utilisateur, je veux pouvoir lancer l’analyse en un clic.
- **US-UI-002** – En tant qu’analyste, je veux voir les résultats IA par score dans une heatmap.
- **US-UI-003** – En tant que trader, je veux exécuter un ordre simulé en 1 clic.
- **US-UI-004** – En tant qu’utilisateur, je veux basculer entre les watchlists (IA, manuel, Jaguar).
- **US-UI-005** – En tant que chef de projet, je veux suivre l’avancement du backlog en UI.
- **US-UI-006** – En tant que dev, je veux voir les logs et le debug dans des sections claires.

---

> ✅ Cette interface rend le bot utilisable, débogable, présentable et pilotable, même sans expertise Python.

---


# 18_journalisation_trades_db

# 📘 Chapitre 18 – Journalisation des ordres (`trades.db`)

La base de données `trades.db` est au cœur du suivi historique, de la simulation, et de l’apprentissage IA. Chaque ordre exécuté (réel ou simulé) y est enregistré avec précision, permettant :

- la traçabilité complète,
- la rétro-analyse des stratégies,
- l'entraînement du module IA,
- le calcul des statistiques journalières,
- la détection automatique des anomalies ou des modèles gagnants.

---

## 🗂️ Structure de la base `trades.db`

### 📌 Table `simulated_trades`

| Colonne           | Type    | Description                                                |
| ----------------- | ------- | ---------------------------------------------------------- |
| `id`              | INTEGER | Identifiant unique de la ligne (clé primaire)              |
| `symbol`          | TEXT    | Ticker de l’action                                         |
| `entry_price`     | REAL    | Prix d’achat                                               |
| `exit_price`      | REAL    | Prix de vente (si clôturé)                                 |
| `quantity`        | INTEGER | Nombre d’actions tradées                                   |
| `fees`            | REAL    | Frais estimés ou calculés (Moomoo Canada, par défaut)      |
| `gain_pct`        | REAL    | Gain/perte en pourcentage                                  |
| `timestamp_entry` | TEXT    | Horodatage de l’achat                                      |
| `timestamp_exit`  | TEXT    | Horodatage de la vente (si applicable)                     |
| `strategy`        | TEXT    | Stratégie utilisée (e.g. `breakout`, `pullback`, `manual`) |
| `score`           | INTEGER | Score IA au moment de l’achat                              |
| `source`          | TEXT    | Source du signal (IA, manuel, news, Jaguar...)             |
| `stop_loss`       | REAL    | Valeur du SL à l’achat                                     |
| `take_profit`     | REAL    | Valeur du TP initial                                       |
| `atr`             | REAL    | Valeur de l’ATR lors de l’entrée                           |
| `status`          | TEXT    | État (`open`, `closed`, `cancelled`, `error`)              |
| `comment`         | TEXT    | Notes ou raison spécifique liée à l’ordre                  |

---

## ⚙️ Fichier Python responsable : `journal.py`

```python
import sqlite3

def enregistrer_trade_auto(trade_data):
    conn = sqlite3.connect("trades.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO simulated_trades (
            symbol, entry_price, quantity, fees, timestamp_entry,
            strategy, score, source, stop_loss, take_profit, atr, status, comment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade_data["symbol"], trade_data["entry_price"], trade_data["quantity"],
        trade_data["fees"], trade_data["timestamp_entry"], trade_data["strategy"],
        trade_data["score"], trade_data["source"], trade_data["stop_loss"],
        trade_data["take_profit"], trade_data["atr"], "open", trade_data.get("comment", "")
    ))
    conn.commit()
    conn.close()
```

---

## ✅ Pourquoi ce design ?

- **Simplicité SQLite** : légère, sans serveur externe, idéale pour local/dev.
- **Historique structuré** : tous les ordres sont consultables.
- **Compatible apprentissage IA** : le module `learn_from_trades.py` s’appuie sur ces données.
- **Filtrable pour le dashboard** : affichage des PnL, performance journalière, etc.

---

## 📌 User Stories associées

- **US-JOURNAL-001** – En tant qu’utilisateur, je veux que chaque ordre soit automatiquement enregistré.
- **US-JOURNAL-002** – En tant qu’analyste, je veux pouvoir visualiser l’historique des trades.
- **US-JOURNAL-003** – En tant qu’IA, je veux pouvoir utiliser ces données pour améliorer les prédictions.
- **US-JOURNAL-004** – En tant que chef de projet, je veux que les erreurs ou statuts soient traçables.

---

## 🔍 À noter pour la maintenance

- Toujours vérifier que la table existe avant d’écrire.
- Prévoir une routine d’archivage pour éviter les surcharges.
- Ajouter un test automatique pour valider l’intégrité des lignes.

> Cette journalisation est un **pilier de l’auditabilité** et du **renforcement IA**. Elle permet d’analyser le comportement réel vs théorique du bot.

---


# 19_moteur_ia_learn_trades

# 📘 Chapitre 19 – Moteur IA d’apprentissage à partir des trades (`learn_from_trades.py`)

Le fichier `learn_from_trades.py` est un module central du **mécanisme adaptatif** du bot. Il analyse tous les trades enregistrés dans `trades.db` pour en tirer des **enseignements**, ajuster le **poids des indicateurs**, et recalibrer automatiquement la stratégie IA en fonction des résultats passés.

---

## 🎯 Objectifs du moteur d'apprentissage

- Identifier les patterns gagnants/perdants.
- Comparer les gains estimés vs. réels (écarts d’exécution).
- Réajuster les formules de score IA.
- Sélectionner les meilleurs paramètres d’entrée (entry price, SL, TP).
- Générer un fichier `meta_ia.json` mis à jour automatiquement.

---

## ⚙️ Fichier Python : `learn_from_trades.py`

```python
import sqlite3
import json
import numpy as np

PARAMS_FILE = "intelligence/meta_ia.json"

# Valeurs initiales par défaut si aucun apprentissage n’a encore été fait
def default_params():
    return {
        "rsi_weight": 1.0,
        "ema_weight": 1.0,
        "vwap_weight": 1.0,
        "volume_weight": 1.0,
        "catalyst_weight": 1.0,
        "min_gain_threshold": 3.0  # % minimal pour trade considéré comme gagnant
    }

def learn_from_trades():
    conn = sqlite3.connect("trades.db")
    df = pd.read_sql("SELECT * FROM simulated_trades WHERE status = 'closed'", conn)
    conn.close()

    if df.empty:
        return default_params()

    successful = df[df['gain_pct'] >= 3.0]
    failed = df[df['gain_pct'] < 0.0]

    # Exemple de pondération simple
    win_rate = len(successful) / len(df)
    updated_params = default_params()

    updated_params["rsi_weight"] = np.clip(win_rate * 2.5, 0.5, 3.0)
    updated_params["volume_weight"] = np.clip((len(successful)/max(1, len(failed))) * 1.2, 0.5, 3.0)
    updated_params["min_gain_threshold"] = max(2.0, df['gain_pct'].mean())

    with open(PARAMS_FILE, "w") as f:
        json.dump(updated_params, f, indent=4)

    return updated_params
```

---

## 🔁 Fichier généré : `meta_ia.json`

```json
{
    "rsi_weight": 2.4,
    "ema_weight": 1.0,
    "vwap_weight": 1.0,
    "volume_weight": 1.8,
    "catalyst_weight": 1.0,
    "min_gain_threshold": 3.5
}
```

Ce fichier est lu automatiquement par le module de scoring IA. Il permet au système de s’améliorer **en continu**.

---

## 📌 User Stories associées

- **US-LEARN-001** – En tant qu’IA, je veux ajuster les poids d’indicateurs en fonction des performances passées.
- **US-LEARN-002** – En tant qu’utilisateur, je veux que les poids soient sauvegardés dans un fichier exploitable.
- **US-LEARN-003** – En tant que bot, je veux utiliser ce fichier pour influencer le score au prochain trade.
- **US-LEARN-004** – En tant qu’architecte IA, je veux auditer les impacts des changements de paramètres.

---

## 📊 Variables apprises & logiques

| Variable             | Rôle                                                 | Appris depuis             |
| -------------------- | ---------------------------------------------------- | ------------------------- |
| `rsi_weight`         | Pondère l’importance du RSI dans le score            | Ratio succès trades RSI   |
| `volume_weight`      | Pondère l’impact du volume (ex: > 1M = bon signal)   | Ratio volume dans trades  |
| `min_gain_threshold` | Seuil minimal de gain attendu pour considérer succès | Moyenne des meilleurs PnL |

---

## 🔐 Sécurité & robustesse

- Vérification de l’existence de `trades.db` et `meta_ia.json`.
- Protection contre les divisions par zéro.
- Utilisation de `clip` pour encadrer les poids (anti-régression).

> Ce module rend le bot **vivant**, capable d’apprendre de ses erreurs comme de ses réussites. Chaque jour, il devient plus efficace.

---


# 20_watchlists_enrichies

# 📘 Chapitre 20 – Watchlists enrichies : Manuel, IA et Jaguar

Le système WatchlistBot génère une **liste intelligente de tickers à surveiller** à partir de **trois sources principales** :

- **Liste manuelle** (`tickers_manuels.json`),
- **Liste IA** (`meta_ia.json`, résultats de scoring),
- **Scraping Jaguar** (données temps réel de sentiment et de volume).

L’objectif est de produire une **watchlist unifiée**, triée par score et enrichie d’indicateurs clés, pour optimiser la prise de décision du trader ou du bot.

---

## 🧩 Fichiers et formats

### `tickers_manuels.json`

Ajout manuel des tickers par l’utilisateur via l’interface Streamlit.

```json
{
  "tickers": [
    { "symbol": "GNS", "provenance": "manuel", "ajout": "2024-06-20" },
    { "symbol": "APDN", "provenance": "manuel", "ajout": "2024-06-20" }
  ]
}
```

### `meta_ia.json`

Liste générée automatiquement par le moteur IA après analyse des patterns historiques + scorings des indicateurs.

```json
[
  { "symbol": "TTOO", "score": 94, "provenance": "IA", "catalyseur": true },
  { "symbol": "TOPS", "score": 91, "provenance": "IA", "catalyseur": false }
]
```

### Fichier `tickers_jaguar.json` (scraping)

Contient les tickers détectés via le scraping Jaguar (sentiment, volume anormal, activité forum).

```json
[
  { "symbol": "AVTX", "score": 88, "provenance": "jaguar", "volume": 1500000 },
  { "symbol": "FNHC", "score": 86, "provenance": "jaguar" }
]
```

---

## 🧠 Logique de fusion et filtrage : `watchlist_manager.py`

1. Charger les trois fichiers.
2. Fusionner en une seule liste (en supprimant les doublons).
3. Appliquer les règles de filtrage :
   - Exclure les penny stocks < \$1 (optionnel selon UI).
   - Score minimal (ex: 60).
   - Exclure tickers invalides ou sans données récentes.
4. Trier la liste finale par `score` décroissant.

```python
def generer_watchlist_unifiee():
    tickers = charger_tous_les_tickers()
    tickers = [t for t in tickers if t['score'] >= 60]
    tickers = filtrer_tickers_invalides(tickers)
    tickers_uniques = fusionner_et_supprimer_doublons(tickers)
    return sorted(tickers_uniques, key=lambda x: x['score'], reverse=True)
```

---

## 🔎 Détail des champs standardisés par ticker

| Champ        | Description                                |
| ------------ | ------------------------------------------ |
| `symbol`     | Ticker du titre                            |
| `score`      | Score calculé par IA ou scraping           |
| `provenance` | Source (manuel, IA, jaguar, news, scanner) |
| `catalyseur` | Si vrai, événement comme FDA, IPO, etc.    |
| `ajout`      | Date d’ajout à la watchlist                |
| `volume`     | Volume échangé (si disponible)             |

---

## 📌 User Stories associées

- **US-WATCHLIST-001** – En tant qu’utilisateur, je veux ajouter un ticker manuellement à la watchlist.
- **US-WATCHLIST-002** – En tant que bot, je veux fusionner les tickers IA, Jaguar et manuels dans une liste unique.
- **US-WATCHLIST-003** – En tant qu’IA, je veux filtrer les tickers invalides ou trop faibles.
- **US-WATCHLIST-004** – En tant qu’interface UI, je veux afficher la provenance, le score et le graphique de chaque ticker.
- **US-WATCHLIST-005** – En tant qu’utilisateur, je veux voir les tickers triés par pertinence (score).

---

## 📂 Modules Python concernés

- `utils_watchlist.py` → chargement/fusion
- `check_tickers.py` → validation ticker avec Finnhub
- `dashboard.py` → affichage final des tickers
- `tickers_manuels.json` → stockage côté utilisateur
- `meta_ia.json` → résultats IA
- `tickers_jaguar.json` → scraping dynamique

---

## 🧪 Cas de test clés

| Cas de test                           | Attendu                                       |
| ------------------------------------- | --------------------------------------------- |
| Ajout manuel d’un ticker              | Sauvegardé et visible dans la liste           |
| Ticker présent dans plusieurs sources | Fusionné, provenance prioritaire selon règles |
| Score < 60                            | Exclu sauf en mode debug                      |
| Ticker sans données récentes          | Exclu                                         |

---

## 📊 Table `tickers_enrichis` (base de données optionnelle future)

| Colonne        | Type    | Description                 |
| -------------- | ------- | --------------------------- |
| `symbol`       | TEXT    | Code du ticker              |
| `score`        | INTEGER | Score calculé               |
| `source`       | TEXT    | manuel / jaguar / IA / news |
| `added_on`     | TEXT    | Date d’intégration          |
| `has_catalyst` | BOOLEAN | Présence d’un catalyseur    |
| `volume`       | INTEGER | Volume au moment du scan    |

---

> Cette logique garantit que chaque matin, le bot dispose d’une watchlist **triée, pertinente et actualisée automatiquement**, combinant la connaissance humaine, l’IA et le sentiment de marché.

---


# 21_pre_market_post_market_scanner

# 📘 Chapitre 21 – Scanner Pré-Market & Post-Market Automatique

Ce module permet de **scanner automatiquement les marchés** en dehors des heures d'ouverture (entre 16h00 et 9h30) afin de détecter les tickers potentiellement explosifs pour le lendemain.

Il est **essentiel pour les penny stocks biotech/pharma** avec news ou catalyseurs récents.

---

## 🕐 Période de scan

- **Post-Market** : 16h00 à 00h00
- **Pre-Market** : 05h00 à 09h30

Le bot exécute un **scan automatique toutes les 15 minutes** pendant ces plages horaires.

---

## 🧪 Critères de détection

Un ticker est retenu s’il répond à **tous** les critères suivants :

| Critère                  | Valeur minimale           | Source           |
| ------------------------ | ------------------------- | ---------------- |
| Pourcentage de hausse    | > +50 %                   | Finnhub          |
| Volume                   | > 500 000 actions         | Finnhub / Jaguar |
| Float                    | < 200 millions d’actions  | Finnhub          |
| Anomalie carnet d’ordres | Oui (via scraping)        | Jaguar / forums  |
| Catalyseur actif         | IPO, FDA, SPAC, Fusion... | News Finnhub     |

---

## 📂 Fichiers et scripts

- `postmarket_scanner.py` → exécute les scans horaires
- `utils_finnhub.py` → récupère les données float, prix, news
- `scraper_jaguar.py` → détecte l’activité anormale
- `tickers_scanned.json` → stockage temporaire des tickers

---

## 🔁 Fonctionnement général

```python
def scanner_postmarket():
    tickers = detecter_tickers_volatils()
    for t in tickers:
        if valider_criteres(t):
            ajouter_watchlist_auto(t)
            alerter_user(t)
```

Chaque ticker retenu est :

- ajouté à la **watchlist IA avec provenance = "PostMarketScanner"**,
- accompagné d’une **alerte Telegram + alarme sonore**,
- visible dans le tableau de bord du lendemain matin.

---

## 📌 User Stories associées

- **US-SCAN-001** – En tant que bot, je veux détecter les tickers actifs en dehors des horaires pour les surveiller à l'ouverture.
- **US-SCAN-002** – En tant qu’utilisateur, je veux recevoir une alerte dès qu’un ticker postmarket est identifié.
- **US-SCAN-003** – En tant que bot, je veux filtrer uniquement les tickers avec catalyseur et conditions réunies.

---

## 🔐 Sécurité & validation

Avant chaque ajout, le bot vérifie :

- Que les données du ticker sont valides (`valider_ticker_finnhub`)
- Qu’il n’a pas déjà été ajouté dans la watchlist IA
- Que l’activité est récente (moins de 24h)

---

## 📊 Table future `postmarket_tickers`

| Colonne       | Type    | Description                |
| ------------- | ------- | -------------------------- |
| `symbol`      | TEXT    | Code du ticker             |
| `detected_on` | TEXT    | Timestamp UTC de détection |
| `score`       | INTEGER | Score IA calculé           |
| `catalyseur`  | TEXT    | FDA, IPO, SPAC, etc.       |
| `float`       | INTEGER | Nombre d’actions en float  |
| `volume`      | INTEGER | Volume détecté             |

---

## ✅ Impact sur le bot WatchlistBot

- Génère automatiquement des **opportunités analysables dès l’ouverture**
- Prend une **longueur d’avance sur les scanners classiques**
- Permet d’**entraîner l’IA en continu** avec ces détections

> Ce module est une **brique clé de la version IA pro-active** du bot, assurant une détection précoce à haut potentiel.

---


# 22_pump_detector_et_trailing_stop

# 📘 Chapitre 22 – Détecteur de Pump et Trailing Stop Automatique

Ce module permet d’identifier en temps réel les **phases de pump suspectes** ou les **explosions de volume**, puis de **sécuriser automatiquement les gains via un trailing stop dynamique**.

C’est un élément clé du scalping intelligent pour penny stocks à forte volatilité.

---

## 🚀 Détection de Pump : logique IA

Le pump est détecté par l’agrégation des indicateurs suivants :

| Indicateur             | Seuil / déclencheur                | Source         |
| ---------------------- | ---------------------------------- | -------------- |
| Variation sur 1min     | > +5%                              | Finnhub        |
| Volume 1min            | > 200% moyenne mobile 5min         | Finnhub        |
| Bougie haussière forte | Close > Open + 2x ATR              | Interne        |
| RSI                    | > 75 (confirmé par hausse brutale) | Interne        |
| MACD                   | Croisement + momentum positif      | Interne        |
| Détection IA           | Score IA > 85                      | `meta_ia.json` |

Ces règles sont combinées avec une **pondération IA dynamique**.

```python
if variation_pct > 5 and volume_surge and rsi > 75 and score_ia > 85:
    detect_pump(ticker)
```

---

## 🧠 Réactions possibles

Lorsqu’un pump est détecté :

- une **alerte est envoyée** (Telegram + Streamlit + alarme),
- l’ordre d’achat peut être simulé ou exécuté si activé,
- un **stop loss suiveur (trailing stop)** est déclenché immédiatement.

---

## 📉 Trailing Stop : Sécurisation intelligente

Le stop suiveur permet de **laisser courir les gains tout en bloquant les pertes**.

### Règles intégrées (module `trailing.py`)

| Seuil       | Action                                  |
| ----------- | --------------------------------------- |
| Gain > +2%  | SL déplacé au prix d’entrée (breakeven) |
| Gain > +5%  | SL remonté à +3%                        |
| Gain > +10% | SL à +7%, Take Profit partiel possible  |

L’ajustement est fait **en temps réel** sur chaque nouveau prix détecté.

```python
trailing = TrailingManager(entry_price=1.0, stop_loss=0.95)
sl = trailing.update(current_price)
```

---

## 📂 Modules Python concernés

- `execution/pump_detector.py` → détection temps réel
- `execution/trailing.py` → stop dynamique
- `utils_finnhub.py` → récupération volume / prix
- `journal.py` → enregistrement des trades exécutés

---

## 📌 User Stories associées

- **US-PUMP-001** – En tant qu’IA, je veux détecter les hausses anormales sur une minute pour alerter l’utilisateur.
- **US-PUMP-002** – En tant que bot, je veux initier un trailing stop dès l’achat sur pump.
- **US-PUMP-003** – En tant qu’utilisateur, je veux visualiser le niveau du SL en temps réel dans l’interface.
- **US-PUMP-004** – En tant que système, je veux sécuriser une partie des gains à +10% automatiquement.

---

## 🧪 Cas de test clés

| Cas de test                | Résultat attendu                        |
| -------------------------- | --------------------------------------- |
| Pump détecté > 5% + volume | Alerte déclenchée                       |
| Pump + score IA > 85       | Ordre d’achat simulé et trailing activé |
| Gain > +2%                 | SL = prix d’entrée                      |
| Gain > +5%                 | SL remonté                              |
| Gain > +10%                | TP partiel + SL haut                    |

---

## 🗄️ Table `trailing_trades` (optionnel en base)

| Colonne         | Type | Description                       |
| --------------- | ---- | --------------------------------- |
| `symbol`        | TEXT | Ticker du trade                   |
| `entry_price`   | REAL | Prix d’entrée                     |
| `initial_sl`    | REAL | SL de départ                      |
| `current_sl`    | REAL | SL mis à jour dynamiquement       |
| `current_price` | REAL | Prix de marché                    |
| `gain_pct`      | REAL | % de gain actuel                  |
| `status`        | TEXT | actif / sécurisé / vendu          |
| `updated_on`    | TEXT | Timestamp de dernière mise à jour |

---

> Ce module permet une **sécurisation intelligente des trades explosifs**, sans intervention manuelle, avec une compatibilité IA et des règles adaptatives. Il est indispensable dans un environnement de scalping ultra-rapide.

---


# 23_daily_closure

# 📘 Chapitre 23 – Clôture Journalière (Daily Closure)

Le module de **clôture de journée** est une étape essentielle pour garantir l’intégrité des données, archiver les résultats, déclencher les alertes récapitulatives, et préparer une nouvelle session propre.

Il intervient en toute fin de journée après les analyses, simulations et exécutions éventuelles.

---

## 🎯 Objectifs de la clôture

- Geler les données de la session (résultats, scores, watchlist).
- Calculer les statistiques globales (PnL, nombre de trades, efficacité IA).
- Nettoyer l’environnement (réinitialisation des listes temporaires).
- Archiver les fichiers exportables (Excel, JSON, logs).
- Envoyer une notification Telegram résumant la journée.

---

## 🧪 Fonction principale : `cloturer_journee()`

### Localisation :

- `ui/page_modules/cloture_journee.py`

### Déclencheur :

- Bouton dans l’interface Streamlit : `st.button("Clôturer la journée")`

### Logique principale (extrait simplifié) :

```python
def cloturer_journee():
    stats = calculer_stats_du_jour()
    exporter_resultats_journaliers(stats)
    envoyer_alerte_telegram(stats)
    reset_watchlist_temporaire()
    vider_scores()
    logger("Clôture terminée avec succès")
```

---

## 🗃️ Tables affectées

| Table            | Action effectuée                       |
| ---------------- | -------------------------------------- |
| `watchlist`      | Suppression ou archivage               |
| `scores`         | Réinitialisation                       |
| `trades`         | Lecture seule pour calcul des KPIs     |
| `trades_simules` | Lecture + possibilité d’archivage JSON |

---

## 📁 Exports générés

- `export_journalier_{date}.json` : résultat des trades
- `pnl_resume_{date}.xlsx` : synthèse des gains/pertes
- `log_cloture_{date}.txt` : journalisation complète

Fichiers placés dans le dossier `exports/`.

---

## 🔔 Notification finale

- Appel de `envoyer_alerte_telegram(stats)` (via `telegram_bot.py`)
- Message résumé :

```
📊 Clôture du {date}
- Total trades : X
- Gain net : $Y
- Score IA moyen : Z
```

---

## 🔐 Sécurité & conditions

- Bouton de clôture **désactivé automatiquement** après usage (1 fois / jour).
- Historique journalier conservé dans `exports/`.
- Option de relancer `cloturer_journee(force=True)` en cas de correction manuelle.

---

## 📌 User Stories associées

- **US-CLOSE-001** – En tant qu’utilisateur, je veux archiver mes résultats de trading à la fin de chaque journée.
- **US-CLOSE-002** – En tant que système, je veux remettre à zéro la watchlist et les scores pour la prochaine session.
- **US-CLOSE-003** – En tant que responsable IA, je veux récupérer les journaux pour affiner les modèles d’apprentissage.
- **US-CLOSE-004** – En tant qu’utilisateur, je veux recevoir un résumé des résultats sans avoir à chercher dans les fichiers.

---

> ✅ Ce module garantit une base saine pour les sessions suivantes, tout en assurant la traçabilité des performances quotidiennes.

---


# 24_simulation_et_backtest_ia

# 📘 Chapitre 24 – Simulation et Backtest IA

Ce module est au cœur de l'amélioration continue du bot. Il permet de simuler des trades passés à partir de données historiques et d’évaluer l’efficacité des stratégies IA dans divers contextes de marché.

---

## 🎯 Objectif

- Tester les stratégies IA sur plusieurs jours/mois/années de données historiques
- Évaluer les performances (gains, drawdown, fiabilité)
- Ajuster dynamiquement les paramètres IA pour les futures sessions live
- Renforcer l’IA avec apprentissage supervisé + renforcement

---

## 🔁 Fonction principale

```python
from simulation.simulateur import lancer_backtest

resultats = lancer_backtest(
    liste_tickers=['GNS', 'CAMP'],
    periode='1y',
    capital_initial=2000,
    strategie='scalping_ai_v2',
    mode='historique'
)
```

Résultat : dictionnaire structuré contenant le PnL, les taux de réussite, les logs, et les ajustements IA.

---

## ⚙️ Paramètres du moteur

| Paramètre         | Type  | Description                                          |
| ----------------- | ----- | ---------------------------------------------------- |
| `strategie`       | str   | Nom de la stratégie à tester                         |
| `periode`         | str   | Durée : `1y`, `6mo`, `3mo`, `30d`, etc.              |
| `capital_initial` | float | Capital de départ pour calcul du PnL                 |
| `tickers`         | list  | Liste de symboles à analyser                         |
| `frais_reels`     | bool  | Appliquer ou non les frais Moomoo Canada             |
| `slippage_pct`    | float | Valeur à simuler pour slippage                       |
| `mode`            | str   | `historique`, `intraday`, `reel`                     |
| `afficher_graphs` | bool  | Générer ou non les graphiques Streamlit / Matplotlib |

---

## 🔍 Détail des indicateurs simulés

Chaque trade simule :

- RSI, EMA(9,21), VWAP, MACD, Volume, Bollinger, ATR, ADX
- Timing (cassure, pullback, rebond), float, catalyseur IA
- Application des seuils IA validés (score IA > 85, volume > seuil, etc.)

```python
if score_ia > 85 and vwap_crossed and breakout_validated:
    acheter(ticker)
```

---

## 📂 Modules Python concernés

- `simulation/simulateur.py` → moteur de backtest principal
- `intelligence/learning_engine.py` → ajustement des poids IA
- `execution/strategie_scalping.py` → logique de scalping
- `utils/data_loader.py` → récupération des données historiques
- `journal.py` → enregistrement des résultats simulés

---

## 📊 Structure de la table `simulated_trades`

| Colonne      | Type | Description                       |
| ------------ | ---- | --------------------------------- |
| `symbol`     | TEXT | Ticker                            |
| `timestamp`  | TEXT | Heure de l’action simulée         |
| `prix_achat` | REAL | Prix d’entrée simulé              |
| `prix_vente` | REAL | Prix de sortie simulé             |
| `strategie`  | TEXT | Stratégie IA utilisée             |
| `gain`       | REAL | Gain brut                         |
| `gain_pct`   | REAL | % de gain                         |
| `resultat`   | TEXT | `WIN` ou `LOSS`                   |
| `duration`   | TEXT | Durée du trade                    |
| `notes`      | TEXT | Détails stratégiques / erreurs IA |

---

## 📌 User Stories associées

- **US-SIM-001** – En tant qu’utilisateur, je veux tester une stratégie IA sur 6 mois de données historiques.
- **US-SIM-002** – En tant que système, je veux enregistrer tous les trades simulés dans une table dédiée.
- **US-SIM-003** – En tant qu’IA, je veux ajuster mes poids après chaque backtest pour m’améliorer.
- **US-SIM-004** – En tant qu’utilisateur, je veux visualiser un rapport graphique après simulation.
- **US-SIM-005** – En tant qu’architecte, je veux exporter les résultats pour audit / migration.

---

## 🧪 Cas de test clés

| Cas de test                 | Résultat attendu                       |
| --------------------------- | -------------------------------------- |
| Simulation sur 30 jours     | Résultat PnL global                    |
| Trade IA avec gain > 5%     | Enregistrement dans `simulated_trades` |
| Trade IA avec perte         | Stocké avec note d’erreur              |
| Ajustement IA après test    | Nouveau poids IA sauvegardé            |
| Visualisation des résultats | Graphique Streamlit avec gain/jour     |

---

## 📤 Fichiers de sortie

- `results/simulation_{date}.json` – Résultats structurés complets
- `graphs/simulation_{date}.png` – Graphique de performance
- `simulated_trades.db` – Table complète des ordres simulés

---

> Ce module permet un **entraînement IA à grande échelle**, une **validation empirique des stratégies** et une **préparation fiable à l’exécution réelle** sur compte démo ou réel.

---


# 25_apprentissage_renforce_ia

# 📘 Chapitre 25 – Apprentissage Renforcé IA

Ce module applique une logique d’apprentissage par renforcement à partir des résultats de trading (réels ou simulés) pour ajuster automatiquement les décisions futures du bot IA.

Il repose sur une **formule de récompense** calibrée, la **pénalisation des erreurs critiques**, et une **mise à jour dynamique des poids stratégiques**.

---

## 🎯 Objectif du module

- Apprendre automatiquement des trades gagnants et perdants
- Renforcer les décisions menant à de bons résultats
- Éviter les patterns conduisant à des pertes
- Mettre à jour dynamiquement les règles IA (score, stop loss, timing)

---

## 🧠 Logique de renforcement IA

Chaque trade (réel ou simulé) est analysé à postériori selon ces règles :

```python
reward = gain_pct * facteur_confiance
penalty = erreur_strategique * facteur_erreur
score_ajuste = score_ia + reward - penalty
```

**Explications :**

- `gain_pct` : gain du trade en %
- `facteur_confiance` : pondération basée sur la solidité des signaux
- `erreur_strategique` : erreurs détectées (ex: entrée tardive, SL trop serré)
- `score_ia` : score de départ du trade

Un système de **logique floue** permet de moduler ces valeurs entre 0 et 1.

---

## 🧩 Modules Python concernés

- `intelligence/learning_engine.py` → moteur IA de mise à jour
- `simulation/simulateur.py` → fournit les résultats des trades simulés
- `execution/strategie_scalping.py` → fournit les signaux bruts
- `journal.py` → source de vérité pour les trades réels
- `utils/math_tools.py` → fonctions de pondération et normalisation

---

## 🧾 Format des données d’entrée (résultats de trade)

| Champ         | Type | Description                            |
| ------------- | ---- | -------------------------------------- |
| `symbol`      | TEXT | Ticker analysé                         |
| `score_ia`    | REAL | Score initial au moment de la décision |
| `gain_pct`    | REAL | Gain ou perte (en %)                   |
| `sl_touch`    | BOOL | Si le stop loss a été touché           |
| `tp_reached`  | BOOL | Si le take profit a été atteint        |
| `duree_trade` | TEXT | Durée entre achat et vente             |
| `volume`      | INT  | Volume échangé pendant le trade        |
| `indicateurs` | JSON | Valeurs des indicateurs clés utilisés  |
| `notes`       | TEXT | Observations du moteur IA              |

---

## ⚙️ Paramètres par défaut

| Paramètre              | Valeur défaut | Description                                    |
| ---------------------- | ------------- | ---------------------------------------------- |
| `facteur_confiance`    | 1.0           | Pondération des signaux                        |
| `facteur_erreur`       | 1.5           | Pénalité en cas de défaillance                 |
| `seuil_gain_minimal`   | 3.0           | % à partir duquel un trade est considéré utile |
| `score_min_retenu`     | 85            | Score minimal pour renforcement                |
| `max_trades_par_cycle` | 1000          | Pour éviter surcharge mémoire                  |

---

## 🧪 Cas de test clés

| Cas de test                              | Résultat attendu                     |
| ---------------------------------------- | ------------------------------------ |
| Trade gagnant avec TP atteint            | Augmentation du poids de stratégie   |
| Trade perdant avec SL déclenché          | Diminution du score de configuration |
| Trade neutre (0% gain)                   | Pas de mise à jour                   |
| Erreur IA détectée (entrée trop tardive) | Pénalité sur le critère de timing    |
| Plusieurs trades avec même pattern       | Ajustement groupé des paramètres     |

---

## 📌 User Stories associées

- **US-IA-REWARD-001** – En tant qu’IA, je veux renforcer les stratégies qui génèrent des gains > 5%.
- **US-IA-REWARD-002** – En tant qu’utilisateur, je veux voir l’évolution des poids IA dans l’interface.
- **US-IA-REWARD-003** – En tant que système, je veux éviter d’utiliser une stratégie si elle a échoué 3 fois.
- **US-IA-REWARD-004** – En tant qu’architecte, je veux exporter les pondérations IA pour debug / analyse.

---

## 📤 Fichiers de sortie

- `logs/learning/poids_ia_{date}.json` – Nouveau mapping des pondérations IA
- `learning_history.db` – Historique complet des ajustements stratégiques
- `rapport_apprentissage.csv` – Résumé lisible des mises à jour

---

## 📌 Impact système

✅ Ce module permet à l’IA d’apprendre de manière **autonome et continue**, avec un focus sur :

- La **fiabilité** des signaux IA (par renforcement positif)
- La **correction des erreurs fréquentes** (par pénalité)
- L’**adaptation automatique** au marché

> C’est l’un des piliers majeurs de la performance long terme du bot de trading.

---


# 26_watchlist_multi_source

# 📘 Chapitre 26 – Générateur de Watchlist Multi-Sources

Ce module centralise les tickers à analyser chaque jour, en fusionnant plusieurs sources (manuel, IA, scraping), avec un mécanisme de filtrage, priorisation, et enrichissement automatique.

---

## 🎯 Objectif du module

- Créer une watchlist quotidienne unifiée à partir de plusieurs sources
- Appliquer des règles de priorité, nettoyage, et enrichissement
- Éviter les doublons, les erreurs, et les faux signaux
- Proposer des tickers avec score, timing et provenance claire

---

## 📥 Sources de données principales

| Source          | Format | Fichier / Module utilisé  | Détails                                             |
| --------------- | ------ | ------------------------- | --------------------------------------------------- |
| Manuel          | JSON   | `tickers_manuels.json`    | Ajouts directs via interface ou fichier             |
| Scraping Jaguar | JSON   | `resultats_scraping.json` | Tickers détectés sur sites spécialisés              |
| IA interne      | JSON   | `meta_ia.json`            | Résultats du moteur IA sur les patterns historiques |

---

## ⚙️ Logique de fusion / enrichissement

```python
from intelligence.watchlist_engine import generer_watchlist

tickers_fusionnes = generer_watchlist(sources=['manuel', 'ia', 'scraping'])
```

### Étapes appliquées :

1. Chargement de chaque fichier source
2. Suppression des doublons (clé = `symbol`)
3. Fusion des métadonnées (score, float, volume, provenance)
4. Calcul du score final pondéré (score IA, catalyseur, anomalie volume)
5. Enrichissement avec données techniques :
   - VWAP, EMA9/21, RSI, news FDA, float < 200M, etc.
6. Tri décroissant par score

---

## 🧩 Modules Python concernés

- `intelligence/watchlist_engine.py` → module principal de fusion
- `utils_fusion.py` → fonctions de nettoyage / enrichissement
- `data/sources_loader.py` → charge chaque fichier source
- `ui/pages/gestion_watchlist.py` → interface de visualisation

---

## 🧾 Structure finale d’un ticker

| Champ            | Type | Description                                         |
| ---------------- | ---- | --------------------------------------------------- |
| `symbol`         | TEXT | Code du ticker (ex: GNS, HLTH)                      |
| `provenance`     | TEXT | Source d’origine : `manuel`, `IA`, `scraping`, etc. |
| `score_final`    | REAL | Score combiné (sur 100) calculé dynamiquement       |
| `float`          | INT  | Nombre d’actions en circulation                     |
| `variation_pct`  | REAL | % de gain journalier                                |
| `volume`         | INT  | Volume journalier observé                           |
| `news_detected`  | BOOL | True si catalyseur type FDA / Fusion détecté        |
| `graph_snapshot` | STR  | Lien vers image graphique (optionnel)               |

---

## 📌 User Stories associées

- **US-WL-001** – En tant qu’utilisateur, je veux que tous les tickers soient centralisés dans une seule liste triée.
- **US-WL-002** – En tant que système, je veux ignorer les doublons et les tickers invalides (prix ≤ 0).
- **US-WL-003** – En tant qu’IA, je veux que le score soit recalculé après enrichissement.
- **US-WL-004** – En tant qu’utilisateur, je veux voir la provenance de chaque ticker dans l’interface.
- **US-WL-005** – En tant qu’architecte, je veux que les règles de fusion soient traçables et auditées.

---

## 🧪 Cas de test clés

| Cas de test                       | Résultat attendu                                   |
| --------------------------------- | -------------------------------------------------- |
| Présence du même ticker 2x        | Un seul ticker fusionné avec métadonnées enrichies |
| Ticker avec float > 200M          | Exclu automatiquement (règle IA)                   |
| Ticker sans catalyseur            | Score réduit                                       |
| Chargement manuel + IA + scraping | Liste complète triée par score final               |

---

## ⚙️ Fichier de sortie

- `watchlist_du_jour.json` → Liste complète triée avec scores et provenances
- `watchlist_log.csv` → Historique des ajouts par source + horodatage
- `watchlist_debug_invalids.json` → Liste des tickers exclus avec raison

---

## 📌 Impact système

✅ Ce module garantit une **base de travail fiable chaque matin**, avec des tickers analysés, enrichis et triés automatiquement, permettant à l’IA de démarrer avec une liste cohérente et performante.

> Un module stratégique pour éviter les faux positifs et focaliser les ressources IA sur les meilleurs candidats journaliers.

---


# 27_analyse_graphique_signaux (1)

# 📘 Chapitre 27 – Analyse Graphique & Signaux Visuels

Ce module vise à détecter visuellement des signaux techniques clés sur les graphiques des tickers, notamment via les cassures de niveau, les chandeliers, les volumes anormaux, et les patterns de breakout. Il sert à alerter l'utilisateur via l'interface Streamlit avec une lecture claire, sans interférence sur la logique IA principale.

---

## 🎯 Objectif du module

- Visualiser les signaux techniques pertinents directement dans l’interface utilisateur
- Détecter automatiquement des patterns : cassure, pullback, volume, chandelier, etc.
- Générer des instantanés graphiques (snapshots) à afficher avec chaque ticker
- Ne pas interférer avec les décisions IA (module purement visuel)

---

## 🔍 Patterns détectés

| Pattern / Signal      | Condition de déclenchement                       | Exemple visuel                               |
| --------------------- | ------------------------------------------------ | -------------------------------------------- |
| Cassure de résistance | Dernier prix > plus haut des 2 dernières bougies | `df['Close'].iloc[-1] > df['High'].iloc[-2]` |
| Pullback validé       | Retour au niveau cassé + volume supérieur        | `Volume[-1] > moyenne(3)`                    |
| Marubozu haussier     | Bougie sans mèche basse, forte clôture au sommet | `Open ≈ Low` et `Close ≈ High`               |
| Engulfing haussier    | Bougie verte > bougie rouge précédente           | `BodyGreen > BodyRed`                        |
| Volume anormal        | Volume dernier tick > 1.5× moyenne précédente    | `vol[-1] > 1.5 * moyenne(vol[-10:])`         |

---

## 🧠 Logique technique (extrait de code)

```python
import pandas as pd
import matplotlib.pyplot as plt

def detect_breakout(df):
    return df['Close'].iloc[-1] > df['High'].iloc[-2]

def snapshot_graph(df, symbol):
    fig, ax = plt.subplots()
    df[['Open','High','Low','Close']].tail(20).plot(ax=ax, title=f"{symbol} - Derniers chandeliers")
    img_path = f"images_snapshots/{symbol}.png"
    fig.savefig(img_path)
    return img_path
```

---

## 🧩 Modules Python concernés

- `utils_graph.py` → gestion des graphiques, snapshots
- `intelligence/pattern_graphique.py` → détection des patterns
- `ui/pages/heatmap_realtime.py` → affichage interactif
- `data/historique_manager.py` → accès aux données de bougies

---

## 🧾 Structure d’un signal visuel (dans ticker enrichi)

| Champ             | Type   | Description                                   |
| ----------------- | ------ | --------------------------------------------- |
| `symbol`          | TEXT   | Code du ticker                                |
| `graph_snapshot`  | STRING | Chemin vers l’image snapshot (PNG)            |
| `pattern_detecte` | TEXT   | Pattern détecté (`breakout`, `pullback`, ...) |
| `volume_alert`    | BOOL   | True si volume anormal détecté                |

---

## 📌 User Stories associées

- **US-GRAPH-001** – En tant qu’utilisateur, je veux voir le graphique de chaque ticker avec des indications visuelles.
- **US-GRAPH-002** – En tant que bot, je veux générer un snapshot au moment du scan journalier.
- **US-GRAPH-003** – En tant que système, je veux détecter automatiquement les patterns sans interagir avec les décisions IA.
- **US-GRAPH-004** – En tant qu’utilisateur, je veux comprendre visuellement pourquoi un score élevé est attribué à un ticker.

---

## 🧪 Cas de test fonctionnels

| Cas de test                 | Résultat attendu                            |
| --------------------------- | ------------------------------------------- |
| Cassure détectée            | Image générée + tag `breakout` dans ticker  |
| Pullback après cassure      | Pattern = `pullback`                        |
| Volume > 1.5x moyenne       | Champ `volume_alert` = True                 |
| Affichage graphique dans UI | Image visible dans panneau ticker Streamlit |

---

## 📤 Dossiers de sortie

- `/images_snapshots/` → Contient les images graphiques par ticker
- `tickers_enrichis.json` → Contient les champs `pattern_detecte`, `graph_snapshot`

---

## 🔄 Mécanisme de rafraîchissement

- Snapshots générés **uniquement lors de l’ouverture manuelle du ticker** dans l’interface
- Aucun impact sur les performances IA (traitement uniquement visuel)

---

## 🎯 Impact global

✅ Améliore l’interprétation humaine et la prise de décision ✅ Permet aux traders de valider visuellement les signaux IA ✅ Sert de support à l’audit et à l’apprentissage visuel

Un module complémentaire essentiel pour renforcer la confiance dans le système de détection, tout en conservant la séparation claire entre IA et interface visuelle.

---


# 27_analyse_graphique_signaux (2)

# 📘 Chapitre 28 – Détection de Pump + Stop Loss Dynamique

Ce module permet de détecter les situations de pump (hausse anormale et soudaine d’un ticker) et d’appliquer une gestion dynamique du stop loss via un gestionnaire de trailing stop (suivi de prix). Il améliore la sécurité des positions et l’automatisation des prises de bénéfices.

---

## 🎯 Objectif du module

- Détecter automatiquement les situations de pump (hausse brutale + volume anormal)
- Appliquer un stop loss évolutif basé sur la performance en temps réel
- Automatiser la prise de bénéfices ou sortie préventive
- Intégrer un moteur intelligent de gestion du risque (TrailingManager)

---

## 🚀 Détection de Pump – Logique métier

| Critère             | Condition Python                                 | Justification                              |
| ------------------- | ------------------------------------------------ | ------------------------------------------ |
| Gain instantané     | `(price_now - price_5s_ago)/price_5s_ago > 0.03` | Hausse > 3% en quelques secondes           |
| Volume minute élevé | `volume_1m > 500000`                             | Preuve d’un engouement ou flux soudain     |
| Float bas           | `float < 100_000_000`                            | Sensibilité accrue des petits flottants    |
| Catalyseur détecté  | `score_catalyseur > 0.5`                         | Événement externe favorable (news, FDA...) |

---

## 🧠 Exemple de code : pump detector

```python
from execution.utils_indicateurs import get_last_price, get_price_5s_ago, get_volume, get_float, get_catalyseur_score

def is_pump_candidate(ticker):
    p_now = get_last_price(ticker)
    p_old = get_price_5s_ago(ticker)
    v1m = get_volume(ticker, '1m')
    fl = get_float(ticker)
    score = get_catalyseur_score(ticker)
    return (
        (p_now - p_old) / p_old > 0.03 and
        v1m > 500_000 and
        fl < 100_000_000 and
        score > 0.5
    )
```

---

## 🛡️ Stop Loss Dynamique – TrailingManager

Le module `TrailingManager` ajuste automatiquement le stop selon la performance :

| Condition d'évolution      | Nouvelle valeur de SL          | Description                 |
| -------------------------- | ------------------------------ | --------------------------- |
| Prix > +2% au-dessus achat | SL = prix d’achat (break-even) | Sécurisation immédiate      |
| Prix > +5%                 | SL = +3% au-dessus prix achat  | Protection du profit latent |
| Chute de prix              | Retour immédiat au SL          | Sortie automatique          |

### Implémentation

```python
class TrailingManager:
    def __init__(self, entry_price, stop_loss):
        self.entry_price = entry_price
        self.stop_loss = stop_loss

    def update(self, price):
        if price >= self.entry_price * 1.05:
            self.stop_loss = max(self.stop_loss, self.entry_price * 1.03)
        elif price >= self.entry_price * 1.02:
            self.stop_loss = max(self.stop_loss, self.entry_price)
        return self.stop_loss
```

---

## 🧩 Modules Python concernés

- `execution/pump_detector.py` → détection de pump
- `execution/strategie_scalping.py` → intègre le TrailingManager
- `execution/utils_indicateurs.py` → indicateurs nécessaires (prix, volume, float, catalyseur)

---

## 📊 Structure des résultats enrichis

| Champ              | Type  | Description                      |
| ------------------ | ----- | -------------------------------- |
| `symbol`           | TEXT  | Code du ticker                   |
| `pump_detected`    | BOOL  | True si pump détecté             |
| `entry_price`      | FLOAT | Prix d’entrée initial            |
| `stop_loss`        | FLOAT | Stop loss dynamique (mis à jour) |
| `gain_potentiel`   | FLOAT | Gain projeté à +5%               |
| `trailing_manager` | OBJ   | État interne du gestionnaire     |

---

## 📌 User Stories associées

- **US-PUMP-001** – En tant que bot, je veux détecter les situations de pump en temps réel.
- **US-PUMP-002** – En tant que bot, je veux appliquer un stop loss dynamique basé sur le comportement du prix.
- **US-PUMP-003** – En tant qu’utilisateur, je veux visualiser dans l’UI le SL actuel ajusté automatiquement.
- **US-PUMP-004** – En tant que système, je veux que la gestion de stop ne bloque pas l’interface (asynchrone).

---

## ✅ Cas de test

| Cas de test                            | Résultat attendu                         |
| -------------------------------------- | ---------------------------------------- |
| Pump détecté avec volume et catalyseur | `pump_detected = True`                   |
| Prix monte à +5%                       | SL mis à jour à `entry_price * 1.03`     |
| Prix chute en-dessous du SL            | Trade clôturé automatiquement            |
| Utilisateur visualise le SL en UI      | Valeur actualisée dans le panneau ticker |

---

## 🎯 Impact global

✅ Sécurise automatiquement les trades avec logique IA de sortie ✅ Prévient les pertes en cas de chute soudaine ✅ Favorise les gains dans les situations de pump ✅ Complément essentiel au moteur d’exécution intelligent

---


# 28_pump_detector_trailing_stop

# 📘 Chapitre 28 – Pump Detector & Trailing Stop

Ce module est dédié à la **surveillance en temps réel** des mouvements brutaux de prix (« pumps ») et à la gestion intelligente des sorties via un **Trailing Stop dynamique**.

Il s'agit d’un composant clé pour le **scalping sur penny stocks volatils** : il détecte les anomalies de prix et déclenche des simulations ou alertes avec sécurité automatisée.

---

## 🎯 Objectifs fonctionnels

- Détecter les hausses de prix brutales sur un court laps de temps.
- Confirmer la légitimité du mouvement par le volume.
- Exécuter (ou simuler) une entrée IA avec sortie via Trailing Stop.
- Notifier l’utilisateur en cas de signal confirmé (popup ou Telegram).

---

## 🔁 Surveillance temps réel : `pump_detector.py`

### 📥 Source de données

- Table `ticks` (ou `intraday_smart`) de la base `trades.db`
- Mise à jour via : `realtime/real_time_tick_collector.py`

### 🔎 Critères de détection (paramétrables)

Chargés depuis `config/rules_auto.json` :

| Paramètre           | Valeur par défaut | Rôle                                       |
| ------------------- | ----------------- | ------------------------------------------ |
| `price_spike_pct`   | 5.0               | Variation minimum (%) sur quelques minutes |
| `volume_ratio_min`  | 3.0               | Volume instantané / moyenne historique     |
| `trailing_stop_pct` | 2.5               | Pourcentage utilisé pour trailing stop     |

### 🔧 Exemple d'appel simplifié

```python
if price_change > price_spike_pct and volume_ratio > volume_ratio_min:
    envoyer_alerte_ia(ticker, motif="Pump détecté")
    simulate_trailing_trade(ticker)
```

---

## 🧠 Composant IA : `simulate_trailing_trade()`

Ce simulateur effectue un achat virtuel à l’instant du signal, puis laisse le **Trailing Stop** gérer la sortie en maximisant le gain sans retour brutal.

Fonctions clés :

- `TrailingStop(entry_price, stop_pct)`
- `update(price)` → met à jour dynamiquement le niveau de sortie

### Exemple illustratif :

```python
ts = TrailingStop(entry_price=1.0, stop_pct=0.025)

for price in [1.01, 1.03, 1.07, 1.05, 1.02]:
    new_sl = ts.update(price)
    print(f"New SL: {new_sl:.2f}")
```

🔁 Lors d’un retracement dépassant le SL calculé, la **vente est déclenchée automatiquement**.

---

## 💾 Enregistrement simulé : `simulate_trade_result.py`

Tous les résultats sont insérés dans :

| Table            | Champs utilisés                                                |
| ---------------- | -------------------------------------------------------------- |
| `trades_simules` | `symbol`, `entry`, `exit`, `gain`, `sl`, `strategy`, `comment` |

---

## 🔔 Notifications

| Méthode               | Description                         |
| --------------------- | ----------------------------------- |
| `envoyer_alerte_ia()` | Message Telegram ou popup Streamlit |
| `popup_trade.py`      | Fenêtre en overlay dans l'interface |

---

## ⚖️ Justification des paramètres

- **Variation de prix ≥ 5%** : seuil conservateur pour éviter les faux signaux
- **Ratio volume ≥ 3x** : filtre les mouvements faibles ou suspects
- **Trailing Stop 2.5%** : sécurisé mais assez large pour laisser courir un pump

Ces valeurs sont optimisées pour : **penny stocks entre 0.5\$ et 10\$, float faible, catalyst actif**.

---

## 🔗 Modules liés

| Module                                 | Fonction                              |
| -------------------------------------- | ------------------------------------- |
| `realtime/real_time_tick_collector.py` | Alimente `ticks` en live              |
| `simulate_trade_result.py`             | Calcule les résultats simulés         |
| `telegram_bot.py` / `popup_trade.py`   | Envoie les alertes                    |
| `ai_scorer.py`                         | Peut ajuster le score suite à un pump |

---

## 📌 User Stories associées

- **US-PUMP-001** – En tant qu’IA, je dois détecter rapidement les variations de prix brutales.
- **US-PUMP-002** – En tant que système, je dois vérifier si le volume valide le mouvement.
- **US-PUMP-003** – En tant qu’utilisateur, je veux être alerté immédiatement avec un message clair.
- **US-PUMP-004** – En tant que simulateur, je dois estimer le gain net avec trailing stop.

---

> ✅ Ce module est critique pour détecter des opportunités ultra-courtes en temps réel, tout en assurant une sortie intelligente sans stress manuel.

---


# 30_execution_reelle_et_journal (1)

# 📘 Chapitre 30 – Exécution des Ordres Réels & Journalisation

Ce module gère l’envoi réel des ordres d’achat ou de vente, que ce soit vers un courtier ou en mode simulation locale. Il est au cœur de la gestion de l’exécution sécurisée, traçable, et connectée à l’IA.

---

## 🎯 Objectifs du module

- Exécuter les ordres en respectant les règles de stratégie et de sécurité
- Journaliser chaque action dans la base (`real_trades`, `trade_logs`...)
- Confirmer l’exécution ou l’échec (avec détails)
- Gérer les erreurs et états (annulé, échoué, rempli partiellement, etc.)
- Déclencher les notifications (interface, son, Telegram)

---

## ⚙️ Logique d’exécution

```python
from execution.broker_api import envoyer_ordre
from db_model import enregistrer_trade_reel

def executer_ordre(ticker, prix, quantite, sens="buy", strategie="manual"):
    try:
        resultat = envoyer_ordre(ticker, prix, quantite, sens)
        if resultat["status"] == "filled":
            enregistrer_trade_reel(ticker, prix, quantite, sens, resultat, strategie)
        return resultat
    except Exception as e:
        logger.error(f"Erreur exécution: {e}")
        return {"status": "failed", "error": str(e)}
```

---

## 🧾 Table `real_trades`

| Champ      | Type  | Description                            |
| ---------- | ----- | -------------------------------------- |
| id         | INT   | Identifiant unique                     |
| symbol     | TEXT  | Ticker exécuté                         |
| date\_time | TEXT  | Timestamp de l’ordre                   |
| type       | TEXT  | buy / sell                             |
| prix       | FLOAT | Prix d’exécution                       |
| quantite   | INT   | Quantité exécutée                      |
| status     | TEXT  | filled / partial / failed              |
| courtier   | TEXT  | API utilisée (IBKR, Alpaca, Simulé...) |
| strategie  | TEXT  | Stratégie ayant généré l’ordre         |
| log\_id    | INT   | Référence vers la ligne de log         |

---

## 🗂️ Modules Python concernés

- `execution/broker_api.py` → interface avec API courtier ou simulateur
- `execution/strategie_scalping.py` → appel à `executer_ordre`
- `db_model.py` → gestion de la table `real_trades`
- `journal/journal.py` → enregistrement contextuel des logs
- `ui/pages/dashboard.py` → affichage des résultats et historiques
- `telegram/alertes.py` → notification si exécution réelle réussie ou échouée

---

## 📌 User Stories

- **US-EXEC-001** – En tant que système, je veux envoyer un ordre au courtier et obtenir une confirmation.
- **US-EXEC-002** – En tant qu’utilisateur, je veux voir mes ordres exécutés dans une interface claire.
- **US-EXEC-003** – En tant que bot, je veux enregistrer chaque ordre pour audit et apprentissage futur.
- **US-EXEC-004** – En tant que développeur, je veux pouvoir simuler l’exécution locale sans courtier.
- **US-EXEC-005** – En tant qu’analyste, je veux suivre l’état de chaque ordre (échec, partiel, rempli).

---

## ✅ Cas de test

| Cas de test                                      | Résultat attendu                               |
| ------------------------------------------------ | ---------------------------------------------- |
| Envoi d’un ordre d’achat à 1.00 pour 100 actions | Réponse `filled` avec données enregistrées     |
| Courtier non disponible                          | Réponse `failed` + erreur affichée/loguée      |
| Interface affiche la ligne                       | L’ordre apparaît dans l’historique utilisateur |
| Notification Telegram activée                    | Message envoyé avec détails de l’ordre         |
| Ordre partiellement rempli                       | Statut `partial` + quantité réelle enregistrée |

---

## 🔐 Aspects sécurité & robustesse

- Vérification du solde ou capital simulé
- Validation du ticker et de la stratégie
- Timeout automatique si pas de réponse du courtier
- Log complet en local (erreur + succès)
- Aucune répétition en cas d’échec sauf confirmation explicite

---

## 🧠 Impact global

✅ Centralise les décisions en un point unique d’exécution ✅ Traçabilité complète (backtest, audit, apprentissage IA) ✅ Sécurité renforcée contre les erreurs d’ordre ✅ Intégration multi-brokers ou mode déconnecté sans perte de logique

---


# 31_cloture_journaliere

# 📘 Chapitre 31 – Clôture Journalière Automatique & Résumé des Performances

Ce module permet de geler les activités de la journée, de sauvegarder les résultats, d’enrichir les indicateurs d’apprentissage, et de fournir un tableau de bord consolidé pour évaluer les performances.

---

## 🎯 Objectifs du module

- Arrêter proprement toutes les activités de trading à la fin de la journée
- Calculer les statistiques journalières : gains, pertes, nombre d’ordres, ratio de succès
- Archiver les données critiques dans la base (`daily_summary`, `indicateurs_ia`...)
- Mettre à jour les scores et les pondérations IA selon les résultats
- Envoyer un résumé automatique par mail, Telegram ou UI

---

## ⚙️ Logique de traitement

```python
from cloture import cloturer_journee
from dashboard import generer_resume

def cloture_auto():
    cloturer_journee()
    resume = generer_resume()
    notifier_resultats(resume)
```

---

## 🧾 Table `daily_summary`

| Champ            | Type  | Description                           |
| ---------------- | ----- | ------------------------------------- |
| id               | INT   | Identifiant                           |
| date             | TEXT  | Date de clôture (YYYY-MM-DD)          |
| nb\_trades       | INT   | Nombre total d’ordres exécutés        |
| gain\_total      | FLOAT | Gain ou perte net de la journée       |
| nb\_gagnants     | INT   | Ordres ayant généré un gain           |
| nb\_perdants     | INT   | Ordres perdants                       |
| taux\_reussite   | FLOAT | Pourcentage de réussite (0 à 1)       |
| max\_win         | FLOAT | Meilleur gain réalisé                 |
| max\_loss        | FLOAT | Plus grosse perte                     |
| moyenne\_holding | FLOAT | Durée moyenne de détention en minutes |

---

## 🧾 Table `indicateurs_ia`

| Champ          | Type  | Description                                 |
| -------------- | ----- | ------------------------------------------- |
| date           | TEXT  | Date d’entrée                               |
| param\_name    | TEXT  | Nom de l’indicateur (ex: score\_rsi)        |
| value          | FLOAT | Valeur moyenne observée ce jour-là          |
| trades\_winner | INT   | Nombre de trades gagnants avec ce paramètre |
| trades\_loser  | INT   | Nombre de trades perdants                   |
| poids\_ajuste  | FLOAT | Poids ajusté en fonction des résultats      |

---

## 🗂️ Modules Python concernés

- `cloture.py` → déclencheur du processus de fin de journée
- `dashboard.py` → résumé visuel, tableau, export CSV
- `journal.py` → collecte et nettoyage des journaux
- `utils.py` → fonctions d’agrégation, calculs de moyenne, ratio, etc.
- `telegram/alertes.py` → envoi du bilan en message
- `ia/learning_engine.py` → mise à jour pondérée des paramètres

---

## 📌 User Stories

- **US-CLOT-001** – En tant que bot, je veux sauvegarder proprement tous les résultats à 16h00.
- **US-CLOT-002** – En tant qu’utilisateur, je veux voir un tableau clair avec les gains et pertes du jour.
- **US-CLOT-003** – En tant que système IA, je veux adapter les pondérations selon la réussite des signaux.
- **US-CLOT-004** – En tant qu’analyste, je veux exporter un bilan journalier en CSV.
- **US-CLOT-005** – En tant qu’utilisateur, je veux recevoir un résumé des performances sur Telegram ou mail.

---

## ✅ Cas de test

| Cas de test                          | Résultat attendu                                   |
| ------------------------------------ | -------------------------------------------------- |
| Appel à `cloturer_journee()` à 16h00 | Données sauvegardées dans `daily_summary`          |
| IA met à jour les pondérations       | Changement visible dans `indicateurs_ia`           |
| UI affiche le résumé du jour         | Dashboard avec gains, pertes, ratio, top trades    |
| CSV exporté avec succès              | Fichier contenant tous les résultats de la journée |
| Alerte envoyée en fin de clôture     | Message Telegram avec les chiffres clés            |

---

## 🧠 Intérêt stratégique

✅ Permet d’avoir une trace quotidienne pour le backtest ✅ Nourrit le moteur IA avec des statistiques réelles ✅ Automatise les bilans et facilite la communication à l’utilisateur ✅ Sert de base pour l’évolution de la stratégie à long terme

---

## 🔐 Aspects sécurité & qualité

- Clôture bloquée si des ordres sont encore en cours
- Vérification de l’intégrité des journaux avant agrégation
- Sauvegarde redondante dans un fichier CSV + base
- Possibilité de rejouer les étapes si données absentes
- Archivage automatique hebdomadaire et mensuel

---


# 31_daily_workflow_detailed

# 📘 Chapitre 31 – Workflow Journalier Complet (Daily Workflow)

Ce chapitre détaille l’enchaînement **complet, structuré et justifié** des modules utilisés au quotidien dans WatchlistBot V7.03, depuis l’ouverture jusqu’à la clôture de session, incluant les indicateurs techniques utilisés, leurs valeurs seuils, les fonctions appelées, les tables mises à jour, et les raisons des choix techniques.

---

## 🧭 Vue d’ensemble du workflow journalier

```mermaid
graph TD
    Start[Lancement UI Streamlit] --> Import[Import Watchlist (manuel, Jaguar, fichier)]
    Import --> Analyse[Analyse IA + Scoring (indicateurs)]
    Analyse --> Affichage[Affichage des tickers + Interface interactive]
    Affichage --> Execution[Simulation ou Exécution de stratégie scalping]
    Execution --> Journal[Journalisation des trades (trades.db)]
    Journal --> Cloture[Clôture journalière + export + reset]
    Cloture --> End[Fin de session]
```

---

## 🔁 Étape 1 : Lancement de l’application

| Élément           | Description                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------- |
| Commande          | `streamlit run ui/app_unifie_watchlistbot.py`                                                 |
| Modules chargés   | `analyse_tickers_realtime.py`, `cloture_journee.py`, `checklist_import_affichage.py`, etc.    |
| Fonction critique | `charger_watchlist()` → charge `tickers_manuels.json`, `watchlist_jaguar.txt`, `meta_ia.json` |
| Précondition      | Connexion à `data/trades.db` avec toutes les tables initialisées                              |

---

## 📥 Étape 2 : Import ou ajout de tickers

| Source | Module Python                                        | Type           |
| ------ | ---------------------------------------------------- | -------------- |
| Manuel | `tickers_manuels.json`                               | JSON statique  |
| Jaguar | `scripts/scraper_jaguar.py` → `watchlist_jaguar.txt` | scraping texte |
| IA     | `meta_ia.json` généré par `learning_loop.py`         | pondérations   |

Fonction centrale : `fusion/module_fusion_watchlist.py`

```python
# Exemple de fusion des sources
sources = [tickers_manuels, jaguar, ia_meta]
watchlist_fusion = fusionner_watchlists(sources)
```

> 🎯 Objectif : obtenir une liste unifiée et filtrée de tickers pertinents à analyser.

---

## 🤖 Étape 3 : Analyse IA et Scoring

Module principal : `intelligence/ai_scorer.py`

### Indicateurs utilisés & valeurs typiques (ajustables)

| Indicateur | Fonction                       | Seuil / Poids                | Raison                                 |
| ---------- | ------------------------------ | ---------------------------- | -------------------------------------- |
| RSI        | `get_rsi(ticker)`              | 70 (surachat), 30 (survente) | Momentum                               |
| EMA        | `get_ema(ticker, [9,21])`      | Croisement EMA9 > EMA21      | Signal haussier                        |
| VWAP       | `get_vwap(ticker)`             | Prix > VWAP = force          | Volume moyen pondéré                   |
| MACD       | `get_macd(ticker)`             | MACD > 0 et > signal         | Accélération tendance                  |
| Volume     | `get_volume(ticker, '1m')`     | > 500 000                    | Activité confirmée                     |
| Float      | `get_float(ticker)`            | < 100M                       | Petite capitalisation → potentiel pump |
| Catalyseur | `get_catalyseur_score(ticker)` | > 0.7                        | News, FDA, fusion...                   |
| ATR        | `get_atr(ticker)`              | base pour SL/TP dynamiques   | Volatilité                             |

### Fonction critique

```python
def _compute_score(ticker):
    rsi = get_rsi(ticker)
    ema = get_ema(ticker, [9, 21])
    volume = get_volume(ticker)
    price = get_last_price(ticker)
    score = calculer_score_pondere(rsi, ema, volume, price, ...)
    return score
```

Résultat stocké dans : `scores` table (SQLite)

---

## 📊 Étape 4 : Affichage et interface utilisateur

- Interface : `ui/app_unifie_watchlistbot.py`
- Composants : boutons de scan, filtres, sliders score, mode debug
- Backend : `analyse_tickers_realtime.py`, `dashboard.py`

Fonctions :

- `afficher_watchlist()` → composants dynamiques
- `afficher_graphiques_indicateurs(ticker)`
- `streamlit.expander()` par ticker : score, graphique, indicateurs clés, bouton de simulation/exécution

---

## 📈 Étape 5 : Simulation ou Exécution réelle

| Mode       | Modules                                            | Base de données  |
| ---------- | -------------------------------------------------- | ---------------- |
| Simulation | `simulate_trade_result.py`, `execution_simulee.py` | `trades_simules` |
| Exécution  | `strategie_scalping.py`, `executer_ordre_reel()`   | `trades`         |

📌 Code clé dans stratégie :

```python
def executer_strategie_scalping(ticker):
    if enter_breakout(ticker, price, atr):
        ordre = executer_ordre_reel(ticker)
        enregistrer_trade_auto(ticker, ordre)
        envoyer_alerte_ia(ticker, ...)
```

---

## 📝 Étape 6 : Journalisation des trades

| Table concernée  | Colonnes                                                      |
| ---------------- | ------------------------------------------------------------- |
| `trades`         | `id`, `symbol`, `price`, `volume`, `pnl`, `type`, `timestamp` |
| `trades_simules` | `symbol`, `entry`, `exit`, `gain`, `stop_loss`, `comment`     |

🔁 Appelée via : `enregistrer_trade_auto()` ou `enregistrer_trade_simule()`

---

## 🛑 Étape 7 : Clôture de journée

| Module    | `cloture_journee.py` |
| --------- | -------------------- |
| Fonction  | `cloturer_journee()` |
| Actions : |                      |

- Calculs de PnL finaux
- Export JSON/Excel possible
- Nettoyage : reset watchlist, scores, tickers ignorés
- Envoi d’une alerte Telegram récapitulative

---

## 📌 User Stories associées

- **US-WF-001** – En tant qu’utilisateur, je veux pouvoir démarrer ma session avec les bons tickers chargés automatiquement.
- **US-WF-002** – En tant qu’IA, je veux scorer tous les tickers avec mes indicateurs pour prioriser les opportunités.
- **US-WF-003** – En tant que trader, je veux simuler ou exécuter une stratégie et voir mes résultats.
- **US-WF-004** – En tant qu’utilisateur, je veux pouvoir clôturer ma journée proprement avec tous les logs sauvegardés.

---

## 📂 Fichiers sources impliqués dans ce workflow

- `ui/app_unifie_watchlistbot.py`
- `fusion/module_fusion_watchlist.py`
- `intelligence/ai_scorer.py`
- `execution/strategie_scalping.py`
- `simulation/simulate_trade_result.py`
- `db/trades.py`, `db/scores.py`
- `notifications/telegram_bot.py`
- `ui/page_modules/cloture_journee.py`

---

## 📚 Notes complémentaires

- Les seuils d’indicateurs sont ajustables dans `config/rules_auto.json`
- Tous les résultats sont sauvegardés dans `data/trades.db` pour auditabilité
- L’apprentissage IA est renforcé à partir de la base `trades_simules` (voir `learning_loop.py`)

> ✅ Ce chapitre est indispensable pour comprendre le cycle de vie complet du bot pendant une session de trading.

---


# 32_logs_et_historique_audit (1)

# 📘 Chapitre 32 – Logs, Historique, Audit & Redondance

Ce module est au cœur de la fiabilité du bot. Il assure une traçabilité complète des actions, une supervision des anomalies, et une base d’audit pour les équipes techniques, légales ou analytiques.

---

## 🎯 Objectifs du module

- Enregistrer **chaque action importante** effectuée par le bot (scan, exécution, alerte...)
- Sauvegarder tous les messages d’erreur ou de debug dans des fichiers lisibles
- Conserver un historique structuré pour la **relecture ou le replay**
- Fournir un système de **traçabilité/audit** pour l’IA, les décisions et l’exécution
- Permettre une redondance locale (fichier) et distante (base SQL ou cloud)

---

## 🗃️ Répertoire de Logs (`logs/`)

| Fichier                   | Description                                     |
| ------------------------- | ----------------------------------------------- |
| `logs/system.log`         | Journal général des actions (niveau INFO)       |
| `logs/error.log`          | Journal des erreurs critiques                   |
| `logs/trading_{date}.log` | Journal de chaque jour de trading (exécution)   |
| `logs/ia_learning.log`    | Activités du moteur IA (pondérations, feedback) |
| `logs/audit.log`          | Trace complète des décisions, avec horodatage   |

Tous les logs utilisent le format suivant :

```
[2025-06-21 15:05:33] INFO - Exécution de trade sur $CAMP à 3.12$ réussie
[2025-06-21 15:05:34] ERROR - Erreur API Finnhub : Timeout
```

Rotation automatique tous les 7 jours, avec compression des anciens fichiers (`.gz`).

---

## 🧾 Table `journal_execution`

| Champ     | Type | Description                                |
| --------- | ---- | ------------------------------------------ |
| id        | INT  | Identifiant                                |
| timestamp | TEXT | Date/heure de l’action (UTC)               |
| module    | TEXT | Nom du module (`execution`, `ia`, etc.)    |
| action    | TEXT | Action réalisée (`order_executed`, etc.)   |
| details   | TEXT | Détail structuré en JSON (données, params) |

## 🧾 Table `error_log`

| Champ     | Type | Description                               |
| --------- | ---- | ----------------------------------------- |
| id        | INT  | Identifiant                               |
| timestamp | TEXT | Date/heure                                |
| source    | TEXT | Module ou service à l’origine de l’erreur |
| niveau    | TEXT | `WARNING`, `ERROR`, `CRITICAL`            |
| message   | TEXT | Message d’erreur                          |

## 🧾 Table `audit_trail`

| Champ       | Type | Description                            |
| ----------- | ---- | -------------------------------------- |
| id          | INT  | Identifiant                            |
| horodatage  | TEXT | Datetime complet UTC                   |
| event\_type | TEXT | `DECISION_IA`, `OVERRIDE_MANUAL`, etc. |
| user\_id    | TEXT | (optionnel) identifiant utilisateur    |
| payload     | TEXT | Données brutes liées à l’événement     |

---

## 🧠 Modules Python concernés

- `utils/logger.py` – Initialisation des fichiers et niveaux de log
- `journal.py` – Insertion dans les tables SQL et consolidation
- `error_handler.py` – Catch et enrichissement des erreurs
- `audit.py` – Génération de traces pour chaque événement critique

---

## 🧩 Intégration avec le système IA

Chaque décision d’achat/vente, chaque apprentissage ou chaque ajustement est loggé avec :

- Score IA
- Paramètres déclencheurs
- Source (news, algo, manuel)
- Résultat final (succès, échec, rejet)

Permet de **tracer les biais**, **justifier les actions IA**, et **alimenter la courbe de confiance IA**.

---

## 📌 User Stories

- **US-LOG-001** – En tant qu’analyste, je veux accéder à tous les événements du bot pour relecture.
- **US-LOG-002** – En tant qu’admin, je veux être alerté immédiatement en cas d’erreur critique.
- **US-LOG-003** – En tant que responsable IA, je veux voir toutes les décisions et leurs justifications.
- **US-LOG-004** – En tant qu’architecte, je veux que les logs soient compressés, redondants et historisés.
- **US-LOG-005** – En tant que développeur, je veux injecter les logs dans un dashboard de monitoring.

---

## ✅ Cas de test

| Cas de test                                | Résultat attendu                               |
| ------------------------------------------ | ---------------------------------------------- |
| Ajout d’une ligne dans `journal_execution` | Visible immédiatement en SQL et fichier `.log` |
| Génération d’un message d’erreur           | Ajout dans `error_log` avec message horodaté   |
| Clôture journalière                        | Regroupement de tous les logs dans un seul ZIP |
| Lancement IA                               | Trace des poids IA avant/après visibles        |
| Crash système                              | Sauvegarde des logs persistée (aucune perte)   |

---

## 🛡️ Sécurité, audit, conformité

- Accès restreint aux fichiers `.log` en écriture uniquement via le bot
- Contrôle via hash d’intégrité SHA256 pour `audit.log`
- Surveillance par script cron toutes les 24h pour anomalie dans les logs
- Possibilité de remontée dans un ELK Stack (ElasticSearch, Kibana...)

---

## 🧠 Intérêt stratégique

✅ Reproductibilité des bugs et des trades ✅ Preuve légale d’exécution ou d’alerte IA ✅ Diagnostic rapide en cas de crash ou dérive comportementale ✅ Pilier de l’observabilité dans l’écosystème WatchlistBot

Souhaites-tu que je passe au chapitre suivant : **33 – Interface UI, Panneaux Dynamiques & Tableaux** ?

---


# 33_interface_ui_et_panneaux_dynamiques

# 📘 Chapitre 33 – Interface UI, Panneaux Dynamiques & Tableaux

Ce chapitre présente l’interface principale de WatchlistBot, développée avec Streamlit. Elle sert à visualiser les données critiques des tickers, interagir avec les modules IA, simuler des ordres, et piloter le bot.

---

## 🎯 Objectifs de l’interface

- Offrir une **navigation claire et fluide** entre les étapes du processus (scan → analyse → simulation → exécution → journal)
- Permettre une **visualisation détaillée** de chaque ticker, avec **graphique, score, indicateurs clés**
- Autoriser les utilisateurs à **simuler ou exécuter un ordre** directement depuis l’écran
- Afficher dynamiquement les données de l’IA, avec **valeurs apprises**, **score actuel**, **alerte visuelle/sonore**
- Offrir un tableau récapitulatif avec **pagination** pour garder une vue globale sans surcharger l’écran

---

## 🧩 Modules Python concernés

- `ui/app_unifie_watchlistbot.py` – Point d’entrée principal
- `ui/pages/` – Pages dynamiques modulaires (watchlist, IA, paramètres...)
- `ui/components/panneau_ticker.py` – Affichage détaillé d’un ticker (score, graph, infos)
- `execution/strategie_scalping.py` – Appelé pour la simulation/exécution depuis l’interface
- `intelligence/modeles_dynamiques.py` – Récupération des paramètres IA appris

---

## 🖼️ Structure visuelle

- **Sidebar** :
  - Filtres (score min, float, penny stocks…)
  - Boutons : Lancer analyse, Stopper, Importer, Clôturer
  - Options debug, affichage valeurs IA, logs

- **Corps principal** :
  - **Liste paginée de tickers** (10 à 20 par page)
  - Chaque ticker = **panneau Streamlit dépliable** avec :
    - Score global + source
    - Prix actuel, variation, volume, float
    - Graphique dynamique (via `utils_graph.py` ou yfinance)
    - Formulaire : prix d’achat, quantité, frais, SL, TP
    - Bouton : `Exécuter ordre`
    - Résultat affiché immédiatement après simulation

---

## 📊 Tableaux utilisés

- `watchlist_enrichie` : liste des tickers avec toutes les colonnes IA
- `trades_simules` : résultats des simulations en base
- `parametres_dynamiques` : stockage des valeurs apprises (mise à jour live)

---

## ⚙️ Champs affichés dans les panneaux

| Champ              | Source                  | Exemple | Description                                         |
|--------------------|--------------------------|---------|-----------------------------------------------------|
| `score`            | IA (modèle composite)    | 87      | Score agrégé basé sur les indicateurs pondérés      |
| `prix_actuel`      | Finnhub Live             | 3.21    | Dernier prix                                         |
| `volume_1m`        | Finnhub Live             | 890000  | Volume sur la dernière minute                       |
| `variation_pct`    | Finnhub / calcul interne | +23.4%  | Variation depuis l’ouverture                         |
| `float`            | Finnhub Fundamentals     | 47M     | Nombre d’actions disponibles à la vente             |
| `source`           | Watchlist import         | Jaguar  | Origine du ticker (manuel, news, IA...)             |
| `stop_loss`        | Formule dynamique        | 3.00    | SL proposé (ATR ou pourcentage)                     |
| `take_profit`      | Formule dynamique        | 3.50    | TP proposé                                           |
| `gain_potentiel`   | Calcul automatique       | +12.5%  | Différence entre prix actuel et TP - frais          |

---

## 🧠 Intégration IA – UI

L’interface permet de :
- Voir en temps réel les valeurs apprises par l’IA
- Afficher les coefficients d’importance des indicateurs (heatmap)
- Simuler une évolution de marché pour tester la robustesse du modèle IA
- Notifier l’utilisateur si une décision IA diverge du comportement habituel

---

## 📌 User Stories

- **US-UI-001** – En tant qu’utilisateur, je veux visualiser les tickers avec les scores et graphiques en un seul écran
- **US-UI-002** – En tant qu’analyste, je veux modifier le prix d’achat/vente et simuler un ordre en temps réel
- **US-UI-003** – En tant qu’admin, je veux accéder aux logs ou à l’état IA depuis l’interface sans changer de page
- **US-UI-004** – En tant qu’investisseur, je veux savoir d’où provient un ticker (manuel, IA, news)
- **US-UI-005** – En tant que testeur, je veux voir les ordres simulés s’afficher dynamiquement après clic

---

## ✅ Cas de test

| Cas de test                                 | Résultat attendu                                           |
|---------------------------------------------|------------------------------------------------------------|
| Clic sur ticker                             | Déploiement du panneau avec données                        |
| Simulation d’ordre                          | Ajout dans DB `trades_simules` + affichage dans UI        |
| Modification de paramètres IA dans backend  | Changement visible immédiatement dans l’interface          |
| Changement de filtre dans sidebar           | Rafraîchissement automatique de la liste                   |
| Importation Watchlist (fichier ou Jaguar)   | Affichage des nouveaux tickers en temps réel              |

---

## 🎨 Accessibilité et ergonomie

- Contrastes couleurs validés WCAG (Dark/Light)
- Icônes explicites pour les boutons (exécution, alerte...)
- UI multilingue prévu (FR/EN)
- Navigation fluide sans rechargement inutile (optimisation Streamlit caching)

---

## 📌 Enjeux stratégiques

- Clarté des données pour prise de décision rapide
- Intégration étroite IA–utilisateur final
- Évolutivité pour des interfaces spécialisées par rôle
- Gain de temps journalier pour l’opérateur humain
- Simulation d’ordres avant passage réel pour test en conditions réelles

---


# 34_generateur_watchlists_automatique (1)

# 📘 Chapitre 35 – Moteur de Scoring IA et Pondération Dynamique des Indicateurs

Ce module est responsable de l’évaluation des tickers identifiés, en attribuant un **score de pertinence** basé sur des indicateurs techniques, fondamentaux, et contextuels. Ce score guide ensuite les modules d’exécution, de simulation, et d’alerte.

---

## 🎯 Objectifs du moteur de scoring

- Calculer un **score unique et standardisé (sur 100)** pour chaque ticker détecté
- Pondérer dynamiquement les **indicateurs techniques et catalyseurs** selon le contexte
- Exploiter un système IA qui **apprend des trades passés** et ajuste les pondérations
- Fournir des données exploitables en priorité pour les modules d’exécution

---

## 📦 Modules Python concernés

- `intelligence/scoring_engine.py` – Calcul du score global
- `intelligence/indicateurs.py` – Récupération des indicateurs techniques
- `intelligence/model_ia.py` – Pondération dynamique et auto-ajustement
- `data/stream_data_manager.py` – Données de marché en temps réel (float, prix, volume...)
- `utils_finnhub.py` – Données fondamentales et catalyseurs externes

---

## 📊 Indicateurs utilisés dans le scoring

| Indicateur       | Rôle dans la stratégie           | Seuils critiques       | Pondération (%) par défaut |
| ---------------- | -------------------------------- | ---------------------- | -------------------------- |
| RSI (14)         | Surachat/survente                | RSI > 70 (risque pump) | 10 %                       |
| EMA 9 / EMA 21   | Confirmation de tendance         | EMA9 > EMA21           | 15 %                       |
| VWAP             | Niveau clé intraday              | Prix > VWAP            | 10 %                       |
| MACD             | Momentum court/moyen terme       | MACD > 0               | 10 %                       |
| Volume 1m / 5m   | Activité récente                 | > 500 000              | 20 %                       |
| Gap d’ouverture  | Volatilité intraday              | > 10 %                 | 10 %                       |
| Float            | Potentiel de pump                | < 200M                 | 10 %                       |
| Score catalyseur | FDA, IPO, uplisting, etc.        | > 0.7                  | 10 %                       |
| Support IA       | Résultat d’analyse IA précédente | > 0.6                  | 5 %                        |

---

## 🧠 Logique de calcul du score

```python
score = (
    poids_rsi * get_rsi_score(ticker) +
    poids_ema * get_ema_score(ticker) +
    poids_vwap * get_vwap_score(ticker) +
    poids_macd * get_macd_score(ticker) +
    poids_volume * get_volume_score(ticker) +
    poids_gap * get_gap_score(ticker) +
    poids_float * get_float_score(ticker) +
    poids_catalyseur * get_catalyseur_score(ticker) +
    poids_ia * get_meta_ia_score(ticker)
)
```

---

## 🤖 Pondération dynamique par IA

Le moteur IA ajuste automatiquement les pondérations à partir :

- Des **résultats des trades précédents (gains réels vs estimés)**
- Du type de catalyseur (ex : FDA augmente le poids du volume)
- De la configuration du marché (volatilité générale mesurée par VIX)
- Des préférences utilisateur (scalping vs swing)

Un historique est conservé dans `learning_weights.json` et mis à jour quotidiennement.

---

## 🧪 Exemples concrets de scoring

| Ticker | RSI | EMA9>21 | VWAP | Volume | Float | Score Catalyseur | Score IA | Total  |
| ------ | --- | ------- | ---- | ------ | ----- | ---------------- | -------- | ------ |
| AVTX   | 72  | Oui     | Oui  | 1.2M   | 50M   | 0.9              | 0.65     | 96/100 |
| GNS    | 60  | Non     | Oui  | 600K   | 120M  | 0.8              | 0.5      | 76/100 |

---

## 🗃️ Tables & fichiers associés

| Fichier / Table         | Description                                     |
| ----------------------- | ----------------------------------------------- |
| `meta_ia.json`          | Résultats IA préalables à la détection          |
| `learning_weights.json` | Pondérations IA mises à jour quotidiennement    |
| `historique_trades.db`  | Résultats des simulations et exécutions réelles |
| `scoring_log.csv`       | Logs des scores journaliers pour audit          |

---

## 📌 User Stories

- **US-SCORE-001** – En tant que bot, je veux attribuer un score unique à chaque ticker pour décider de l’exécution
- **US-SCORE-002** – En tant qu’IA, je veux adapter les poids des indicateurs en fonction de mes apprentissages
- **US-SCORE-003** – En tant qu’analyste, je veux comprendre pourquoi un ticker a eu un score élevé
- **US-SCORE-004** – En tant qu’utilisateur, je veux afficher le score final et les composantes dans l’interface

---

## ✅ Cas de test

| Cas de test                              | Résultat attendu                        |
| ---------------------------------------- | --------------------------------------- |
| Calcul d’un score normal                 | Score entre 0 et 100, valeur cohérente  |
| Ticker avec volume nul                   | Score faible ou exclu du processus      |
| Poids IA ajusté après 10 trades gagnants | Pondération volume/catalyseur augmentée |
| Enregistrement dans scoring\_log.csv     | Score sauvegardé avec horodatage        |

---

## 🛡️ Sécurité & robustesse

- Protection contre division par zéro ou absence de données
- Exclusion des tickers avec données manquantes (float ou prix ≤ 0)
- Pondération IA limitée entre 0 % et 30 % pour éviter les dérives
- Journalisation complète des scores et poids

---

## 📈 Impact stratégique

- Filtrage automatisé des meilleures opportunités
- Renforcement de la logique IA dans le processus décisionnel
- Réduction des faux positifs grâce au contexte dynamique
- Transparence et auditabilité complète du modèle IA utilisé

Ce module est **au cœur de l'intelligence décisionnelle du bot WatchlistBot**, car il permet d’ordonner objectivement les tickers à analyser, simuler ou exécuter.

---


# 34_generateur_watchlists_automatique - Copie

# 📘 Chapitre 34 – Générateur de Watchlists Automatique

Ce module constitue la première étape du workflow quotidien. Il est chargé de générer, enrichir et fusionner les différentes sources de tickers pour créer une **watchlist pertinente et exploitable** pour le day trading algorithmique.

---

## 🎯 Objectifs du générateur

- Fusionner plusieurs sources de tickers : **manuelle**, **IA**, **Jaguar**, **news Finnhub**, **FDA**, **uplisting**, **IPO**, etc.
- Scanner les marchés **avant ouverture** (Pre-Market) et **après clôture** (Post-Market)
- Détecter automatiquement les **hausses >50 %**, **volumes >500K**, **float < 200M**, et **anomalies carnet d’ordre**
- Générer un **fichier JSON ou DataFrame** prêt à être analysé et scoré
- Déclencher des **alertes Telegram, alarmes sonores, et affichage UI**

---

## 📦 Modules Python concernés

- `data_sources/manual_loader.py` – Lecture du fichier `tickers_manuels.json`
- `data_sources/jaguar_scraper.py` – Scraping et parsing de la watchlist Jaguar
- `data_sources/news_scanner.py` – Scan des news Finnhub sur catalyseurs (FDA, IPO, fusion, uplisting)
- `data_sources/market_screener.py` – Détection automatique via variation/volume/float
- `utils/merge_watchlists.py` – Fusion, nettoyage et normalisation des sources
- `utils_finnhub.py` – Appels API pour données fondamentales

---

## 🔎 Critères de détection Pre-Market / Post-Market

| Critère                | Valeur cible | Justification métier                              |
| ---------------------- | ------------ | ------------------------------------------------- |
| Variation (%)          | > +50 %      | Signal fort de momentum, potentiel pump           |
| Volume PreMarket       | > 500 000    | Confirmation d’intérêt massif avant marché        |
| Float                  | < 200M       | Petit float = plus de volatilité                  |
| News FDA/IPO/Uplisting | Obligatoire  | Catalyseurs puissants validés par études          |
| Anomalie carnet ordre  | Oui          | Détection optionnelle si carnet trop déséquilibré |

---

## 🧠 Exemple de fusion des sources

```json
[
  {"symbol": "HLBZ", "source": "Jaguar", "score": null},
  {"symbol": "GNS", "source": "News_FDA", "score": null},
  {"symbol": "AVTX", "source": "PostMarketScanner", "score": null},
  {"symbol": "CNSP", "source": "Manuel", "score": null}
]
```

Chaque entrée est ensuite enrichie par les modules d’analyse technique avant scoring IA.

---

## 🗃️ Tables de données utilisées

| Table                   | Description                                  |
| ----------------------- | -------------------------------------------- |
| `tickers_manuels.json`  | Liste définie manuellement par l’utilisateur |
| `jaguar_watchlist.json` | Résultat du scraping journalier              |
| `meta_ia.json`          | Résultats IA des dernières analyses          |
| `watchlist_fusionnee`   | Watchlist globale, nettoyée et triée         |

---

## 📌 User Stories

- **US-WL-001** – En tant qu’utilisateur, je veux que mes tickers manuels soient toujours inclus dans la watchlist
- **US-WL-002** – En tant que trader, je veux détecter automatiquement les tickers ayant >50 % de variation Pre-Market
- **US-WL-003** – En tant qu’analyste, je veux ajouter automatiquement les tickers contenant des news FDA ou IPO
- **US-WL-004** – En tant qu’utilisateur, je veux recevoir une alerte Telegram dès qu’un nouveau ticker est détecté Post-Market
- **US-WL-005** – En tant qu’admin, je veux voir la provenance de chaque ticker pour justifier son ajout

---

## ✅ Cas de test

| Cas de test                       | Résultat attendu                                           |
| --------------------------------- | ---------------------------------------------------------- |
| Chargement manuel                 | Les tickers dans `tickers_manuels.json` sont intégrés      |
| Détection Pre-Market à 6h00       | Tous les tickers >50 % + volume >500k sont détectés        |
| Scraping Jaguar réussi            | Les tickers extraits sont visibles dans la fusion          |
| Watchlist fusionnée               | Pas de doublons, triée par priorité ou score               |
| Affichage dans l’interface        | Tous les tickers apparaissent dans les panneaux dynamiques |
| Détection d’un nouveau ticker FDA | Envoi alerte Telegram et popup dans l’UI                   |

---

## 📣 Intégrations et alertes

- 📱 **Telegram Bot** : envoi de messages automatiques avec ticker + raison + lien graph
- 🔊 **Alarme sonore locale** : bip en cas de détection Pre/Post-Market
- 📺 **Popup Streamlit** : message coloré + focus sur ticker détecté

---

## 🧠 Stratégie IA appliquée en post-détection

Après la génération, chaque ticker est :

1. Vérifié via `valider_ticker_finnhub()` (prix > 0, données existantes)
2. Enrichi avec les indicateurs techniques principaux (RSI, EMA, VWAP, etc.)
3. Transmis au module IA pour scoring (`scorer_ticker()`) et priorisation

---

## 🛠️ Robustesse & fallback

- Si une source échoue (API, scraping), les autres sources restent actives
- Un log est généré pour chaque phase (manuelle, IA, Jaguar, news)
- L'utilisateur est alerté si une source est manquante ou désactivée

---

## 🔒 Enjeux techniques

- Ne jamais manquer un ticker pertinent, surtout avec catalyseur FDA
- Éviter les doublons, les penny stocks indésirables (si filtre activé)
- Maintenir un pipeline stable même avec des interruptions API
- Offrir une lisibilité maximale aux opérateurs avant ouverture

---

## 📈 Impact stratégique

- Gain de temps chaque matin (watchlist prête à 9h)
- Réduction des erreurs humaines (filtres automatisés)
- Alignement sur les meilleures pratiques de scalping (momentum + news)
- Amélioration continue grâce à la boucle IA

---

Ce générateur constitue la **colonne vertébrale de la détection de trades potentiels**. Sans lui, le pipeline ne peut démarrer efficacement. C’est pourquoi il est testé en priorité dans toutes les versions du bot.

---


# 34_generateur_watchlists_automatique

# 📘 Chapitre 34 – Générateur de Watchlists Automatique

Ce module constitue la première étape du workflow quotidien. Il est chargé de générer, enrichir et fusionner les différentes sources de tickers pour créer une **watchlist pertinente et exploitable** pour le day trading algorithmique.

---

## 🎯 Objectifs du générateur

- Fusionner plusieurs sources de tickers : **manuelle**, **IA**, **Jaguar**, **news Finnhub**, **FDA**, **uplisting**, **IPO**, etc.
- Scanner les marchés **avant ouverture** (Pre-Market) et **après clôture** (Post-Market)
- Détecter automatiquement les **hausses >50 %**, **volumes >500K**, **float < 200M**, et **anomalies carnet d’ordre**
- Générer un **fichier JSON ou DataFrame** prêt à être analysé et scoré
- Déclencher des **alertes Telegram, alarmes sonores, et affichage UI**

---

## 📦 Modules Python concernés

- `data_sources/manual_loader.py` – Lecture du fichier `tickers_manuels.json`
- `data_sources/jaguar_scraper.py` – Scraping et parsing de la watchlist Jaguar
- `data_sources/news_scanner.py` – Scan des news Finnhub sur catalyseurs (FDA, IPO, fusion, uplisting)
- `data_sources/market_screener.py` – Détection automatique via variation/volume/float
- `utils/merge_watchlists.py` – Fusion, nettoyage et normalisation des sources
- `utils_finnhub.py` – Appels API pour données fondamentales

---

## 🔎 Critères de détection Pre-Market / Post-Market

| Critère                | Valeur cible | Justification métier                              |
| ---------------------- | ------------ | ------------------------------------------------- |
| Variation (%)          | > +50 %      | Signal fort de momentum, potentiel pump           |
| Volume PreMarket       | > 500 000    | Confirmation d’intérêt massif avant marché        |
| Float                  | < 200M       | Petit float = plus de volatilité                  |
| News FDA/IPO/Uplisting | Obligatoire  | Catalyseurs puissants validés par études          |
| Anomalie carnet ordre  | Oui          | Détection optionnelle si carnet trop déséquilibré |

---

## 🧠 Exemple de fusion des sources

```json
[
  {"symbol": "HLBZ", "source": "Jaguar", "score": null},
  {"symbol": "GNS", "source": "News_FDA", "score": null},
  {"symbol": "AVTX", "source": "PostMarketScanner", "score": null},
  {"symbol": "CNSP", "source": "Manuel", "score": null}
]
```

Chaque entrée est ensuite enrichie par les modules d’analyse technique avant scoring IA.

---

## 🗃️ Tables de données utilisées

| Table                   | Description                                  |
| ----------------------- | -------------------------------------------- |
| `tickers_manuels.json`  | Liste définie manuellement par l’utilisateur |
| `jaguar_watchlist.json` | Résultat du scraping journalier              |
| `meta_ia.json`          | Résultats IA des dernières analyses          |
| `watchlist_fusionnee`   | Watchlist globale, nettoyée et triée         |

---

## 📌 User Stories

- **US-WL-001** – En tant qu’utilisateur, je veux que mes tickers manuels soient toujours inclus dans la watchlist
- **US-WL-002** – En tant que trader, je veux détecter automatiquement les tickers ayant >50 % de variation Pre-Market
- **US-WL-003** – En tant qu’analyste, je veux ajouter automatiquement les tickers contenant des news FDA ou IPO
- **US-WL-004** – En tant qu’utilisateur, je veux recevoir une alerte Telegram dès qu’un nouveau ticker est détecté Post-Market
- **US-WL-005** – En tant qu’admin, je veux voir la provenance de chaque ticker pour justifier son ajout

---

## ✅ Cas de test

| Cas de test                       | Résultat attendu                                           |
| --------------------------------- | ---------------------------------------------------------- |
| Chargement manuel                 | Les tickers dans `tickers_manuels.json` sont intégrés      |
| Détection Pre-Market à 6h00       | Tous les tickers >50 % + volume >500k sont détectés        |
| Scraping Jaguar réussi            | Les tickers extraits sont visibles dans la fusion          |
| Watchlist fusionnée               | Pas de doublons, triée par priorité ou score               |
| Affichage dans l’interface        | Tous les tickers apparaissent dans les panneaux dynamiques |
| Détection d’un nouveau ticker FDA | Envoi alerte Telegram et popup dans l’UI                   |

---

## 📣 Intégrations et alertes

- 📱 **Telegram Bot** : envoi de messages automatiques avec ticker + raison + lien graph
- 🔊 **Alarme sonore locale** : bip en cas de détection Pre/Post-Market
- 📺 **Popup Streamlit** : message coloré + focus sur ticker détecté

---

## 🧠 Stratégie IA appliquée en post-détection

Après la génération, chaque ticker est :

1. Vérifié via `valider_ticker_finnhub()` (prix > 0, données existantes)
2. Enrichi avec les indicateurs techniques principaux (RSI, EMA, VWAP, etc.)
3. Transmis au module IA pour scoring (`scorer_ticker()`) et priorisation

---

## 🛠️ Robustesse & fallback

- Si une source échoue (API, scraping), les autres sources restent actives
- Un log est généré pour chaque phase (manuelle, IA, Jaguar, news)
- L'utilisateur est alerté si une source est manquante ou désactivée

---

## 🔒 Enjeux techniques

- Ne jamais manquer un ticker pertinent, surtout avec catalyseur FDA
- Éviter les doublons, les penny stocks indésirables (si filtre activé)
- Maintenir un pipeline stable même avec des interruptions API
- Offrir une lisibilité maximale aux opérateurs avant ouverture

---

## 📈 Impact stratégique

- Gain de temps chaque matin (watchlist prête à 9h)
- Réduction des erreurs humaines (filtres automatisés)
- Alignement sur les meilleures pratiques de scalping (momentum + news)
- Amélioration continue grâce à la boucle IA

---

Ce générateur constitue la **colonne vertébrale de la détection de trades potentiels**. Sans lui, le pipeline ne peut démarrer efficacement. C’est pourquoi il est testé en priorité dans toutes les versions du bot.

---


# 36_moteur_execution_ordres

# Chapitre 36 – Moteur d’Exécution des Ordres Simulés & Réels

## 🎯 Objectifs du module

Permettre au bot d’exécuter automatiquement des ordres d’achat et de vente, en prenant en compte :

- les frais réels (Moomoo Canada par défaut),
- les paramètres IA (stop loss, take profit, trailing stop),
- les décisions de l’utilisateur ou du système IA,
- la journalisation dans la base de données,
- le suivi des ordres pour apprentissage futur.

## 🧱 Modules Python concernés

- `execution/strategie_scalping.py`
- `db_model.py`
- `execution/ordre_utils.py`
- `simulation/simulateur_execution.py`

## 🗂️ Tables utilisées

### Table : `trades_simules`

| Colonne         | Type    | Description                           |
| --------------- | ------- | ------------------------------------- |
| id              | INTEGER | Clé primaire                          |
| symbole         | TEXT    | Symbole de l’action                   |
| type\_ordre     | TEXT    | 'achat' ou 'vente'                    |
| prix\_execution | REAL    | Prix payé ou reçu                     |
| quantite        | INTEGER | Quantité échangée                     |
| frais\_total    | REAL    | Frais déduits                         |
| pnl\_estime     | REAL    | Gain/perte estimé                     |
| strategie       | TEXT    | Nom de la stratégie utilisée          |
| horodatage      | TEXT    | Date et heure UTC                     |
| gain\_reel      | REAL    | Si fourni plus tard par l’utilisateur |
| source          | TEXT    | 'IA', 'Utilisateur', 'Test'           |

### Table : `trades_reels`

(mêmes colonnes + statut et courtier)

## ⚙️ Logique d’exécution

```python
# Exemple simplifié d'exécution simulée avec frais Moomoo Canada
COMMISSION = max(0.0049 * quantite, 0.99)
PLATFORM_FEE = min(max(0.005 * quantite, 1.0), 0.01 * (prix * quantite))
frais_total = round(COMMISSION + PLATFORM_FEE, 2)
```

### Étapes générales

1. Vérification des fonds simulés disponibles (si applicable)
2. Calcul des frais selon profil de courtier (modifiable via config)
3. Simulation ou exécution réelle de l’ordre
4. Enregistrement dans la base (`trades_simules` ou `trades_reels`)
5. Notification IA + enregistrement apprentissage (pour IA dynamique)

## 🧠 Fonctions IA intégrées

- Calcul du **gain projeté**
- Comparaison avec le **gain simulé réel**
- Ajustement automatique des paramètres : stop loss, taille, momentum
- Suivi des ordres IA dans `journal_apprentissage`

## 🧪 User Stories

### US-EXE-01 – Simulation avec frais dynamiques

**En tant que** Trader, **je veux** simuler l’achat d’une action en prenant en compte les frais réels, **afin de** valider la rentabilité d’une stratégie IA.

**Critères d’acceptation :**

- L’ordre simulé est enregistré dans `trades_simules`
- Les frais affichés respectent les règles du courtier
- Le résultat est affiché dans l’interface utilisateur

### US-EXE-02 – Ordre réel avec retour IA

**En tant que** Utilisateur IA, **je veux** exécuter un ordre via mon courtier réel (Moomoo, IBKR), **afin de** suivre les performances de mon modèle en production.

**Critères d’acceptation :**

- L’ordre est envoyé via l’API réelle (mockée pour test)
- Le statut (`filled`, `rejected`) est journalisé
- Une alerte est envoyée si le trade est exécuté avec succès

## 🔁 Cas d’utilisation spéciaux

- Ordre conditionnel (trigger sur prix ou volume)
- Ordre annulé (latence ou timeout IA)
- Exécution en backtest historique (module simulateur)

## 🔒 Journalisation et Sécurité

Chaque ordre (simulé ou réel) est lié à :

- l’utilisateur ou IA qui l’a généré,
- l’algorithme ayant pris la décision,
- les données de contexte (score, catalyseur, etc.)

Les logs sont stockés dans :

- `logs/orders/YYYY-MM-DD.log`
- Base de données pour réutilisation en IA ou analyse manuelle

## 🧪 Tests unitaires

- `test_execution_orders.py`
  - test\_frais\_calculés\_correctement
  - test\_enregistrement\_bdd\_simulée
  - test\_exécution\_mock\_réelle
  - test\_alerte\_post\_trade
  - test\_gain\_estime\_vs\_reel

## ✅ Résumé

Ce module centralise l'exécution automatique sécurisée d'ordres dans le bot. Il garantit la cohérence entre simulation, IA et interface, tout en assurant traçabilité, apprentissage et adaptation continue.

---

⏭️ Suivant : **Chapitre 37 – Module d’Apprentissage Automatique post-trade** ?

---


# 38_suivi_performances_dashboard

# Chapitre 38 – Suivi des Performances & Dashboard IA

## 🎯 Objectif du module

Offrir un tableau de bord complet de suivi des performances du bot de trading IA, permettant une évaluation claire, visuelle et temps réel de l’efficacité des stratégies exécutées, des scores IA et des résultats simulés ou réels.

---

## 🧱 Modules Python concernés

- `dashboard.py`
- `simulation/stats_kpi.py`
- `db_model.py`
- `utils_graph.py`
- `streamlit_pages/dashboard_performance.py`

---

## 🗂️ Tables utilisées

### Table : `trades_simules`

| Colonne      | Type | Description                            |
| ------------ | ---- | -------------------------------------- |
| symbole      | TEXT | Nom du ticker                          |
| date\_trade  | TEXT | Date UTC de la simulation              |
| gain\_simule | REAL | Gain ou perte estimé                   |
| strategie    | TEXT | Breakout, Pullback, etc.               |
| score\_ia    | REAL | Score IA au moment du trade            |
| statut       | TEXT | Statut du trade : success, échec, skip |

### Table : `trades_reels`

| Colonne     | Type | Description            |
| ----------- | ---- | ---------------------- |
| symbole     | TEXT | Titre du trade réel    |
| date\_trade | TEXT | Date UTC               |
| gain\_reel  | REAL | Gain ou perte constaté |
| sl\_price   | REAL | Stop loss utilisé      |
| tp\_price   | REAL | Take profit utilisé    |

---

## 📊 Indicateurs de performance

- ✅ Nombre de trades exécutés (par jour, semaine, mois)
- 💰 Profit net cumulé
- 📉 Maximum drawdown (max perte en %)
- 📈 Taux de réussite global et par stratégie
- 🔍 Moyenne du gain par trade
- 🧠 Score IA moyen des trades gagnants
- ⚖️ Ratio gain/perte (Risk Reward)

---

## 🧠 Visualisation (Streamlit)

- Graphiques `Plotly` :
  - Barres pour gain journalier
  - Courbe cumulée du capital
  - Pie chart répartition stratégie gagnante
- Filtres : par période, par stratégie, par score IA
- Section : "Top 5 des gains" / "Top 5 des pertes"

---

## 🧾 Exports et archivage

- 📁 Export CSV des performances quotidiennes (`performance_YYYYMMDD.csv`)
- 📄 Export PDF du dashboard à la clôture journalière

---

## ⚙️ Fichiers de configuration et fonctions clés

```python
# simulation/stats_kpi.py

def calculer_kpi(trades):
    taux_reussite = ...
    profit_total = ...
    drawdown = ...
    return {"success_rate": taux_reussite, "profit": profit_total, "max_drawdown": drawdown}

# dashboard.py

def generer_dashboard(df):
    fig1 = generer_courbe_capital(df)
    fig2 = generer_repartition_strategie(df)
    ...
```

---

## 📌 KPI Suivis par IA

- Impact moyen de chaque stratégie
- Gain moyen selon score IA [<70, 70-90, >90]
- Historique des versions de `meta_ia.json` utilisées

---

## 🧪 User Stories

### US-DASH-01 – Visualiser les performances quotidiennes

**En tant que** trader IA, **je veux** visualiser mes gains et pertes par jour, **afin de** piloter mon activité.

**Critères :**

- Accès direct à la performance du jour
- Filtrage par type de trade (IA / manuel / simulateur)

### US-DASH-02 – Calcul automatique des KPI

**En tant que** développeur IA, **je veux** automatiser le calcul des KPI de performance, **afin de** détecter toute dérive de stratégie.

**Critères :**

- Taux de réussite < 50% = alerte
- Drawdown > 10% = alerte IA

### US-DASH-03 – Export et archivage des performances

**En tant que** analyste, **je veux** exporter les résultats en CSV et PDF, **afin de** conserver une trace documentaire.

**Critères :**

- Génération quotidienne automatique du CSV à la clôture
- Export PDF disponible dans l’interface

---

## ✅ Résumé

Le module de dashboard et suivi de performance permet un pilotage global du bot de trading. Il consolide les résultats, détecte les dérives, alimente l’apprentissage IA, et fournit des rapports visuels à forte valeur pour les traders, les analystes, et les développeurs IA.

---


# 39_journalisation_et_rapports

# Chapitre 39 – Journalisation Complète & Rapports Quotidiens

## 🎯 Objectif du module

Assurer la traçabilité complète de toutes les actions du bot IA (exécution, erreurs, IA, utilisateur), générer des rapports quotidiens exploitables par tous les intervenants (traders, devs, DBA, responsables sécurité) et permettre l’audit, le support et l’analyse post-mortem.

---

## 📚 Modules Python concernés

- `utils_logger.py`
- `db_model.py`
- `rapport/generateur_rapport.py`
- `journal.py`
- `cloture.py`

---

## 📁 Fichiers de journalisation générés

- `journal_execution.csv` : ordres simulés/réels exécutés, détails complet
- `journal_erreurs.log` : erreurs critiques ou exception capturées
- `journal_apprentissage.json` : ajustements IA post-trade
- `journal_user.json` : actions manuelles utilisateur dans l’interface
- `rapport_cloture_YYYYMMDD.pdf` : synthèse quotidienne multi-source

---

## 🗂️ Tables SQLite concernées

### `journal_execution`

| Colonne     | Type    | Description                        |
| ----------- | ------- | ---------------------------------- |
| id          | INTEGER | ID unique                          |
| symbole     | TEXT    | Ticker concerné                    |
| type\_ordre | TEXT    | achat / vente / simulation / rejet |
| date\_exec  | TEXT    | Date UTC                           |
| prix\_exec  | REAL    | Prix exécuté                       |
| quantite    | INTEGER | Volume                             |
| strategie   | TEXT    | Stratégie utilisée                 |
| statut      | TEXT    | success / échec / pending          |

### `journal_erreurs`

| Colonne   | Type | Description                       |
| --------- | ---- | --------------------------------- |
| id        | INT  | Clé primaire                      |
| timestamp | TEXT | Heure UTC                         |
| module    | TEXT | Nom du fichier concerné           |
| message   | TEXT | Stacktrace ou message utilisateur |

### `journal_user`

| Colonne  | Type | Description                     |
| -------- | ---- | ------------------------------- |
| id       | INT  | Clé primaire                    |
| user\_id | TEXT | Identifiant utilisateur         |
| action   | TEXT | Ajout ticker, changement filtre |
| valeur   | TEXT | Valeur de l’action              |
| date     | TEXT | Date de l’action                |

---

## 🧾 Formats d’export automatique

- `.csv` pour journal lecture rapide et tableur
- `.json` pour usage technique ou API
- `.pdf` pour archivage quotidien avec synthèse visuelle

```python
# Extrait simplifié - cloture.py

def generer_rapport_pdf(date):
    data = lire_journaux_du_jour(date)
    render_pdf(data, output=f"rapport_cloture_{date}.pdf")
```

---

## 📈 Données intégrées dans le rapport PDF journalier

- Nombre total de trades (réussis, échoués)
- Performance globale (PnL du jour)
- Liste des erreurs critiques
- Liste des symboles à haut score IA
- Ajustements IA effectués ce jour
- Actions manuelles utilisateur

---

## 🧪 User Stories

### US-LOG-01 – Journalisation des actions système

**En tant que** développeur, **je veux** enregistrer chaque ordre exécuté, **afin de** pouvoir le relire en cas d’erreur ou de débogage.

**Critères :**

- Chaque ordre déclenche une écriture dans `journal_execution`
- Le statut (success / fail) est toujours renseigné

### US-LOG-02 – Suivi des erreurs critiques

\*\*En tant qu’\*\*administrateur, **je veux** consulter facilement les erreurs, **afin de** anticiper les crashs ou corriger les bugs.

**Critères :**

- Le fichier `journal_erreurs.log` est généré en temps réel
- Les erreurs contiennent timestamp, stacktrace et module

### US-LOG-03 – Génération de rapport PDF quotidien

**En tant que** responsable IA, **je veux** recevoir un PDF récapitulatif journalier, **afin de** suivre les résultats, incidents et ajustements IA.

**Critères :**

- Le PDF contient les 6 sections listées ci-dessus
- Il est automatiquement sauvegardé dans `rapports/`

---

## ✅ Résumé

Le système de journalisation et de génération de rapports est un pilier de traçabilité du bot. Il permet à chaque acteur (développeur, trader, support, analyste IA) de suivre, comprendre et corriger le comportement du système en toute transparence. Chaque donnée est horodatée, centralisée et exportable pour archivage, audit ou post-analyse.

---


# Chapitre_40_Securite

# Chapitre 40 – Sécurité, Authentification et Contrôle d’Accès

## 🎯 Objectif du module

Garantir un accès sécurisé à toutes les fonctionnalités critiques du bot WatchlistBot en intégrant un système de **login**, de **gestion des rôles**, de **journalisation des connexions** et de **contrôle dynamique des permissions** dans l’interface.

...

## ✅ Résumé

Ce module apporte une base solide de sécurité, extensible vers des systèmes professionnels.

---


# chapitre_41_assistant_vocal

---
