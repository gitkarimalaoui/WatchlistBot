# Module `intelligence.ai_scorer`

## Role
Provides utilities to compute AI-based scores from raw ticker data, blend them with other metrics and load trained models.

## Files read
- `rules_auto.json` next to the module, containing scoring weights
- Model files `<version>.pkl` or `<version>.pkl.b64` inside `models/`

## Files written
None

## Public functions
- `score_ai(ticker_data)` – apply the rules from `rules_auto.json`
- `compute_global_score(score_ai_val, gpt_score, percent_gain, volume, float_shares, sentiment)` – combine indicators into a 0–10 score
- `load_model_by_version(version)` – load a model file and return the model object

## Key variables
- `RULES` – dictionary loaded from `rules_auto.json`
- `MODELS_DIR` – directory containing model pickles


## Example flow
1. Market data for a ticker is collected elsewhere in the code.
2. `score_ai` computes a raw numeric value based on `RULES`.
3. This value is passed along with sentiment, gain and volume to `compute_global_score`.
4. A trained model loaded with `load_model_by_version` can further classify the ticker for trading decisions.
