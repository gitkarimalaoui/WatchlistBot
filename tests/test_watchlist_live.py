import utils.watchlist_live as wl


def test_alert_sent_once(monkeypatch):
    sent = []
    monkeypatch.setattr(wl, 'send_telegram_message', lambda msg: sent.append(msg) or True)

    entries = [
        {'ticker': 'ABC', 'isPump': True},
        {'ticker': 'XYZ', 'isPump': False},
    ]

    wl.seen_pumps.clear()
    wl.get_watchlist_data_for_ui(entries)
    assert sent == ['PUMP detected on ABC']
    assert 'ABC' in wl.seen_pumps

    wl.get_watchlist_data_for_ui(entries)
    assert sent == ['PUMP detected on ABC']
