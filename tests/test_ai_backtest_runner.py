import pandas as pd

from backtest.ai_backtest_runner import run_backtest


class DummyModel:
    def predict_proba(self, X):
        return [[0.2, 0.8] for _ in X]


def test_run_backtest(monkeypatch, tmp_path):
    df_sample = pd.DataFrame({
        "timestamp": [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-02')],
        "close": [1.0, 1.1],
    })
    monkeypatch.setattr(
        'backtest.ai_backtest_runner._load_data',
        lambda *a, **k: df_sample,
    )
    monkeypatch.setattr(
        'backtest.ai_backtest_runner.load_model_by_version',
        lambda v: DummyModel(),
    )
    monkeypatch.setattr(
        'backtest.ai_backtest_runner.analyser_ticker',
        lambda t, return_features=False: [1, 2, 3],
    )
    output = tmp_path / 'report.csv'
    df = run_backtest(['TEST'], '2024-01-01', '2024-01-02', 'dummy', output)
    assert not df.empty
    assert output.exists()

