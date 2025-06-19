import sqlite3

from db.checks import column_null_ratio, constant_value_columns, has_data


def _make_db(tmp_path):
    db = tmp_path / "t.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t(id INTEGER, a REAL, b REAL)")
    conn.executemany(
        "INSERT INTO t VALUES (?, ?, ?)",
        [
            (1, None, 1.0),
            (2, None, 1.0),
        ],
    )
    conn.commit()
    return conn


def test_column_null_ratio(tmp_path):
    conn = _make_db(tmp_path)
    ratios = column_null_ratio(conn, "t")
    conn.close()
    assert ratios["a"] == 1.0
    assert ratios["b"] == 0.0


def test_constant_value_columns(tmp_path):
    conn = _make_db(tmp_path)
    cols = constant_value_columns(conn, "t")
    conn.close()
    assert set(cols) == {"a", "b"}


def test_has_data(tmp_path):
    conn = _make_db(tmp_path)
    assert not has_data(conn, "t", ["a"])
    assert has_data(conn, "t", ["b"])
    conn.close()
