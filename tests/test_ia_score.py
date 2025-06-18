import types
import sys

dummy_graph = types.ModuleType("utils_graph")
dummy_graph.plot_dual_chart = lambda *a, **k: None
dummy_graph.charger_historique_intelligent = lambda *a, **k: None
dummy_graph.charger_intraday_intelligent = lambda *a, **k: None
sys.modules.setdefault("utils_graph", dummy_graph)

dummy_order = types.ModuleType("utils.order_executor")
dummy_order.executer_ordre_reel_direct = lambda *a, **k: None
sys.modules.setdefault("utils.order_executor", dummy_order)

sys.modules.setdefault("utils_signaux", types.ModuleType("utils_signaux"))
sys.modules["utils_signaux"].is_buy_signal = lambda *a, **k: False

import pytest
from ui.utils_affichage_ticker import _ia_score


def test_ia_score_basic():
    data = {
        "rsi": 60,
        "ema9": 12,
        "ema21": 10,
        "price": 5,
        "vwap": 4,
        "volume_ratio": 1.6,
        "source": "FDA",
    }
    score, details = _ia_score(data, return_breakdown=True)
    assert score == 95
    assert details == {"RSI": 15, "EMA": 25, "VWAP": 15, "Vol": 15, "FDA": 25}

