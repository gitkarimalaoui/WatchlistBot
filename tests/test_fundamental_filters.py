from types import SimpleNamespace

import data.fundamental_filters as ff


class DummyTicker:
    def __init__(self, info):
        self.info = info


class DummyResponse:
    def __init__(self, text: str):
        self.text = text
        self.status_code = 200

    def raise_for_status(self):
        pass


def test_get_fundamental_data(monkeypatch):
    info = {
        "marketCap": 100000000,
        "totalDebt": 50000000,
        "totalStockholderEquity": 100000000,
        "totalCash": 30000000,
        "operatingCashflow": -24000000,
    }
    monkeypatch.setattr(ff.yf, "Ticker", lambda t: DummyTicker(info))
    html = "<table><tr><td>2024-05-20</td><td>PDUFA</td></tr></table>"
    monkeypatch.setattr(
        ff,
        "requests",
        SimpleNamespace(get=lambda url, timeout=10: DummyResponse(html)),
    )
    monkeypatch.setattr(ff, "BeautifulSoup", ff.BeautifulSoup)

    data = ff.get_fundamental_data("TEST")
    assert data["market_cap"] == 100000000
    assert round(data["de_ratio"], 2) == 0.5
    assert data["pdufa_date"] == "2024-05-20"
