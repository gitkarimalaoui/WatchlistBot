# 📘 Chapitre 20 – AI Performance Tracking (Suivi de Performance IA)

## 🎯 Objectif de ce module

Ce module permet de suivre les performances réelles de l’intelligence artificielle dans la durée. Il enregistre les résultats des décisions IA, calcule la rentabilité cumulée, et évalue la pertinence du scoring à travers des KPIs visuels.

## 🧠 Modules et acteurs impliqués

* **UI** : Présente les graphiques de performance IA
* **Bot** : Met à jour les données de résultats en fin de journée
* **AI** : Compare ses propres prédictions avec les résultats réels
* **DB** : Stocke les statistiques et courbes de suivi
* **Trader** : Utilise les courbes pour ajuster ou valider les stratégies

## 🗃️ Tables utilisées

| Table                | Description                                |
| -------------------- | ------------------------------------------ |
| `ai_performance_log` | Données journalières des résultats IA      |
| `ai_parameters`      | Paramètres utilisés lors de chaque session |
| `trades_simules`     | Résultats des trades simulés               |
| `learning_log`       | Historique des ajustements IA              |

## 📜 User Stories de cet EPIC

* US-AI-TRACK-001 : Afficher l’évolution journalière du PnL IA
* US-AI-TRACK-002 : Comparer les performances IA vs baseline manuelle
* US-AI-TRACK-003 : Identifier les périodes de forte performance IA
* US-AI-TRACK-004 : Enregistrer les résultats dans `ai_performance_log`
* US-AI-TRACK-005 : Corréler les scores IA avec les gains réalisés
* US-AI-TRACK-006 : Visualiser les KPIs dans un tableau de bord
* US-AI-TRACK-007 : Générer une alerte si sous-performance prolongée
* US-AI-TRACK-008 : Lister les meilleurs scores IA sur 30 jours
* US-AI-TRACK-009 : Mettre en pause l’IA si performance trop faible
* US-AI-TRACK-010 : Partager automatiquement les résultats par email ou Telegram

## ⚙️ Conditions critiques

* Si IA en mode désactivé → aucune donnée collectée
* Si erreur dans les résultats simulés → rejet du calcul journalier
* Historique incomplet → KPI incorrects ou absents

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_20_ai_performance_tracking.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour le module 'AI Performance Tracking' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : enregistrement, calculs, affichage KPIs, alerte
Flux alternatifs si données manquantes ou IA inactive
```

## ⚠️ Limites connues

* Certains indicateurs sensibles à la volatilité extrême
* Pas encore de filtrage par stratégie IA
* Performance parfois biaisée par les trades manuels ajoutés

## 🔁 Références croisées

| Fonction     | EPIC concerné               |
| ------------ | --------------------------- |
| IA Engine    | EPIC 16 – Learning Engine   |
| Simulation   | EPIC 13 – Simulation Trades |
| UI Dashboard | EPIC 19 – UI Multi-Modules  |

## 💡 Leçon clé

Une IA sans suivi devient une boîte noire. Le suivi de performance transforme l’intelligence artificielle en un outil mesurable, ajustable, et digne de confiance.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 18](../images/bpmn_epic_18_ia_image_graphique.png)
