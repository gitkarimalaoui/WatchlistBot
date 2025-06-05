# 📆 MODULE 7 – Daily Closure : `cloture.py`

## 🎯 Objectif du module
Ce module permet de **clôturer la journée de trading** : il fige les données, calcule les statistiques finales, déclenche des exports et nettoie l’environnement de travail pour le prochain cycle.

---

## 📂 Fichier principal
- `cloture.py`

### 📁 Chemin projet suggéré :
```
BOTV7/analytics/cloture.py
```

### 📁 Chemin local recommandé :
```
C:\Users\KARIM\Desktop\python\projet AI\BOTV7\BOTV7\analytics\cloture.py
```

---

## 📋 User Stories associées (Daily Closure)

| ID              | Rôle        | Objectif résumé                                   | Statut |
|-----------------|-------------|----------------------------------------------------|--------|
| US-CLOSE-001     | Trader      | Déclencher la clôture manuellement                | To Do  |
| US-CLOSE-002     | Bot         | Geler les données et bloquer la modification      | To Do  |
| US-CLOSE-003     | System      | Exporter les données journalières en CSV          | To Do  |
| US-CLOSE-004     | Bot         | Envoyer une alerte Telegram avec le résumé        | To Do  |
| US-CLOSE-005     | System      | Verrouiller les boutons/inputs après clôture      | To Do  |
| US-CLOSE-006     | Bot         | Calculer et sauvegarder les KPI journaliers       | To Do  |
| US-CLOSE-007     | Bot         | Réinitialiser les listes internes (watchlist, etc.) | To Do |
| US-CLOSE-008     | System      | Archiver les logs générés pendant la journée      | To Do  |
| US-CLOSE-009     | System      | Logger la date/heure exacte de clôture            | To Do  |
| US-CLOSE-010     | Trader      | Visualiser un tableau de bord de fin de journée   | To Do  |

---

## 🔧 Fonction clé

### `cloturer_journee()`
- Affiche un bouton dans Streamlit
- Appelle `calculer_stats_journalieres()` (depuis `db_model.py`)
- Affiche une notification de succès avec les résultats calculés

---

## 🔗 Connexions

| Connecté à...           | Rôle                            |
|--------------------------|---------------------------------|
| `db_model.py`            | Calcul des stats journalières   |
| `journal.py`             | Lecture des trades du jour      |
| `telegram_bot.py` (opt.) | Envoi de notification           |
| `dashboard.py` (opt.)    | Résumé visuel                   |

---

## 📌 Statut

- ✅ Code Streamlit validé
- ✅ 10 user stories importées
- 🟡 Fonction externe `calculer_stats_journalieres()` à auditer
- 🟢 Prêt à être intégré dans le menu UI principal

---

## 📌 Historique des mises à jour

- **2025-05-21** : Création complète du module et intégration des US
---
### ✅ User Story — US-CLOSE-011

- **Epic** : Daily Closure  
- **En tant que** système  
- **Je veux** détecter s’il existe déjà une entrée pour la date sélectionnée dans `stats_journalieres`  
- **Afin de** proposer à l’utilisateur de la remplacer ou non

#### 🎯 Critères d’acceptation

1. Affiche un avertissement si une ligne existe déjà
2. Affiche une case à cocher pour confirmer le remplacement
3. Si coché, supprime la ligne et insère la nouvelle
4. Si non coché, annule l’opération sans modifier
5. Affiche le résumé après succès de la mise à jour