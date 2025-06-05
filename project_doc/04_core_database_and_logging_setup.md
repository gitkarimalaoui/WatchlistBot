# 📘 Chapitre 04 – Core Database & Logging Setup

## 🎯 Objectif de ce module

Mettre en place la base de données centrale et la journalisation systématique de toutes les opérations critiques du bot (scans, imports, trades, erreurs) pour assurer traçabilité et auditabilité.

## 🧠 Modules et acteurs impliqués

* **UI** : Affiche le statut de la base et des logs
* **Bot** : Exécute les opérations CRUD et enregistre les logs
* **AI** : Consomme les logs pour apprentissage et reporting
* **DB** : Point focal des données structurées et des logs
* **Trader** : Consulte et télécharge les historiques via l’interface

## 🗃️ Tables utilisées

| Table           | Description                           |
| --------------- | ------------------------------------- |
| `config`        | Paramètres système                    |
| `watchlist`     | Tickers en cours d’analyse            |
| `scan_log`      | Historique des exécutions de scan     |
| `trade_log`     | Journal des ordres simulés et réels   |
| `error_log`     | Erreurs et exceptions avec timestamps |
| `daily_summary` | Résumé quotidien des performances     |

## 📜 User Stories de cet EPIC

* US-DB-001 : Initialiser la base de données à la première exécution
* US-DB-002 : Créer ou migrer les tables nécessaires automatiquement
* US-DB-003 : Journaliser chaque scan dans `scan_log`
* US-DB-004 : Enregistrer chaque trade dans `trade_log`
* US-DB-005 : Capturer et stocker chaque exception dans `error_log`
* US-DB-006 : Générer le résumé quotidien dans `daily_summary`
* US-DB-007 : Afficher l’état de la BD dans l’UI de configuration
* US-DB-008 : Gérer les migrations de schéma sans perte de données
* US-DB-009 : Archiver les logs anciens au-delà d’un seuil temporel
* US-DB-010 : Exporter les journaux en CSV ou JSON via l’UI

## ⚙️ Conditions critiques

* Corruption DB → mode lecture seule
* Migrations échouées → rollback automatique
* Taille excessive des logs → archivage et purge

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_04_core_db_logging_setup.png`

## 🧠 Prompt IA utilisé

```
Generate a BPMN diagram for EPIC 'Core Database & Logging Setup' with:
- Swimlanes: UI, Bot, AI, DB, Trader
- Tasks: init DB, create tables, log scan, log trade, log errors
- Decisions: migration needed?
```

## ⚠️ Limites connues

* Migrations manuelles possibles si rollback partiel
* Pas de sharding ou répartition horizontale

## 🔁 Références croisées

| Fonction       | EPIC concerné |
| -------------- | ------------- |
| Config         | EPIC 01       |
| Journalisation | EPIC 12       |

## 💡 Leçon clé

Une base de données robuste et un log exhaustif sont les fondations d’une plateforme fiable, facilitant audit et apprentissage IA.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 04](../images/bpmn_epic_04_core_db_logging_setup.png)
