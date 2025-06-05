# 📘 Chapitre 07 – Scan News (Pré-Market Scanner)

## 🌟 Objectif de ce module

Ce module a pour objectif de scanner automatiquement les news pré-market susceptibles d'impacter fortement certains tickers (FDA, Uplisting, IPO, Fusion, SPAC, etc.), et d'ajouter les tickers à la watchlist avec provenance et score initial.

## 🧠 Modules et acteurs impliqués

* **UI** : Affichage des options de scan et des tickers détectés
* **Bot** : Scan des news via API Finnhub
* **AI** : Attribution d'un score initial en fonction du type de news
* **DB** : Enregistrement du ticker, de la provenance, du score, des logs
* **Trader** : Visualisation des tickers ajoutés automatiquement

## 📃 Tables utilisées

| Table            | Description                         |
| ---------------- | ----------------------------------- |
| `tickers`        | Tickers retenus pour analyse        |
| `tickers_source` | Provenance : `ScanNews`             |
| `tickers_log`    | Log d'exécution du scan automatique |

## 📜 User Stories de cet EPIC

* US-NEWS-001 : Démarrer un scan pré-market depuis l'interface
* US-NEWS-002 : Le bot interroge l'API Finnhub (type=fda, uplisting...)
* US-NEWS-003 : Identifier les tickers mentionnés dans les news
* US-NEWS-004 : Valider chaque ticker (prix > 0, données existantes)
* US-NEWS-005 : Attribuer un score IA selon le type de news
* US-NEWS-006 : Enregistrer dans `tickers`, `tickers_source`, `tickers_log`
* US-NEWS-007 : Afficher les tickers détectés dans la watchlist
* US-NEWS-008 : Notifier via Telegram si activé
* US-NEWS-009 : Rejeter les tickers invalides
* US-NEWS-010 : Rafraîchir dynamiquement si mode auto activé

## ⚙️ Conditions critiques

* News non pertinente → ignorée
* Ticker introuvable / invalide → rejeté dans `tickers_invalid`
* Scan uniquement entre 04:00 et 09:30 (heure de New York)
* Si doublon : le score peut être mis à jour mais sans répétition dans la watchlist

## 📊 Diagramme BPMN associé

→ Voir `/images/bpmn_epic_07_scan_news.png`

## 🧠 Prompt IA utilisé

```
Génère le diagramme BPMN pour l'EPIC 'Scan News' avec :
- Couloirs : UI / Bot / AI / DB / Trader
- Tâches : appel API, parsing, scoring, filtrage, enregistrement
- Flux normaux + rejets
- Affichage final dans l'interface + notification Telegram
```

## ⚠️ Limites connues

* Certaines news sans tickers valides (titre ambigu)
* Tickers parfois déjà présents (risque de sur-score)
* Dépendance forte à la qualité de l'API Finnhub

## 🔄 Références croisées

| Fonction       | EPIC concerné              |
| -------------- | -------------------------- |
| Scraping forum | EPIC 06 - Jaguar Scraping  |
| Import manuel  | EPIC 05 - Watchlist Import |
| IA scoring     | EPIC 09 - Analyse IA       |

## 💡 Leçon clé

Un bon scanner de news peut détecter des opportunités avant l'ouverture du marché. Couplé à une IA et un bon filtrage, il devient un outil redoutable de préparation à haute valeur ajoutée.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 07](../images/bpmn_epic_07_scan_news.png)
