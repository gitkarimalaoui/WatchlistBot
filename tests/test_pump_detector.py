import os
import pandas as pd
import tempfile

import realtime.pump_detector as mod


def make_ticks(prices, volumes):
    now = pd.Timestamp.now().floor("T")
    data = []
    for i, (p, v) in enumerate(zip(prices, volumes)):
        ts = now - pd.Timedelta(minutes=len(prices)-i-1)
        data.append({"timestamp": ts.value // 10**9, "c": p, "v": v, "o": p, "h": p, "l": p})
    return pd.DataFrame(data)


def test_detect_pump(monkeypatch):
    prices = [1, 1.02, 1.05, 1.1, 1.3]
    volumes = [100, 100, 1000, 1000, 8000]
    df = make_ticks(prices, volumes)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "TEST.csv")
        df.to_csv(path, index=False)
        monkeypatch.setattr(mod, "TICKS_DIR", tmp)
        rules = {"price_spike_pct": 20, "volume_ratio_min": 2}
        alerts = {}
        monkeypatch.setattr(mod, "envoyer_alerte_ia", lambda t, s, g: alerts.setdefault("sent", True))
        metrics = mod.detect_pump("TEST", rules)
        assert metrics["alert_sent"] is True
        assert alerts.get("sent")


def test_trailing_stop_exit():
    ts = mod.TrailingStop(entry_price=10, trailing_pct=10)
    prices = [10, 12, 13, 11]
    exit_hit = None
    for p in prices[1:]:
        ts.update(p)
        if ts.should_exit(p):
            exit_hit = p
            break
    assert exit_hit == 11
