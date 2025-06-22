import sqlite3
from assistant_vocal import interpret_command, _list_tickers, _best_scores


def test_interpret_command():
    assert interpret_command("liste des tickers")[0] == "list_tickers"
    action, param = interpret_command("exécute achat de abc")
    assert action == "buy" and param == "ABC"
    assert interpret_command("quels sont les meilleurs scores IA ?")[0] == "best_scores"
    assert interpret_command("ferme la journée")[0] == "close_day"


def test_list_and_scores(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE watchlist (ticker TEXT, score REAL)")
    conn.executemany(
        "INSERT INTO watchlist (ticker, score) VALUES (?, ?)",
        [("AAA", 5.0), ("BBB", 8.0), ("CCC", 7.0)],
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr('assistant_vocal.DB_PATH', str(db))
    tickers = _list_tickers()
    assert "AAA" in tickers

    scores = _best_scores()
    assert "BBB" in scores

