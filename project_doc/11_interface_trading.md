# 📘 Chapitre 11 – Interface de Trading (Streamlit UI)

## 🎯 Objectif de ce module

Ce module fournit une interface utilisateur centralisée permettant d’interagir avec tous les éléments du bot : watchlist, scores IA, graphiques, exécutions simulées, et journalisation. L’objectif est de permettre une prise de décision rapide et éclairée.

## 🧠 Modules et acteurs impliqués

* **UI** : Centralise toutes les informations clés (panneaux interactifs)
* **Bot** : Alimente l’interface en données temps réel
* **AI** : Affiche le score, les signaux, et les propositions IA
* **DB** : Fournit les données historiques, logs, watchlist, résultats
* **Trader** : Navigue, filtre, exécute, observe

## 🗃️ Tables utilisées

| Table              | Description                                   |
| ------------------ | --------------------------------------------- |
| `tickers`          | Watchlist actuelle                            |
| `ia_scores`        | Résultats d’analyse IA                        |
| `simulated_trades` | Ordres simulés                                |
| `tickers_log`      | Logs d’interaction                            |
| `trader_input`     | Paramètres saisis ou actions de l’utilisateur |

## 📜 User Stories de cet EPIC

* US-UI-001 : Afficher les tickers avec leurs scores et graphiques
* US-UI-002 : Permettre l’exécution simulée d’un ordre via un bouton
* US-UI-003 : Afficher les gains/pertes simulés en temps réel
* US-UI-004 : Permettre l’ajout manuel d’un ticker via interface
* US-UI-005 : Accéder aux journaux des opérations en un clic
* US-UI-006 : Filtrer les tickers affichés par score ou critère
* US-UI-007 : Mettre à jour dynamiquement les données sans recharger la page
* US-UI-008 : Activer/Désactiver certains modules depuis l’UI
* US-UI-009 : Naviguer entre les onglets (scan, IA, simulation, journal, paramètres)
* US-UI-010 : Recevoir des alertes visuelles ou sonores sur détection IA

## ⚙️ Conditions critiques

* Si la base est vide → affichage par défaut ou message d’alerte
* Si un module plante → affichage partiel avec message d’erreur
* L’interface doit rester fluide, même avec 50+ tickers affichés

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_11_interface_trading.png`

## 🧠 Prompt IA utilisé

```
Génère le diagramme BPMN pour l’EPIC 'Interface Trading' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : affichage des scores, graphiques, journaux, exécutions
Flux d’erreur, boutons interactifs, rafraîchissement dynamique
```

## ⚠️ Limites connues

* La lisibilité devient difficile si trop d’infos sont superposées
* Certaines données critiques peuvent être masquées sans alerte
* Pas encore de version mobile responsive

## 🔁 Références croisées

| Fonction   | EPIC concerné                   |
| ---------- | ------------------------------- |
| IA scoring | EPIC 09 – Analyse IA            |
| Graphique  | EPIC 10 – Graphiques Dynamiques |
| Simulation | EPIC 13 – Simulation Trades     |

## 💡 Leçon clé

Une bonne interface ne se contente pas d’afficher des données : elle guide, alerte et accélère la décision du trader tout en gardant une logique fluide et intuitive.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 11](../images/bpmn_epic_11_interface_trading.png)
