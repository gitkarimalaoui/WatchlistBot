# ✅ MODULE – Exécution réelle : `execution_reelle.py`

## 🎯 Description
Ce module fournit la fonction `executer_ordre_reel` permettant d'envoyer un ordre réel via le script local `executer_ordre_moomoo.py`. L'appel se fait au moyen du module `subprocess` afin de garder l'interface graphique indépendante du bot principal.

## 📌 Utilisation
```python
from utils.execution_reelle import executer_ordre_reel
result = executer_ordre_reel("AAPL", 150.0, 10, "achat")
```
La fonction retourne un dictionnaire `{"success": bool, "message": str}` pour affichage immédiat dans l'interface Streamlit.

## ⚠️ Conditions d'appel
- `prix` et `quantite` doivent être strictement supérieurs à zéro.
- L'action `"vente"` renvoie pour l'instant un message indiquant que la fonctionnalité n'est pas implémentée.
- Le script `executer_ordre_moomoo.py` doit être accessible localement et la plateforme Moomoo ouverte.

## 🔒 Sécurité
Un contrôle simple empêche l'envoi d'ordres avec prix ou quantité nuls. Le script est lancé dans un sous-processus isolé et tout échec est capturé pour retour utilisateur.

## 🗃️ Journalisation
Si la base `trades.db` est présente, un enregistrement est ajouté dans la table `trades_reels` avec :
`symbol`, `price`, `qty`, `side`, `timestamp`, `source`.

## 🔜 Étapes de validation future
- Implémentation de la vente réelle.
- Vérifications supplémentaires sur la cohérence des ordres (prix limites, verrou d'autorisation).
- Tests end‑to‑end sur environnement sécurisé avant passage complet en réel.
