# Module `execution.strategie_scalping`

## Role
Implements the short-term scalping algorithm used after a ticker is detected as promising. It checks breakout/pullback patterns, calculates a score from various indicators and sends real trade orders.

## Files read
- Real-time data and indicators through functions in `data/`
- OHLC data from `yfinance` for confirming breakouts and pullbacks
- Existing trades from the SQLite database via `db.trades`

## Files written
- Trade logs recorded by `db.trades.enregistrer_trade_auto`

## Public functions and classes
- `TrailingManager` – manage stop loss updates as price moves
- `enter_breakout(ticker, volume_spike=3.0, min_body_ratio=0.5)` – detect a breakout candle
- `enter_pullback(ticker, volume_spike=3.0, min_body_ratio=0.5)` – detect a pullback confirmation
- `executer_strategie_scalping(ticker, volume_spike=3.0, min_body_ratio=0.5)` – compute the score and eventually place an order

## Key variables
None (uses helper functions and returns dictionaries)


## Example flow
1. A ticker is passed from `watchlist_loop` when its pump score is high.
2. `_compute_score` gathers indicators and returns a structured dictionary.
3. `enter_breakout` or `enter_pullback` validate the entry conditions.
4. If conditions are met, `executer_ordre_reel` sends the order and the trade is logged via `enregistrer_trade_auto`.
