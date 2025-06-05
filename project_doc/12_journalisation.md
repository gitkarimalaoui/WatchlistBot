# 📘 Chapitre 12 – Journalisation (Logs des Actions)

## 🎯 Objectif de ce module

Ce module assure la traçabilité complète des actions du bot, de l’IA et de l’utilisateur, en enregistrant dans des tables de log chaque événement, décision, erreur ou exécution. Cela permet d’auditer, d’analyser et d’améliorer le système de manière continue.

## 🧠 Modules et acteurs impliqués

* **UI** : Peut afficher les logs récents et journaux filtrés
* **Bot** : Écrit automatiquement tous les événements techniques
* **AI** : Loggue ses scores, ajustements, et décisions
* **DB** : Stocke les journaux dans des tables dédiées
* **Trader** : Consulte les journaux, valide ou annule des actions

## 🗃️ Tables utilisées

| Table           | Description                                      |
| --------------- | ------------------------------------------------ |
| `tickers_log`   | Logs liés aux tickers (ajouts, filtres, erreurs) |
| `ia_log`        | Logs des scores, décisions IA, pondérations      |
| `execution_log` | Logs des simulations ou ordres exécutés          |
| `user_log`      | Actions manuelles de l’utilisateur               |

## 📜 User Stories de cet EPIC

* US-LOG-001 : Enregistrer chaque import de ticker avec source et statut
* US-LOG-002 : Logger chaque score IA attribué
* US-LOG-003 : Logger les erreurs de récupération de données
* US-LOG-004 : Logger les actions de l’utilisateur dans l’interface
* US-LOG-005 : Permettre de consulter les logs dans l’interface
* US-LOG-006 : Rechercher dans les logs par filtre (date, ticker, type)
* US-LOG-007 : Générer un export CSV ou JSON des logs
* US-LOG-008 : Afficher les logs critiques en priorité
* US-LOG-009 : Marquer les logs comme validés ou analysés
* US-LOG-010 : Associer les logs aux décisions d’apprentissage IA

## ⚙️ Conditions critiques

* Si erreur critique → log automatique avec priorité haute
* Si action non reconnue → journalisation dans `user_log` avec tag `undefined`
* Chaque module a sa propre table pour éviter les conflits

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_12_journalisation.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour le module 'Journalisation' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : enregistrement, consultation, export, tri
Flux d’erreurs, alertes, et validations
```

## ⚠️ Limites connues

* Volume important de données en cas d’analyse longue
* Nécessite un système de purge ou d’archivage périodique
* Peut ralentir l’interface si logs trop fréquents affichés en direct

## 🔁 Références croisées

| Fonction         | EPIC concerné               |
| ---------------- | --------------------------- |
| Scoring          | EPIC 09 – Analyse IA        |
| Interface        | EPIC 11 – Interface Trading |
| Apprentissage IA | EPIC 16 – Learning Engine   |

## 💡 Leçon clé

La qualité des décisions futures dépend de la qualité des traces passées. Une journalisation structurée permet non seulement d’auditer, mais aussi d’enseigner à l’IA comment mieux réagir.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 12](../images/bpmn_epic_12_journalisation.png)
