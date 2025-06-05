# 📘 Chapitre 21 – Objectif 100K & Pilotage Stratégique

## 🎯 Objectif de ce module

Ce module fournit une vision stratégique et des outils de pilotage permettant d’aligner les décisions du trader et de l’IA avec un objectif précis de gains : atteindre 100 000 \$ dans un délai déterminé. Il assure le suivi des KPIs clés et propose des ajustements tactiques.

## 🧠 Modules et acteurs impliqués

* **UI** : Affiche les objectifs, la progression et les alertes de pilotage
* **Bot** : Centralise les données de performance et alerte en cas d’écart
* **AI** : Ajuste ses stratégies ou son scoring en fonction des résultats globaux
* **DB** : Stocke les objectifs, les étapes intermédiaires, les écarts
* **Trader** : Pilote les priorités et peut modifier les cibles de gains

## 🗃️ Tables utilisées

| Table             | Description                                     |
| ----------------- | ----------------------------------------------- |
| `strategic_goals` | Objectifs chiffrés par palier                   |
| `performance_kpi` | Suivi journalier et cumulatif des résultats     |
| `adjustments_log` | Modifications manuelles ou IA dans la stratégie |
| `alerts`          | Alerte déclenchée en cas d’écart significatif   |

## 📜 User Stories de cet EPIC

* US-GOAL-001 : Fixer un objectif global de gain (ex. 100 000 \$)
* US-GOAL-002 : Fractionner cet objectif en paliers mensuels et hebdos
* US-GOAL-003 : Afficher la progression actuelle dans un dashboard
* US-GOAL-004 : Alerter en cas de sous-performance prolongée
* US-GOAL-005 : Permettre de réviser dynamiquement les objectifs
* US-GOAL-006 : Corréler les performances aux décisions IA
* US-GOAL-007 : Activer un plan de redressement automatique
* US-GOAL-008 : Journaliser tous les ajustements stratégiques
* US-GOAL-009 : Proposer des suggestions IA pour améliorer la rentabilité
* US-GOAL-010 : Exporter un rapport hebdomadaire de pilotage

## ⚙️ Conditions critiques

* Objectif mal défini → les KPIs deviennent incohérents
* IA non synchronisée avec le plan stratégique → fausses décisions
* Si dashboard désactivé → aucun suivi des alertes de pilotage

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_21_objectif_100k_pilotage.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour l’EPIC 'Objectif 100k & Pilotage' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : fixer objectif, suivre progression, alerte, ajustement IA
Flux alternatifs si non atteinte ou désalignement stratégique
```

## ⚠️ Limites connues

* Le plan stratégique n’intègre pas encore la volatilité du marché
* Pas encore de système d’incitation IA basé sur l’atteinte de résultats
* Le seuil d’alerte est encore manuel, non dynamique

## 🔁 Références croisées

| Fonction     | EPIC concerné              |
| ------------ | -------------------------- |
| IA Engine    | EPIC 16 – Learning Engine  |
| Performance  | EPIC 20 – AI Tracking      |
| UI Dashboard | EPIC 19 – UI Multi-Modules |

## 💡 Leçon clé

Fixer un objectif clair permet d’aligner l’humain et la machine. Le pilotage stratégique transforme le bot en véritable copilote financier orienté résultats.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 21](../images/bpmn_epic_21_objectif_100k_pilotage.png)
