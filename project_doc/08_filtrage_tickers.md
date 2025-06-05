# 📘 Chapitre 08 – Filtrage des Tickers

## 🎯 Objectif de ce module

Ce module a pour but d'appliquer un ensemble de filtres déterminants aux tickers collectés avant leur passage à l’analyse IA ou à la simulation. L’objectif est de ne conserver que les tickers pertinents selon des critères précis de day trading.

## 🧠 Modules et acteurs impliqués

* **UI** : Affiche les tickers filtrés ou rejetés
* **Bot** : Applique les règles de filtrage automatique
* **AI** : Peut influencer ou affiner certains seuils dynamiques
* **DB** : Stocke les tickers retenus et rejetés
* **Trader** : Peut activer un mode debug pour voir les raisons de rejet

## 🗃️ Tables utilisées

| Table              | Description                             |
| ------------------ | --------------------------------------- |
| `tickers`          | Liste des tickers en cours d’analyse    |
| `tickers_filtered` | Liste des tickers exclus après filtrage |
| `tickers_log`      | Enregistrement des filtres appliqués    |

## 📜 User Stories de cet EPIC

* US-FILTER-001 : Appliquer un filtre sur le volume > 500K
* US-FILTER-002 : Écarter les penny stocks (si désactivé dans l’UI)
* US-FILTER-003 : Rejeter les tickers à prix nul ou incohérent
* US-FILTER-004 : Appliquer un filtre sur la variation % > 5 %
* US-FILTER-005 : Écarter les floats > 200M si activé
* US-FILTER-006 : Stocker les tickers filtrés dans `tickers_filtered`
* US-FILTER-007 : Logger les raisons de rejet dans `tickers_log`
* US-FILTER-008 : Afficher les tickers retenus dans l’interface
* US-FILTER-009 : Permettre à l'utilisateur d’activer le mode debug
* US-FILTER-010 : Appliquer les règles conditionnelles selon la stratégie IA

## ⚙️ Conditions critiques

* Un ticker sans volume ou prix → rejet automatique
* Un ticker déjà filtré → pas analysé 2 fois
* En cas de flottement borderline → message d’avertissement en debug
* Les critères peuvent être modifiés dans l’interface de configuration

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_08_filtrage_tickers.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour le module 'Filtrage des Tickers' avec :
- Couloirs : UI, Bot, AI, DB, Trader
- Filtres : volume, prix, float, variation %
- Flux alternatif en cas de rejet
- Affichage et logs dans l’interface
```

## ⚠️ Limites connues

* Certains tickers passent les filtres mais sont peu volatils ensuite
* Nécessite une calibration fine des seuils par stratégie
* En mode debug actif, surcharge d’affichage possible

## 🔁 Références croisées

| Fonction | EPIC concerné              |
| -------- | -------------------------- |
| Import   | EPIC 05 – Watchlist Import |
| Scoring  | EPIC 09 – Analyse IA       |
| Journal  | EPIC 12 – Journalisation   |

## 💡 Leçon clé

Un bon filtrage évite une surcharge de traitement et de faux signaux. Il maximise la pertinence des tickers envoyés à l’IA ou aux stratégies de trading.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 08](../images/bpmn_epic_08_filtrage_tickers.png)
