import json
from utils.progress_tracker import (
    detect_milestone,
    record_progress,
    get_latest_progress,
    update_roadmap_from_progress,
)


def test_detect_milestone():
    assert detect_milestone(50) == "0"
    assert detect_milestone(6000) == "5000"


def test_record_and_update(tmp_path):
    db_path = tmp_path / "progress.db"
    json_path = tmp_path / "roadmap.json"
    json_path.write_text(json.dumps({"step": "00/100"}))

    milestone = record_progress(capital=1500, pnl=100, db_path=db_path, day="2023-01-01")
    assert milestone == "1000"

    row = get_latest_progress(db_path=db_path)
    assert row[1] == 1500
    assert row[2] == 100

    update_roadmap_from_progress(db_path=db_path)

