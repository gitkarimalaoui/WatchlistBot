import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"


def init_progress_table(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            date TEXT PRIMARY KEY,
            capital REAL NOT NULL,
            milestone TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def update_progress(capital: float, db_path: Path = DB_PATH) -> None:
    init_progress_table(db_path)
    milestone = ""
    if capital >= 100000:
        milestone = "target_reached"
    elif capital >= 75000:
        milestone = "75k"
    elif capital >= 50000:
        milestone = "50k"
    elif capital >= 25000:
        milestone = "25k"
    else:
        milestone = "start"

    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO progress (date, capital, milestone) VALUES (?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), capital, milestone),
    )
    conn.commit()
    conn.close()


def load_progress(db_path: Path = DB_PATH):
    init_progress_table(db_path)
    conn = sqlite3.connect(db_path)
    df = conn.execute("SELECT * FROM progress ORDER BY date").fetchall()
    conn.close()
    return df

