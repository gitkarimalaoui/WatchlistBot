import os
from pathlib import Path
from typing import Iterable, Union

import pandas as pd

from utils.db_historical import load_historical
from utils.utils_yf_historical import fetch_historical_with_fallback
from intelligence.ai_scorer import load_model_by_version
from intelligence.features.check_tickers import analyser_ticker


DEFAULT_TICKERS = ["AAPL", "MSFT", "TSLA"]
DEFAULT_START = "2024-01-01"
DEFAULT_END = "2024-06-30"
DEFAULT_MODEL = "dummy_model_v1"
DEFAULT_REPORT = Path("reports/ai_backtest_report.csv")


def _load_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Load historical quotes from DB or fallback sources."""
    df = load_historical(ticker, start, end)
    if df is None or df.empty:
        fetched = fetch_historical_with_fallback(ticker)
        if fetched is not None:
            df = fetched
    if df is None:
        return pd.DataFrame()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    mask = (df["timestamp"] >= pd.to_datetime(start)) & (df["timestamp"] <= pd.to_datetime(end))
    return df.loc[mask].reset_index(drop=True)


def run_backtest(
    tickers: Iterable[str] = DEFAULT_TICKERS,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    model_version: str = DEFAULT_MODEL,
    report_path: Union[str, Path] = DEFAULT_REPORT,
) -> pd.DataFrame:
    """Evaluate the model on historical data and save a CSV report."""

    model = load_model_by_version(model_version)
    rows = []
    for ticker in tickers:
        df = _load_data(ticker, start, end)
        if df.empty:
            continue
        features = analyser_ticker(ticker, return_features=True)
        if not features:
            continue
        try:
            proba = model.predict_proba([features])[0][1]
        except Exception:
            proba = float(model.predict([features])[0])
        avg_return = df["close"].pct_change().mean() * 100
        rows.append({
            "ticker": ticker,
            "ai_score": round(proba * 100, 2),
            "avg_return_pct": round(avg_return, 2),
        })

    report = pd.DataFrame(rows)
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(report_path)
    return report


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    import argparse

    parser = argparse.ArgumentParser(description="Run AI backtest")
    parser.add_argument("--tickers", nargs="*", default=DEFAULT_TICKERS)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    df_report = run_backtest(
        tickers=args.tickers,
        start=args.start,
        end=args.end,
        model_version=args.model,
        report_path=args.output,
    )
    print(df_report)
    print(f"Report saved to {args.output}")
