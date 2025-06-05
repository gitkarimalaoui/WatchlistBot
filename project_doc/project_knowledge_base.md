
# 🧠 Base de Connaissance – Projet WatchlistBot V7.03

---

## 📌 Contexte et Objectif

WatchlistBot est une IA modulaire conçue pour le day trading haute volatilité. Sa logique repose sur :
- L'import dynamique de tickers,
- Le scoring intelligent basé sur des catalyseurs (FDA, float, volume, %gain),
- Une interface Streamlit simple et interactive,
- Une IA auto-apprenante pilotée par journalisation.

---

## 🔖 Versions & Fichiers de Référence

| Type | Nom | Rôle |
|------|-----|------|
| 📦 Code base | BOTV7.zip | Projet technique principal |
| 🗂 User Stories | USER_STORIES_ORGANISEES_PAR_EPIC.xlsx | Source unique des US/EPICs |
| 🧠 Stratégie | JaguarTrainingDailyTrading.docx | Référence cognitive & scalping |
| 📘 Documentation | WatchlistBot_V6_Documentation.pdf | Historique projet & logique V6 |
| 🧭 Structure du livre | project_structure.md | Plan global du projet |
| 🔄 Feuille de route | roadmap_sync.json | Synchronisation dynamique bot / IA |
| 💬 Prompts IA | /prompts/ | Génération assistée IA |
| 📈 BPMN | /images/ | Diagrammes par EPIC |

---

## ✅ Règles prises en compte dans V7.03

- Base SQLite `trades.db` : remplace CSV
- Scoring IA basé sur :
  - `float < 200M`
  - `volume > 500K`
  - `gain% ≥ 50%`
  - `news FDA, merger, IPO, uplisting`
  - `EMA/VWAP breakout`
- UI via Streamlit (ajout manuel, import, fusion, graphes)
- Alerte Telegram via bot privé
- Logging + simulation IA automatique
- BPMN générés par EPIC (21 au total)

---

## 🔧 Variables clés et logique IA (figée à ce stade)

| Nom | Description | Valeur par défaut |
|-----|-------------|-------------------|
| `score_threshold` | Seuil minimal de score pour alerte | 5 |
| `min_float` | Float maximal accepté | 200_000_000 |
| `min_volume` | Volume minimal journalier | 500_000 |
| `gain_min_percent` | %gain minimal intraday | 50% |
| `ema_periods` | Périodes EMA utilisées | 9 / 21 |
| `pattern_check_window` | Fenêtre de détection graphique | 5 dernières minutes |
| `ai_model_type` | Type IA utilisé pour le score | DecisionTreeClassifier (prévu V8) |

---

## 🔁 Améliorations futures prévues

| Phase | Évolution | Statut |
|-------|-----------|--------|
| V8 | Connexion broker réel (IBKR, Alpaca) | Planifiée |
| V8 | Simulation + auto-trade avec feedback | Planifiée |
| V8 | Reconnaissance visuelle de pattern (IA image) | Design |
| V9 | Clonage multi-stratégie (santé, crypto) | En réflexion |
| V9 | Auto-optimisation selon journal | En cours |
| V10 | Publication publique du bot | Objectif final |

---

## 🧠 Sources de vérité & navigation rapide

- `/project_doc/project_structure.md` → Plan du livre
- `/project_doc/roadmap_sync.json` → Tâche actuelle + prompt
- `/project_doc/prompts/` → Tous les prompts utilisés
- `/project_doc/images/` → BPMN et schémas
- `/project_doc/annexes/modules_python.md` → Détail des modules
- `/project_doc/project_knowledge_base.md` → Ce fichier (SSOT)
