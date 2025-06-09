import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("PROGRESS_DB_PATH", PROJECT_ROOT / "data" / "project_tracker.db"))
ROADMAP_JSON = PROJECT_ROOT / "project_doc" / "roadmap_sync.json"

MILESTONES = [1000, 5000, 10000, 20000, 50000, 100000]


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS progress (
            day TEXT PRIMARY KEY,
            capital REAL NOT NULL,
            pnl REAL NOT NULL,
            milestone TEXT
        )"""
    )
    return conn


def detect_milestone(capital: float) -> str:
    for m in sorted(MILESTONES, reverse=True):
        if capital >= m:
            return str(m)
    return "0"


def record_progress(capital: float, pnl: float, day: str | None = None, db_path: Path = DB_PATH) -> str:
    if day is None:
        day = datetime.now().date().isoformat()
    milestone = detect_milestone(capital)
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO progress (day, capital, pnl, milestone) VALUES (?, ?, ?, ?)",
            (day, capital, pnl, milestone),
        )
    conn.close()
    return milestone


def get_latest_progress(db_path: Path = DB_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT day, capital, pnl, milestone FROM progress ORDER BY day DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row


def update_roadmap_from_progress(db_path: Path = DB_PATH, json_path: Path = ROADMAP_JSON) -> None:
    latest = get_latest_progress(db_path)
    if not latest:
        return
    capital = latest[1]
    step = int(capital // 1000)
    if not json_path.exists():
        return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["step"] = f"{step:02d}/100"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


TRADES_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "trades.db"


def init_progress_table(db_path: Path = TRADES_DB_PATH) -> None:
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


def update_progress(capital: float, db_path: Path = TRADES_DB_PATH) -> None:
    init_progress_table(db_path)
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


def load_progress(db_path: Path = TRADES_DB_PATH):
    init_progress_table(db_path)
    conn = sqlite3.connect(db_path)
    df = conn.execute("SELECT * FROM progress ORDER BY date").fetchall()
    conn.close()
    return df
