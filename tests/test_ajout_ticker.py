
import os
import sqlite3
import pytest

pytest.skip("database not available", allow_module_level=True)

def test_ajout_ticker():
    conn = sqlite3.connect("data/watchlist.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO watchlist (ticker, source) VALUES (?, ?)", ("TEST", "manuel"))
    conn.commit()
    cursor.execute("SELECT * FROM watchlist WHERE ticker = 'TEST'")
    result = cursor.fetchone()
    conn.close()
    assert result is not None, "Ticker TEST non trouvé dans la base"
