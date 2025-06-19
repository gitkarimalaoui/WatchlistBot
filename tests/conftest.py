import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def tmp_trades_db(tmp_path):
    orig = Path('data/trades.db')
    backup = None
    if orig.exists():
        backup = tmp_path / 'trades_backup.db'
        shutil.copy(orig, backup)
    db_file = tmp_path / 'trades.db'
    yield db_file
    if backup and orig.exists():
        shutil.copy(backup, orig)
