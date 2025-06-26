import sqlite3
from db import refactor_tasks as rt


def test_upsert_and_fetch(tmp_path):
    db_file = tmp_path / "project_tracker.db"
    tasks = [
        {"id": "T1", "description": "desc", "module": "mod", "priority": "High", "status": "Todo"}
    ]
    rt.upsert_tasks(tasks, db_file)
    rows = rt.fetch_tasks(db_file)
    assert rows == tasks
