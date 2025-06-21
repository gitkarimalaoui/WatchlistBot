# 31 – Daily Workflow

Ce document récapitule l'enchaînement des modules depuis l'ouverture de l'application jusqu'à la clôture de la journée. Il sert de guide pratique pour les nouveaux utilisateurs et comme référence pour l'audit.

## Étapes principales

1. **Lancement de l'application**
   - `streamlit run ui/app_unifie_watchlistbot.py`
   - Connexion aux bases de données et chargement de la watchlist.

2. **Import ou ajout de tickers**
   - Module : [05_watchlist_import.md](05_watchlist_import.md)
   - User stories : US‑WL‑001 à US‑WL‑020.

3. **Analyse IA et scoring**
   - Modules : `intelligence/ai_scorer.py`, [09_analyse_ia.md](09_analyse_ia.md)
   - Les scores sont sauvegardés via `db/scores.py`.

4. **Affichage et trading**
   - Interface : [19_ui_multi_modules.md](19_ui_multi_modules.md)
   - Simulation ou exécution réelle via `simulation/` ou `execution/`.

5. **Journalisation des trades**
   - Module : [12_journalisation.md](12_journalisation.md)
   - Tables mises à jour : `trades`, `trades_auto`.

6. **Clôture de journée**
   - Voir [23_daily_closure.md](23_daily_closure.md).
   - Calcul des statistiques finales et réinitialisation des listes.

Chaque étape possède des user stories dédiées, rassemblées dans le répertoire `user_stories/`.
