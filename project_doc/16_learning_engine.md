# 📘 Chapitre 16 – Learning Engine (Moteur d’Apprentissage IA)

## 🎯 Objectif de ce module

Ce module permet d’analyser automatiquement les performances journalières, de comparer les trades simulés et réels, et d’ajuster dynamiquement les paramètres IA. Il constitue le cœur de l’évolution intelligente du système.

## 🧠 Modules et acteurs impliqués

* **UI** : Affiche les paramètres IA ajustés et l’évolution des performances
* **Bot** : Collecte les données de la journée et déclenche l’analyse
* **AI** : Apprend des erreurs et réussites, ajuste ses poids et seuils
* **DB** : Stocke les résultats, les ajustements, les historiques de modèles
* **Trader** : Consulte l’évolution IA et valide (ou non) certains choix

## 🗃️ Tables utilisées

| Table            | Description                                    |
| ---------------- | ---------------------------------------------- |
| `trades`         | Résultats simulés et réels                     |
| `ai_parameters`  | Poids, seuils et configurations IA             |
| `learning_log`   | Journal d’apprentissage                        |
| `trades_simules` | Historique des trades analysés automatiquement |

## 📜 User Stories de cet EPIC

* US-LEARN-001 : Analyser les trades exécutés de la journée
* US-LEARN-002 : Comparer gain estimé, simulé, réel
* US-LEARN-003 : Identifier les erreurs récurrentes (entrée tardive, TP raté...)
* US-LEARN-004 : Calculer l’efficacité du scoring IA (gain/taux réussite)
* US-LEARN-005 : Ajuster dynamiquement les paramètres IA
* US-LEARN-006 : Enregistrer les modifications dans `ai_parameters`
* US-LEARN-007 : Logger les apprentissages dans `learning_log`
* US-LEARN-008 : Afficher la progression dans un tableau comparatif
* US-LEARN-009 : Simuler l’effet de l’ancien score vs nouveau
* US-LEARN-010 : Réinitialiser les poids IA manuellement depuis l’UI

## ⚙️ Conditions critiques

* Données absentes → apprentissage suspendu
* Si IA en mode verrouillé (manuelle) → pas de mise à jour auto
* Incohérences simulé/réel trop fortes → alerte à afficher

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_16_learning_engine.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour le module 'Learning Engine' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : analyse des trades, comparaison, ajustement IA, logs
Conditions critiques en cas d’erreur ou conflit IA
```

## ⚠️ Limites connues

* Les performances peuvent être influencées par des données biaisées
* Le modèle n’est pas encore versionné (un seul jeu de paramètres)
* IA encore sensible aux résultats de trades trop extrêmes

## 🔁 Références croisées

| Fonction | EPIC concerné             |
| -------- | ------------------------- |
| Clôture  | EPIC 15 – Clôture Journée |
| Journal  | EPIC 12 – Journalisation  |
| Scoring  | EPIC 09 – Analyse IA      |

## 💡 Leçon clé

Un système IA performant apprend chaque jour. Le moteur d’apprentissage transforme les erreurs en stratégie et optimise en continu sans intervention humaine.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 16](../images/bpmn_epic_16_learning_engine.png)
