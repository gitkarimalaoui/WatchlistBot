# Version History

## v7.04 (2025-06-21)

### Added
- **Auto scalping** – new strategy with breakout/pullback entries and trailing stop (`execution/strategie_scalping.py`).
  *Origin: Codex*
- **Streamlit auto refresh** – optional automatic page refresh in the UI using `streamlit_autorefresh` (`ui/app_unifie_watchlistbot.py`).
  *Origin: Codex*
- **Backtest module** – base framework for scalping backtests (`backtest/` directory).
  *Origin: Codex*
- **Telegram alerts** – centralized notifier for trade events (`telegram_notifier.py`, `utils/telegram_utils.py`).
  *Origin: Codex*

### Test Status
- Running `pytest` results in 1 failing test, 65 passing and 8 skipped:
  ```
  tests/test_strategie_scalping.py::test_executer_strategie_scalping FAILED
  1 failed, 65 passed, 8 skipped, 7 warnings
  ```
- Async tests are skipped with warnings due to missing `pytest-asyncio` plugin.

