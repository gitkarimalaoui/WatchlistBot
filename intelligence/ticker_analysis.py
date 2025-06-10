import os
import joblib
from intelligence.features.check_tickers import analyser_ticker

MODEL_PATH = os.path.join('models', 'modele_ia.pkl')
_model = None


def _load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
    return _model


def score_ticker(ticker: str) -> float:
    """Return AI score percentage for the given ticker."""
    model = _load_model()
    features = analyser_ticker(ticker, return_features=True)
    if model is None or not features:
        return 0.0
    prob = model.predict_proba([features])[0][1]
    return round(prob * 100, 2)
