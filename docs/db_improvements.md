# Database Improvement Plan

The profiling report highlights many columns that are either entirely NULL or contain constant values.
To keep the codebase maintainable the following actions are recommended:

1. **Handle missing values gracefully**
   - Use helper functions from `db.checks` to detect nearly empty columns.
   - When reading data, fallback to defaults if indicators like `rsi` or `ema_diff` are missing.

2. **Ignore unused columns**
   - Columns such as `historique_yf.*` or fields in `watchlist` that are never populated should be excluded from queries.
   - Future migrations can drop these columns once confirmed they are not required.

3. **Mock data generation for tests**
   - `scripts/mock_db_fill.py` can create minimal rows in each table so automated tests run with predictable values.

4. **Automated integrity checks**
   - Add tests using the new utilities to ensure critical columns are not completely empty.
   - This prevents silent regressions when ingestion scripts fail to populate data.
