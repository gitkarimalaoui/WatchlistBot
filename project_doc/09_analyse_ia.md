# 📘 Chapitre 09 – Analyse IA (Scoring des Tickers)

## 🎯 Objectif de ce module

Ce module applique une analyse automatisée aux tickers retenus après filtrage afin d’attribuer un score de pertinence via un modèle IA. Ce score permet de prioriser les tickers avant simulation ou exécution.

## 🧠 Modules et acteurs impliqués

* **UI** : Affiche les scores IA des tickers analysés
* **Bot** : Exécute l’appel au moteur IA avec les paramètres requis
* **AI** : Calcule le score selon plusieurs critères pondérés (historique, volatilité, pattern, float, volume…)
* **DB** : Enregistre les scores et les détails de calcul pour audit
* **Trader** : Peut visualiser les tickers triés par score

## 🗃️ Tables utilisées

| Table         | Description                  |
| ------------- | ---------------------------- |
| `tickers`     | Liste des tickers à scorer   |
| `ia_scores`   | Score IA attribué par ticker |
| `tickers_log` | Journalisation des appels IA |

## 📜 User Stories de cet EPIC

* US-IA-001 : Récupérer les tickers retenus pour scoring
* US-IA-002 : Appeler le moteur IA avec les caractéristiques du ticker
* US-IA-003 : Calculer un score basé sur les paramètres préconfigurés
* US-IA-004 : Enregistrer le score dans la table `ia_scores`
* US-IA-005 : Mettre à jour le ticker avec son score IA
* US-IA-006 : Logger l’analyse dans `tickers_log`
* US-IA-007 : Afficher le score dans l’interface UI
* US-IA-008 : Trier les tickers par score décroissant
* US-IA-009 : Permettre à l’IA de corriger un score en fonction d’un retour utilisateur ou trade simulé
* US-IA-010 : Intégrer un système de pondération dynamique évolutif

## ⚙️ Conditions critiques

* Si données incomplètes → scoring annulé
* Si score < seuil min configuré → ticker désactivé
* Si moteur IA indisponible → fallback sur score par défaut

## 📊 Diagramme BPMN

→ Voir `/images/bpmn_epic_09_analyse_ia.png`

## 🧠 Prompt IA utilisé

```
Génère le diagramme BPMN pour le module 'Analyse IA' avec :
Couloirs : UI, Bot, AI, DB, Trader
Tâches : scoring, pondération, sauvegarde, affichage
Flux alternatifs : échec IA, score nul, fallback
```

## ⚠️ Limites connues

* La qualité du scoring dépend fortement des données d’entrée
* Le modèle peut évoluer mais nécessite un mécanisme de recalibrage
* Risque de sur-pondération si les paramètres ne sont pas équilibrés

## 🔁 Références croisées

| Fonction      | EPIC concerné               |
| ------------- | --------------------------- |
| Filtrage      | EPIC 08 – Filtrage Tickers  |
| Simulation    | EPIC 13 – Simulation Trades |
| Apprentissage | EPIC 16 – Learning Engine   |

## 💡 Leçon clé

Le score IA est un pivot stratégique entre détection et action. Il oriente toutes les décisions ultérieures du bot de trading et doit donc rester robuste, auditables et évolutif.


---

## 📊 Diagramme BPMN

![BPMN – EPIC 09](../images/bpmn_epic_09_analyse_ia.png)
