# 📘 Chapitre 24 – Risk Management & Stop‑Loss Guard

## 🎯 Objectif de ce module

Protéger le capital en calculant automatiquement la taille de position selon le risque défini, en plaçant des stop‑loss, et en suspendant l’achat de nouvelles positions en cas de drawdown important.

## 🧠 Modules et acteurs impliqués

* **UI** : Paramétrage du pourcentage de risque par trade et des seuils de drawdown
* **Bot** : Calcule la taille de position, place et surveille les stop‑loss
* **AI** : Ajuste dynamiquement les niveaux de stop‑loss selon la volatilité
* **DB** : Stocke les paramètres de risque et les exécutions de stop‑loss
* **Trader** : Modifie manuellement les paramètres de risk management

## 🗃️ Tables utilisées

| Table             | Description                                  |
| ----------------- | -------------------------------------------- |
| `risk_parameters` | Seuils de risque (% par trade, drawdown max) |
| `stop_loss_log`   | Journal des stop‑loss placés et déclenchés   |

## 📜 User Stories de cet EPIC

* US-RISK-001 : En tant que trader, je veux définir le % de risque par trade
* US-RISK-002 : En tant que bot, je veux calculer la taille de position selon le risque
* US-RISK-003 : En tant que bot, je veux placer un stop‑loss automatiquement après ouverture
* US-RISK-004 : En tant que AI, je veux ajuster le stop‑loss selon la volatilité du marché
* US-RISK-005 : En tant que DB, je veux logguer chaque placement et activation de stop‑loss
* US-RISK-006 : En tant que trader, je veux être alerté immédiatement si un stop‑loss est déclenché
* US-RISK-007 : En tant que bot, je veux suspendre les nouveaux ordres si drawdown > seuil
* US-RISK-008 : En tant que UI, je veux visualiser en temps réel le drawdown actuel
* US-RISK-009 : En tant que bot, je veux retry placer le stop‑loss en cas d’échec technique
* US-RISK-010 : En tant que trader, je veux exporter le log de risk management

## ⚙️ Conditions critiques

* Paramètre de risque manquant → valeur par défaut appliquée
* Stop‑loss non placé → notification et retry automatique
* Drawdown > seuil → blocage automatique des nouveaux ordres

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_24_risk_management_stop_loss.png`

## 🧠 Prompt IA utilisé

```
Generate a BPMN diagram for EPIC 'Risk Management & Stop‑Loss Guard' with:
- Swimlanes: UI, Bot, AI, DB, Trader
- Tasks: calculate position size, place stop‑loss, monitor drawdown, alert
- Decisions: stop‑loss triggered? drawdown exceeded?
```

## ⚠️ Limites connues

* Pas de gestion de trailing stop-loss avancé
* Vulnérable aux gaps de marché hors horaire

## 🔁 Références croisées

| Fonction       | EPIC concerné                     |
| -------------- | --------------------------------- |
| Live Trading   | EPIC 23 – Live Trade Execution    |
| Performance IA | EPIC 20 – AI Performance Tracking |

## 💡 Leçon clé

Le risk management automatisé est le pilier de la pérennité : sans stop‑loss et contrôle du drawdown, aucune stratégie n’est durable.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 25](../images/bpmn_epic_25_automated_reporting_compliancepng.png)
