# Module `watchlist_loop`

## Role
Orchestrates the main detection and scalping loop. It queries market movers, enriches them with fundamentals and executes the scalping strategy when a pump score is high enough.

## Files read
- Market data via `movers_detector.get_top_movers`
- Fundamentals from external APIs via `data.fundamental_filters.get_fundamental_data`

## Files written
- Updates the SQLite watchlist through `db.fundamentals.update_fundamentals`

## Public functions
- `boucle_ia()` – run a single detection/scalping pass
- `boucle_ia_loop(interval=10)` – continuous loop calling `boucle_ia` every *interval* seconds

## Key variables
None


## Example flow
1. `boucle_ia_loop` starts and calls `boucle_ia` every few seconds.
2. `boucle_ia` gets tickers from `get_top_movers` and fetches fundamentals.
3. After updating the DB, it computes a pump score with `score_pump_ia`.
4. If the score is above threshold it triggers `executer_strategie_scalping` from `execution/strategie_scalping`.
