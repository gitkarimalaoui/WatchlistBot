import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import math
from typing import Optional

# ─── Paths and Constants ───────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("PROGRESS_DB_PATH", PROJECT_ROOT / "data" / "project_tracker.db"))
ROADMAP_JSON = PROJECT_ROOT / "project_doc" / "roadmap_sync.json"

MILESTONES = [1000, 5000, 10000, 25000, 50000, 100000]
TARGET_CAPITAL = 100000

# ─── Initialization ────────────────────────────────────────────────────────────
def init_progress_table(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            day TEXT PRIMARY KEY,
            capital REAL NOT NULL,
            pnl REAL,
            milestone TEXT
        )
        """
    )
    conn.commit()
    conn.close()

# ─── Core Functions ────────────────────────────────────────────────────────────
def detect_milestone(capital: float) -> str:
    for m in sorted(MILESTONES, reverse=True):
        if capital >= m:
            return str(m)
    return "0"

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    init_progress_table(db_path)
    return sqlite3.connect(db_path)

def record_progress(capital: float, pnl: float, day: Optional[str] = None, db_path: Path = DB_PATH) -> str:
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

def load_progress(db_path: Path = DB_PATH):
    init_progress_table(db_path)
    conn = sqlite3.connect(db_path)
    df = conn.execute(
        "SELECT day, capital, milestone FROM progress ORDER BY day"
    ).fetchall()
    conn.close()
    return df

def project_target_date(capital: float, daily_gain: float, target: float = TARGET_CAPITAL):
    """Return the estimated date to reach ``target`` assuming ``daily_gain`` profit.

    If ``daily_gain`` is non-positive the function returns ``None``.
    """
    if daily_gain <= 0:
        return None
    remaining = max(target - capital, 0)
    days = math.ceil(remaining / daily_gain)
    return datetime.now().date() + timedelta(days=days)

# Legacy API --------------------------------------------------------------
def update_progress(capital: float, db_path: Path = DB_PATH) -> str:
    """Backward compatible wrapper that stores milestones like ``25k``."""
    init_progress_table(db_path)
    day = datetime.now().date().isoformat()
    milestone = detect_milestone(capital)
    if milestone.isdigit() and int(milestone) >= 1000:
        milestone_label = f"{int(milestone)//1000}k"
    else:
        milestone_label = milestone
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO progress (day, capital, pnl, milestone) VALUES (?, ?, ?, ?)",
            (day, capital, 0, milestone_label),
        )
    conn.close()
    return milestone_label
