
# ✅ MODULE 6 – Simulation Engine : `simulate_trade_result.py`

## 🎯 Objectif du module
Ce module est responsable de la **simulation complète des ordres de trading** à partir des paramètres saisis dans l’interface. Il applique les frais réels (ex. : Moomoo), exécute des stratégies avec **SL / TP**, enregistre les résultats, et fournit un feedback à l’IA.

---

## 📂 Fichiers inclus dans le module

| Fichier                        | Rôle                                              |
|-------------------------------|---------------------------------------------------|
| `simulate_trade_result.py`    | Simulation principale IA + calculs                |
| `execution_simulee.py`        | Enregistrement SQL dans `trades_simules`         |
| `simulation_achat.py`         | Interface manuelle pour ajout de trade (JSON)    |
| `simulation_vente.py`         | Interface manuelle pour vente simulée (JSON)     |

---

## 📁 Chemins recommandés

- `BOTV7/simulation/simulate_trade_result.py`
- `BOTV7/simulation/execution_simulee.py`
- `BOTV7/ui/simulation_achat.py`
- `BOTV7/ui/simulation_vente.py`

---

## 🗃 Tables concernées

| Base        | Table               | Rôle                            |
|-------------|---------------------|----------------------------------|
| `trades.db` | `simulated_trades`  | Enregistrements de simulation IA |
| `trades.db` | `trades_simules`    | Enregistrements manuels SQL     |
| *(retiré)* | Les journaux sont désormais stockés uniquement dans `trades.db` |

---

## 📋 User Stories associées (Simulation Engine)

- Voir document initial : `USER_STORIES_SIMULATION_ENGINE.xlsx` (10 US)

---

## 📌 Fonctions clés

### `simulate_trade_result.py`
- `executer_trade_simule()`

### `execution_simulee.py`
- `enregistrer_trade_simule(conn, ...)`
- `afficher_journal_trades(conn)`

### `simulation_achat.py` & `simulation_vente.py`
- `enregistrer_achat()` / `enregistrer_vente()`

---

## 📌 Statut

- ✅ Tous les fichiers reçus
- 🧠 Logique IA à compléter
- 🟢 Structure claire et modulaire confirmée

---

## 📌 Historique

- **2025-05-21** : Mise à jour avec sous-modules manuels et SQL intégrés
