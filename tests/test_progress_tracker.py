from pathlib import Path
from utils.progress_tracker import update_progress, load_progress, project_target_date
from datetime import date, timedelta

def test_progress_milestone(tmp_path):
    db_path = tmp_path / "test.db"
    update_progress(30000, db_path)
    rows = load_progress(db_path)
    assert rows
    day, capital, milestone = rows[-1]
    assert capital == 30000
    assert milestone == "25k"

def test_project_target_date():
    today = date.today()
    target = project_target_date(90000, 1000)
    assert target == today + timedelta(days=10)
