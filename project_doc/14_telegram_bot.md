# 📘 Chapitre 14 – Bot Telegram (Alerte & Interaction)

## 🎯 Objectif de ce module

Ce module permet de recevoir des alertes automatiques sur Telegram à chaque détection de ticker intéressant, ainsi que d’interagir avec le bot via commandes textuelles simples (ex. : consulter la watchlist, recevoir le top scoré, etc.).

## 🧠 Modules et acteurs impliqués

* **UI** : Paramètre l’état du bot et son comportement
* **Bot** : Envoie les messages et gère les commandes Telegram
* **AI** : Déclenche des alertes basées sur le score ou un événement
* **DB** : Stocke les logs des notifications et actions utilisateurs
* **Trader** : Reçoit les alertes en temps réel et peut interagir

## 🗃️ Tables utilisées

| Table               | Description                         |
| ------------------- | ----------------------------------- |
| `telegram_log`      | Historique des messages envoyés     |
| `telegram_commands` | Commandes reçues et réponses        |
| `tickers`           | Données utilisées pour les messages |

## 📜 User Stories de cet EPIC

* US-TG-001 : Recevoir une alerte Telegram quand un ticker passe un seuil IA
* US-TG-002 : Envoyer automatiquement un message pour chaque ticker retenu
* US-TG-003 : Répondre à des commandes du type `/watchlist`, `/top3`
* US-TG-004 : Logger chaque message envoyé dans `telegram_log`
* US-TG-005 : Logger les commandes reçues dans `telegram_commands`
* US-TG-006 : Afficher une notification dans l’UI si le bot Telegram est inactif
* US-TG-007 : Permettre de configurer le chat\_id et token via paramètres UI
* US-TG-008 : Gérer les erreurs d’envoi avec alerte dans l’interface
* US-TG-009 : Activer ou désactiver le bot Telegram depuis le menu principal
* US-TG-010 : Synchroniser les alertes avec les données de simulation

## ⚙️ Conditions critiques

* Si token invalide → arrêt du bot avec log d’erreur
* Si chat\_id inconnu → message ignoré
* Si API Telegram non disponible → mise en file d’attente possible

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_14_telegram_bot.png`

## 🧠 Prompt IA utilisé

```
Génère un diagramme BPMN pour l’EPIC 'Bot Telegram' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : alerte, commande, logging, notification
Flux d’erreur, fallback si API absente
```

## ⚠️ Limites connues

* Nombre de messages limités si quota dépassé
* Pas encore de gestion multi-utilisateur (un seul trader par défaut)
* Certaines commandes avancées sont en développement

## 🔁 Références croisées

| Fonction        | EPIC concerné               |
| --------------- | --------------------------- |
| Simulation      | EPIC 13 – Simulation Trades |
| Clôture Journée | EPIC 15 – Clôture Journée   |

## 💡 Leçon clé

Un bot performant ne se contente pas d’exécuter : il doit informer. Telegram permet de rester connecté au marché même loin de son écran.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 14](../images/bpmn_epic_14_telegram_bot.png)
