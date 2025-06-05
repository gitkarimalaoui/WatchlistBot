# 📘 Chapitre 19 – UI Multi-Modules (Interface Unifiée)

## 🎯 Objectif de ce module

Ce module vise à regrouper dans une seule interface Streamlit tous les composants clés du bot (watchlist, scoring, graphes, simulations, apprentissage, paramètres). Il permet une navigation fluide, centralisée et modulaire pour le trader.

## 🧠 Modules et acteurs impliqués

* **UI** : Interface principale avec onglets ou panneaux dynamiques
* **Bot** : Fournit les données, exécute les actions liées aux boutons UI
* **AI** : Affiche ses scores et paramètres dans les sections IA
* **DB** : Sert les données selon les modules (watchlist, journal, trades…)
* **Trader** : Utilise l’interface pour piloter tout le bot depuis un seul écran

## 🗃️ Tables utilisées

| Table           | Description                                 |
| --------------- | ------------------------------------------- |
| `tickers`       | Données de la watchlist affichées dans l’UI |
| `trades`        | Données simulées ou réelles affichées       |
| `ai_parameters` | Paramètres IA visibles dans l’onglet IA     |
| `logs`          | Journal affiché dans le tableau de bord     |

## 📜 User Stories de cet EPIC

* US-UI-001 : Accéder à une interface centralisée et fluide
* US-UI-002 : Naviguer entre les modules via onglets ou menu latéral
* US-UI-003 : Afficher les tickers avec leur score, provenance, graphique
* US-UI-004 : Exécuter une simulation depuis l’écran principal
* US-UI-005 : Visualiser les journaux et logs en temps réel
* US-UI-006 : Modifier dynamiquement les paramètres de scoring IA
* US-UI-007 : Générer une alerte ou un log depuis un bouton de l’UI
* US-UI-008 : Utiliser un bouton “Clôturer la journée” accessible globalement
* US-UI-009 : Synchroniser tous les modules sans recharger la page
* US-UI-010 : Afficher l’état actuel de l’IA (mode actif, veille, apprentissage)

## ⚙️ Conditions critiques

* Dépendance forte à la latence API (rafraîchissement live)
* Mauvais découpage des modules UI → surcharge ou ralentissement
* Mauvaise synchronisation entre scoring, graphes et logs → risque d’erreur d’affichage

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_19_ui_multi_modules.png`

## 🧠 Prompt IA utilisé

```
Génère le diagramme BPMN pour le module 'UI Multi-Modules' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : navigation, affichage, simulation, logs, interaction
Flux normal + désynchronisation potentielle ou erreur d’interface
```

## ⚠️ Limites connues

* Pas encore de version mobile responsive complète
* Certains onglets ralentissent si trop d’éléments actifs (graphes live)
* Rafraîchissement automatique non optimisé à ce stade

## 🔁 Références croisées

| Fonction | EPIC concerné             |
| -------- | ------------------------- |
| Journal  | EPIC 12 – Journalisation  |
| Scoring  | EPIC 09 – Analyse IA      |
| Clôture  | EPIC 15 – Clôture Journée |

## 💡 Leçon clé

Une interface fluide et modulaire est la clé de l’efficacité en day trading. Elle permet de tout piloter en un seul clic, avec un maximum d’informations visibles sans surcharge cognitive.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 19](../images/bpmn_epic_19_ui_multi_modules.png)
