# 📘 Chapitre 10 – Graphiques Dynamiques (Live Charting)

## 🎯 Objectif de ce module

Ce module permet d’afficher en temps réel les graphiques des tickers retenus, combinant données historiques (YFinance) et données live (Finnhub), avec overlay des indicateurs et des zones critiques IA.

## 🧠 Modules et acteurs impliqués

* **UI** : Affiche les graphiques, mise à jour dynamique
* **Bot** : Récupère les données YFinance et les données live Finnhub
* **AI** : Fournit des signaux à superposer (support, résistance, cassure)
* **DB** : Optionnel pour le cache ou l’historique
* **Trader** : Observe et agit sur base visuelle

## 🗃️ Tables utilisées

| Table         | Description                              |
| ------------- | ---------------------------------------- |
| `chart_cache` | Données brutes pour chargement rapide    |
| `ia_zones`    | Zones identifiées par l’IA pour overlays |
| `tickers`     | Liste des tickers affichables            |

## 📜 User Stories de cet EPIC

* US-CHART-001 : Charger le graphique historique (YFinance)
* US-CHART-002 : Charger les données live (Finnhub)
* US-CHART-003 : Afficher le graphique dans l’interface avec MAJ automatique
* US-CHART-004 : Superposer les zones IA (support, cassure, alerte)
* US-CHART-005 : Afficher un graphique par ticker sélectionné
* US-CHART-006 : Optimiser le rafraîchissement selon quota API
* US-CHART-007 : Sauvegarder les erreurs d’appel en cache
* US-CHART-008 : Permettre au trader de figer un graphique pour comparaison
* US-CHART-009 : Ajuster l’UI en fonction de la taille d’écran
* US-CHART-010 : Afficher les volumes, EMA, VWAP en overlay

## ⚙️ Conditions critiques

* Ticker non valide → pas d’affichage
* API Finnhub en erreur → fallback partiel YFinance
* Rafraîchissement bloqué si quota dépassé

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_10_graphiques_dynamiques.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour le module 'Graphiques Dynamiques' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : récupération de données, superposition IA, affichage dynamique
Flux alternatifs : API indisponible, cache, fallback
```

## ⚠️ Limites connues

* Dépendance à la qualité des APIs externes (latence, quota)
* Chargement parfois lent si trop de tickers affichés en parallèle
* IA graphique encore basique (limité aux overlays simples)

## 🔁 Références croisées

| Fonction     | EPIC concerné                |
| ------------ | ---------------------------- |
| Analyse      | EPIC 09 – Analyse IA         |
| Interface    | EPIC 11 – Interface Trading  |
| IA graphique | EPIC 18 – IA Image Graphique |

## 💡 Leçon clé

Le visuel reste un levier critique pour les traders humains. Associer l’analyse IA et la représentation graphique dynamique donne une compréhension instantanée de l’opportunité.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 10](../images/bpmn_epic_10_graphiques_dynamiques.png)
