-- Table TRADES
ALTER TABLE trades ADD COLUMN score_at_entry INTEGER;
ALTER TABLE trades ADD COLUMN pump_pct_60s REAL;
ALTER TABLE trades ADD COLUMN rsi_at_entry REAL;
ALTER TABLE trades ADD COLUMN ema9 REAL;
ALTER TABLE trades ADD COLUMN ema21 REAL;
ALTER TABLE trades ADD COLUMN momentum REAL;
ALTER TABLE trades ADD COLUMN source_data TEXT;

-- Table WATCHLIST
ALTER TABLE watchlist ADD COLUMN pump_pct_60s REAL;
ALTER TABLE watchlist ADD COLUMN ema_diff REAL;
ALTER TABLE watchlist ADD COLUMN rsi REAL;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_intraday_smart_ticker ON intraday_smart(ticker);
CREATE INDEX IF NOT EXISTS idx_intraday_smart_ticker_created_at ON intraday_smart(ticker, created_at);
