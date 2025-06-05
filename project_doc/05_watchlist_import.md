
# 📘 Chapitre 05 – Watchlist Import (Fichier + Manuel)

## 🎯 Objectif de ce module

Ce module permet d'importer manuellement des tickers à surveiller pour le day trading via :
- Fichiers `.txt` (ex. DrJaguar.txt)
- Saisie manuelle via l’interface utilisateur Streamlit
- Chargement des tickers sauvegardés directement depuis la base de données

💸 **Ce que recommandent les experts du daily trading :**  
Les traders gagnants préparent une watchlist efficace pré-market. Ce module permet d'intégrer cette logique dans un système structuré et modulaire.

🧠 **Ce que recommandent les experts IA :**  
Un bon scoring IA dépend d'une base d'entrée cohérente et bien marquée (source, validité, structure).

🧩 **C’est pourquoi nous avons choisi cette approche :**
- Import texte simple
- Ajout manuel propre via UI
- Validation immédiate (ticker valide, non doublon)
- Stockage dans base SQLite
- Provenance stockée pour suivi IA

---

## 🗃️ Base de données utilisée

| Table | Description |
|-------|-------------|
| `tickers` | Liste fusionnée des tickers à analyser |
| `tickers_log` | Journalisation de l’import manuel ou fichier |
| `tickers_source` | Provenance des tickers : manuel, fichier, scraping, IA |
| `tickers_invalid` | Tickers rejetés (prix nul, erreur parsing, doublon) |

---

## 📜 User Stories de cet EPIC

- US-WL-001 : Importer un fichier texte contenant des tickers
- US-WL-002 : Parser les tickers extraits du fichier
- US-WL-003 : Logguer chaque ticker ajouté (fichier ou UI)
- US-WL-004 : Ajouter manuellement un ou plusieurs tickers via UI
- US-WL-005 : Enregistrer la provenance dans la table `tickers_source`
- US-WL-006 : Rejeter les doublons
- US-WL-007 : Rejeter les tickers invalides (prix 0, erreur API)
- US-WL-008 : Fusionner dans `tickers` unique
- US-WL-009 : Afficher dans l’interface
- US-WL-010 : Sauvegarder les logs de l’opération

---

## 📊 Diagramme BPMN

➡️ Voir `/images/bpmn_epic_05_watchlist_import.png`

---

## ⚙️ Conditions critiques

- Si ticker invalide (API, nom, prix) → `tickers_invalid`
- Si doublon détecté → ignoré
- Logging dans `tickers_log` à chaque étape
- Affichage Streamlit dans panneau "Watchlist actuelle"

---

## 🧠 Prompt utilisé

```plaintext
Génère le diagramme BPMN pour l’EPIC 'Watchlist Import' avec : UI / Bot / DB / User,
conditions critiques (ticker valide, doublon, source),
logging, flux d'erreur et affichage fusionné dans l’interface.
```

---

## ⚠️ Limites connues

- Ne couvre pas les imports automatiques par scraping (voir EPIC 06)
- Ne gère pas les suggestions IA (voir EPIC 08)

---

## 🔁 Références croisées

| Source d'import | EPIC concerné |
|----------------|----------------|
| `.txt` ou manuel | **EPIC 05 – Watchlist Import (ce module)** |
| Scraping forum | EPIC 06 – Jaguar Scraping |
| News API (FDA, Uplisting…) | EPIC 07 – News Detection |
| Génération IA (GPT) | EPIC 08 – GPT Scoring Validation |

---

## 💡 Leçon clé

Un moteur IA ne vaut que ce que vaut sa source de données.  
Cette étape est la première brique de performance future.



---

## 📊 Diagramme BPMN

![BPMN – EPIC 05](../images/bpmn_epic_05_watchlist_import.png)
