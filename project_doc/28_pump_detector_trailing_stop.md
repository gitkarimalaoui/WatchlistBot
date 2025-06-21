# 📘 Pump Detector & Trailing Stop

Ce module surveille en temps r\u00e9el la table `ticks` (parfois nomm\u00e9e
`intraday_smart`) afin de rep\u00e9rer les hausses de prix brusques
("pumps"). Pour chaque ticker, on calcule :

- **Variation sur quelques minutes** (\`price_change\`)
- **Ratio de volume** par rapport \u00e0 la moyenne r\u00e9cente
- **Score global** via `compute_global_score`

Les seuils sont param\u00e9tr\u00e9s dans `config/rules_auto.json` :
`volume_ratio_min`, `price_spike_pct` et `trailing_stop_pct`.
Lorsque ces limites sont d\u00e9pass\u00e9es, une alerte Telegram est envoy\u00e9e
avec `envoyer_alerte_ia`.

Pour sortir d\u00e9licatement d'une position gagnante, une classe
`TrailingStop` ajuste automatiquement un niveau de stop en fonction du
plus haut atteint. La fonction `simulate_trailing_trade` illustre son
utilisation en estimant le gain net via `executer_trade_simule`.
