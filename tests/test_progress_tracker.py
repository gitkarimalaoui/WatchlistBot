from pathlib import Path
from utils.progress_tracker import update_progress, load_progress

def test_progress_milestone(tmp_path):
    db_path = tmp_path / "test.db"
    update_progress(30000, db_path)
    rows = load_progress(db_path)
    assert rows
    date, capital, milestone = rows[-1]
    assert capital == 30000
    assert milestone == "25k"
