
# 📘 MODULE 1 – Interface Principale `app_unifie_watchlistbot.py`

## 🎯 Objectif du module
Interface principale utilisateur du bot WatchlistBot (Version V7+). Ce module centralise :
- L’analyse des tickers par GPT
- L’affichage dynamique de la watchlist avec données Finnhub
- L’injection des données Moomoo (Jaguar)
- La gestion manuelle des tickers
- La navigation vers les blocs Roadmap, Entreprise et Assistant Personnel

---

## 🧱 Architecture technique

### 📁 Fichier principal :
- `ui/app_unifie_watchlistbot.py`

### 📂 Dépendances internes :
| Fichier                               | Rôle principal                                      |
|---------------------------------------|-----------------------------------------------------|
| `scripts/run_chatgpt_batch.py`        | Lance l’analyse GPT et injecte les scores           |
| `scripts/scraper_jaguar.py`           | Scrape les tickers Jaguar depuis Moomoo            |
| `scripts/load_watchlist.py`           | Injecte les tickers extraits dans la base          |
| `utils/utils_finnhub.py`              | Récupère prix, float, volume, graphes live         |
| `ui/utils_affichage_ticker.py`         | Affiche les tickers et graphiques     |
| `intelligence/ai_scorer.py`            | Calcule le score IA global            |
| `utils/utils_graph.py`                 | Chargement historique & intraday      |
| `roadmap_ui.py`                       | Interface de gestion des EPICs / tâches / US       |
| `query_entreprise_db.py`             | Affiche KPI, cas d’usage et modules CRM/IA         |

---

## 🗃 Bases de données utilisées

### `trades.db`
| Table             | Description                                     |
|------------------|-------------------------------------------------|
| `watchlist`       | Liste des tickers à surveiller/analyser        |
| `news_score`      | Résultats des analyses GPT                     |
| `chatgpt_history` | Historique des prompts et réponses ChatGPT     |

### `entreprise.db`
| Table              | Description                                 |
|--------------------|---------------------------------------------|
| `portfolio_modules`| Liste des modules IA/CRM avec catégories    |
| `use_cases`        | Cas d’usage par région et secteur           |
| `revenue_sources`  | Sources de revenu                           |
| `kpi_targets`      | Objectifs chiffrés (KPI)                    |

---

## 🔄 Flux fonctionnels

```mermaid
flowchart TD
  A[UI WatchlistBot] -->|Click| B[Scraper Jaguar]
  A -->|Click| C[Analyse GPT]
  A -->|Saisie| D[Ajout manuel]
  B --> E[watchlist_jaguar.txt]
  E --> F[load_watchlist.py]
  F --> G[(watchlist DB)]
  C --> H[run_chatgpt_batch.py]
  H --> I[(news_score DB)]
  A --> J[query_entreprise_db.py] --> K[(entreprise.db)]
  A --> L[roadmap_ui.py] --> M[(project_tracker.db)]
```

---

## 🧪 User Stories associées
- #001 Ajouter un ticker manuellement depuis l’interface
- #002 Lancer l’analyse GPT (`run_chatgpt_batch.py`)
- #003 Scraper les posts Jaguar depuis Moomoo (`scraper_jaguar.py`)
- #004 Injecter la watchlist dans la base (`load_watchlist.py`)
- #005 Calculer le score IA des tickers (`intelligence.ai_scorer`)
- #006 Afficher chaque ticker et ses graphes (`ui/utils_affichage_ticker.py`)
- #007 Générer les courbes intraday et historiques (`utils/utils_graph.py`, `utils/utils_finnhub.py`)
- #008 Naviguer vers Roadmap ou Entreprise (`roadmap_ui.py`)

---

## ✅ État du module

- ✅ Tous les fichiers nécessaires reçus
- ✅ Vérification de compatibilité terminée
- ✅ Analyse fonctionnelle complète
- 🟢 Prêt à l'intégration avec modules suivants

---

## 📌 Historique des mises à jour

- **2025-05-21** : Création initiale du document


---

## 🗂 Chemin local de référence (ordinateur utilisateur)

**Répertoire racine local :**
```
Ce PC > Bureau > python > projet AI > BOTV7 > BOTV7
```

**Exemples de chemins complets :**
- `ui/app_unifie_watchlistbot.py`
- `ui/utils_affichage_ticker.py`
- `intelligence/ai_scorer.py`
- `utils/utils_graph.py`
- `scripts/run_chatgpt_batch.py`
- `scripts/scraper_jaguar.py`
- `utils/utils_finnhub.py`
- `data/trades.db`
- `data/entreprise.db`
Les scripts en doublon (versions « x ») ont été supprimés pour simplifier ces chemins.

- `project_doc/` *(documentation des EPICs, images BPMN, etc.)*
- `VERSION_HISTORY.md` *(journal des versions stable)*

**Règle de synchronisation :**
À chaque étape de validation d’un module, le chemin **exploité dans l’environnement Streamlit** et **le chemin local sur l’ordinateur** doivent correspondre.

Ainsi, toute divergence (ex. : fichier déplacé, renommé ou en double) sera signalée ici dans la section de documentation.

