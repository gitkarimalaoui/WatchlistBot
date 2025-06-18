# Audit Summary: WatchlistBot

This summary provides an overview of the repository structure and highlights the modules involved in the WatchlistBot trading assistant. The project combines data ingestion, scoring, a Streamlit UI, and automation scripts. Detailed documentation is found under `project_doc/`.

## Project Structure

```
.
./.git
./JobAutomationAssistant
./USER STORIES
./aiohttp
./automation
./backtest
./cafe
./config
./core
./data
./docs
./dotenv
./fusion
./intelligence
./migration
./models
./notifications
./project_doc
./realtime
./scripts
./simulation
./tests
./ui
./utils
```

Python files count: 172 (see `py_files.txt` for the complete list).

## Main Components

- `ui/app_unifie_watchlistbot.py`: Main Streamlit interface with navigation, manual ticker entry, and progress tracking toward the $100k milestone. Includes features to compute a global score combining AI metrics and news sentiment.
- `intelligence/ai_scorer.py`: Provides functions `score_ai` and `compute_global_score` to generate an overall score for tickers using multiple indicators. Also includes `load_model_by_version` to load predictive models.
- `automation/orchestrateur_evenements.py`: Collects events from various databases, analyzes priority, schedules actions, and dispatches notifications. Useful for coordinating tasks and potential trading actions.
- `utils/progress_tracker.py`: Manages progress data in `project_tracker.db`, with milestones up to $100k. Functions allow recording daily progress and updating a JSON roadmap.
- `scripts/*`: Numerous command line utilities for data collection, scraping, and batch processing (e.g., `batch_news_scoring.py`).

## Documentation

Project documentation is extensive under `project_doc/`. `project_structure.md` enumerates modules and references user stories. Modules related to AI scoring, watchlist management, and trading simulation are described there.

## Example User Story (Generated)

```
User Story: As a trader, I want the bot to compute a global score for each ticker so that I can rank opportunities.
Acceptance Criteria:
- Scores combine AI predictions, GPT news score, price change, volume and float.
- Results are displayed in the Streamlit watchlist page.
Dependencies: `ai_scorer.py`, `app_unifie_watchlistbot.py`, database tables `watchlist` and `news_score`.
```

## Happy Path Overview

1. User launches the UI via `streamlit run ui/app_unifie_watchlistbot.py`.
2. The UI loads watchlist data from `data/trades.db` and computes global scores with `intelligence/ai_scorer.compute_global_score`.
3. Progress toward $100k is tracked in `utils/progress_tracker.py` and displayed.
4. Background scripts in `automation/orchestrateur_evenements.py` can schedule trading-related events and send notifications.
5. Optional training occurs via `intelligence/learning_loop.py` (not covered in depth).

## Improvement Ideas

- Reduce unused scripts and clarify active modules to ease maintenance.
- Provide a diagram linking `ui`, `intelligence`, `automation`, and `scripts` for newcomers.
- Automate continuous updates of progress metrics and integrate with backtest results.

## Running the Function Audit

Use the helper script to generate a list of all functions in the repository and
check whether they are referenced elsewhere. The output appears as a Markdown
table which can be redirected to a file:

```bash
python scripts/generate_function_audit.py > function_audit.md
```

The table reports each function signature, the module path, if it is used in the
codebase, the matching documentation heading (when available) and a placeholder
user story when no documentation is found.

