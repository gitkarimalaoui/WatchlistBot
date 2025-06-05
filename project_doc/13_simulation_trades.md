# 📘 Chapitre 13 – Simulation de Trades (Ordres virtuels)

## 🎯 Objectif de ce module

Ce module permet de simuler des ordres d’achat et de vente à partir des tickers analysés. Il vise à évaluer la performance des stratégies sans risquer de capital réel, en prenant en compte les frais réels et la latence d’exécution.

## 🧠 Modules et acteurs impliqués

* **UI** : Permet de saisir un ordre simulé et de visualiser le résultat
* **Bot** : Exécute les calculs de PnL et frais associés
* **AI** : Peut proposer une entrée ou sortie optimisée
* **DB** : Stocke tous les ordres simulés et leur résultat final
* **Trader** : Lance les simulations et analyse les performances

## 🗃️ Tables utilisées

| Table              | Description                                    |
| ------------------ | ---------------------------------------------- |
| `simulated_trades` | Détails des ordres simulés (achat, vente)      |
| `tickers`          | Source des tickers simulés                     |
| `trade_results`    | Résultat de la simulation : gain, perte, ratio |
| `execution_log`    | Historique de l’exécution des ordres           |

## 📜 User Stories de cet EPIC

* US-SIM-001 : Saisir un ordre d’achat avec prix, quantité et frais
* US-SIM-002 : Calculer le coût total de l’ordre avec commissions
* US-SIM-003 : Générer une vente simulée à partir de conditions IA ou manuelles
* US-SIM-004 : Afficher le PnL (gain ou perte) estimé
* US-SIM-005 : Enregistrer l’ordre simulé dans la base `simulated_trades`
* US-SIM-006 : Visualiser l’impact des frais sur la rentabilité
* US-SIM-007 : Afficher le résultat de tous les trades simulés dans l’interface
* US-SIM-008 : Comparer les résultats simulés aux prédictions IA
* US-SIM-009 : Logger chaque exécution dans `execution_log`
* US-SIM-010 : Permettre un export CSV ou JSON des résultats

## ⚙️ Conditions critiques

* Si prix ou quantité non valide → rejet de la simulation
* Si API en panne → simulation désactivée ou limitée
* Si frais estimés dépassent les gains → alerte affichée

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_13_simulation_trades.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour l’EPIC 'Simulation de Trades' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : saisie d’ordre, calcul PnL, sauvegarde, affichage
Flux alternatifs : erreur de saisie, perte, alerte rentabilité
```

## ⚠️ Limites connues

* Ne reflète pas les conditions de marché réelles (slippage, spread dynamique)
* Ne gère pas encore les trades partiels ou fractionnés
* L’optimisation IA peut sur-ajuster au passé

## 🔁 Références croisées

| Fonction         | EPIC concerné               |
| ---------------- | --------------------------- |
| Scoring IA       | EPIC 09 – Analyse IA        |
| Interface UI     | EPIC 11 – Interface Trading |
| Apprentissage IA | EPIC 16 – Learning Engine   |

## 💡 Leçon clé

Simuler permet de tester sans risque, mais uniquement si l’environnement est réaliste. Chaque simulation doit être considérée comme un entraînement IA à part entière.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 13](../images/bpmn_epic_13_simulation_trades.png)
