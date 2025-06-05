# 📘 Chapitre 03 – Real-time Data Ingestion & Validation

## 🎯 Objectif de ce module

Assurer la collecte continue et la validation des données de marché (prix, volume, news) en temps réel, avant leur passage dans la chaîne d’analyse et de scoring.

## 🧠 Modules et acteurs impliqués

* **UI** : Indicateur de statut de collecte en direct
* **Bot** : Interroge les APIs (Finnhub, yfinance) et récupère les flux de données
* **AI** : Vérifie la cohérence des valeurs (anomalies, outliers)
* **DB** : Stocke les données brutes et validées
* **Trader** : Consulte la qualité et le statut des données via l’interface

## 🗃️ Tables utilisées

| Table                 | Description                                |
| --------------------- | ------------------------------------------ |
| `raw_market_data`     | Données brutes reçues minute par minute    |
| `validated_data`      | Données ayant passé les contrôles qualité  |
| `data_validation_log` | Journal des erreurs et anomalies détectées |

## 📜 User Stories de cet EPIC

* US-DATA-001 : Collecter les ticks et OHLC intraday
* US-DATA-002 : Vérifier l’absence de valeurs nulles ou aberrantes
* US-DATA-003 : Filtrer les outliers selon règles métiers
* US-DATA-004 : Enregistrer les données validées dans `validated_data`
* US-DATA-005 : Logguer chaque anomalie dans `data_validation_log`
* US-DATA-006 : Afficher en temps réel le statut de collecte dans l’UI
* US-DATA-007 : Relancer automatiquement la requête en cas d’échec
* US-DATA-008 : Mettre en cache les derniers points pour fallback
* US-DATA-009 : Supporter plusieurs sources de données simultanées
* US-DATA-010 : Envoyer une alerte si volume anormal détecté

## ⚙️ Conditions critiques

* API indisponible → utiliser le cache
* Valeurs nulles → rejet et log
* Taux de collecte inférieur au seuil → alerte système

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_03_real_time_data_ingestion.png`

## 🧠 Prompt IA utilisé

```
Generate a BPMN diagram for EPIC 'Real-time Data Ingestion & Validation' with:
- Swimlanes: UI, Bot, AI, DB, Trader
- Tasks: fetch data, validate, filter outliers, store validated data
- Decisions: data complete? API available?
```

## ⚠️ Limites connues

* Dépendance aux quotas API
* Latence possible sur les heures de pointe

## 🔁 Références croisées

| Fonction         | EPIC concerné |
| ---------------- | ------------- |
| Scheduler        | EPIC 02       |
| Watchlist Import | EPIC 05       |
| AI Scoring       | EPIC 09       |

## 💡 Leçon clé

La fiabilité de l’analyse repose sur des données valides et cohérentes : sans ingestion robuste, tout scoring est compromis.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 03](../images/bpmn_epic_03_real_time_data_ingestion.png)
