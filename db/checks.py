import sqlite3
from typing import Dict, List


def column_null_ratio(conn: sqlite3.Connection, table: str) -> Dict[str, float]:
    """Return ratio of NULL values for each column in ``table``."""
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    ratios = {}
    total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    for col in cols:
        if total == 0:
            ratios[col] = 1.0
            continue
        nulls = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL"
        ).fetchone()[0]
        ratios[col] = nulls / total
    return ratios


def constant_value_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    """Return columns where all rows have the same value (including NULL)."""
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    constants = []
    for col in cols:
        values = conn.execute(
            f"SELECT COUNT(DISTINCT {col}) FROM {table}"
        ).fetchone()[0]
        if values <= 1 and total > 0:
            constants.append(col)
    return constants


def has_data(
    conn: sqlite3.Connection, table: str, columns: List[str], threshold: float = 0.95
) -> bool:
    """Check that each column has at least ``1-threshold`` fraction of data."""
    ratios = column_null_ratio(conn, table)
    return all(ratios.get(col, 1.0) < threshold for col in columns)
