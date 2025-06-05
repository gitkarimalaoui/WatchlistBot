# 📘 Chapitre 17 – Base IA Historique (Données pour l’Entraînement)

## 🎯 Objectif de ce module

Ce module centralise et organise les données historiques nécessaires à l’apprentissage et à la validation des modèles IA. Il permet de construire une base solide pour le scoring prédictif et les simulations IA futures.

## 🧠 Modules et acteurs impliqués

* **Bot** : Collecte et met à jour les données historiques (daily & intraday)
* **AI** : S’appuie sur ces données pour entraîner ou ajuster ses modèles
* **DB** : Contient la base structurée et optimisée pour l’entraînement IA
* **UI** : Permet de déclencher la génération ou de visualiser l’historique
* **Trader** : Consulte les performances passées ou déclenche un backtest IA

## 🗃️ Tables utilisées

| Table                 | Description                                   |
| --------------------- | --------------------------------------------- |
| `historical_daily`    | Données journalières (2 ans) par ticker       |
| `historical_intraday` | Données minute (1 à 2 jours)                  |
| `training_sets`       | Ensembles préparés pour IA                    |
| `tickers_meta`        | Métadonnées sur les tickers (secteur, float…) |

## 📜 User Stories de cet EPIC

* US-HIST-001 : Générer les données historiques au lancement
* US-HIST-002 : Importer automatiquement les données depuis yfinance/Finnhub
* US-HIST-003 : Nettoyer les données corrompues ou incomplètes
* US-HIST-004 : Stocker les daily data dans `historical_daily`
* US-HIST-005 : Stocker les données minute dans `historical_intraday`
* US-HIST-006 : Fusionner avec les métadonnées de `tickers_meta`
* US-HIST-007 : Créer un jeu d’entraînement dans `training_sets`
* US-HIST-008 : Mettre à jour automatiquement les données chaque jour
* US-HIST-009 : Visualiser les historiques depuis l’interface
* US-HIST-010 : Détecter les anomalies ou absences de données

## ⚙️ Conditions critiques

* Données API manquantes → alerte en log
* Ticker introuvable → rejet automatique avec message debug
* Trop de données à charger → découpage en batch journalier

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_17_base_ia_historique.png`

## 🧠 Prompt IA utilisé

```
Génère le diagramme BPMN pour le module 'Base IA Historique' avec :
Couloirs : Bot, AI, DB, UI, Trader
Étapes : import, nettoyage, stockage, jeu IA, logs
Flux d’erreur si données manquantes ou corruption
```

## ⚠️ Limites connues

* Certaines API historiques ont des limitations (fins de semaine, valeurs nulles)
* Temps de chargement important si batch global
* Pas encore de modèle de versionnement des datasets

## 🔁 Références croisées

| Fonction      | EPIC concerné               |
| ------------- | --------------------------- |
| Apprentissage | EPIC 16 – Learning Engine   |
| Analyse IA    | EPIC 09 – Analyse IA        |
| Simulation    | EPIC 13 – Simulation Trades |

## 💡 Leçon clé

Une IA est aussi puissante que sa base d’entraînement. Une base historique fiable et à jour permet de mieux prédire, mieux simuler et mieux réagir aux mouvements du marché.



---

## 📊 Diagramme BPMN

![BPMN – EPIC 17](../images/bpmn_epic_17_base_ia_historique.png)
