# 📘 Chapitre 15 – Clôture Journée (Fin de Session de Trading)

## 🎯 Objectif de ce module

Ce module permet de clôturer proprement la journée de trading en gelant les données, calculant les performances, enregistrant les statistiques finales et actualisant les indicateurs internes du système.

## 🧠 Modules et acteurs impliqués

* **UI** : Bouton "Clôturer la journée" déclenchant le processus
* **Bot** : Exécute les tâches de clôture (résumé, sauvegarde, nettoyage)
* **AI** : Analyse les performances journalières pour ajustement futur
* **DB** : Met à jour les journaux, les résultats de trading, les indicateurs
* **Trader** : Confirme la fin de session et valide les résultats du jour

## 🗃️ Tables utilisées

| Table           | Description                                    |
| --------------- | ---------------------------------------------- |
| `daily_summary` | Résumé des trades, gains, pertes de la journée |
| `trades`        | Liste des transactions exécutées               |
| `ai_parameters` | Paramètres ajustés automatiquement             |
| `logs`          | Journalisation des étapes de clôture           |

## 📜 User Stories de cet EPIC

* US-CLOSE-001 : Appuyer sur "Clôturer la journée" dans l’interface
* US-CLOSE-002 : Geler toutes les données actives (watchlist, résultats…)
* US-CLOSE-003 : Calculer automatiquement le PnL net et brut
* US-CLOSE-004 : Enregistrer le résumé journalier dans `daily_summary`
* US-CLOSE-005 : Mettre à jour les paramètres IA avec les résultats du jour
* US-CLOSE-006 : Logger l’événement dans la table `logs`
* US-CLOSE-007 : Afficher dans le dashboard les totaux du jour + cumul mensuel
* US-CLOSE-008 : Désactiver le moteur de détection automatique
* US-CLOSE-009 : Envoyer une alerte Telegram de clôture si activé
* US-CLOSE-010 : Relancer le moteur IA en mode veille pour apprentissage nocturne

## ⚙️ Conditions critiques

* Si données incomplètes → rejet de clôture
* Si bouton déclenché hors horaires valides → blocage système
* Si IA déjà en apprentissage → différé automatique

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_15_cloture_journee.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour l’EPIC 'Clôture Journée' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : gel des données, calcul PnL, log, mise à jour IA
Flux alternatifs si erreur ou apprentissage en cours
```

## ⚠️ Limites connues

* Pas de sauvegarde intermédiaire automatique avant clôture
* Si IA en cours d’apprentissage, possible écrasement non désiré
* Le moteur automatique n’est pas encore désactivé par défaut

## 🔁 Références croisées

| Fonction      | EPIC concerné             |
| ------------- | ------------------------- |
| Telegram Bot  | EPIC 14 – Bot Telegram    |
| Apprentissage | EPIC 16 – Learning Engine |

## 💡 Leçon clé

La qualité de l’analyse IA dépend directement de la rigueur de clôture. Chaque session bien terminée est une brique d’apprentissage pour demain.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 15](../images/bpmn_epic_15_cloture_journee.png)
