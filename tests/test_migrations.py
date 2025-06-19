import os
import tempfile
import sqlite3
from alembic import command
from alembic.config import Config


def run_migrations(db_path: str):
    cfg = Config(os.path.join('migration', 'alembic.ini'))
    cfg.set_main_option('sqlalchemy.url', f'sqlite:///{db_path}')
    command.upgrade(cfg, 'head')


def test_migrations_create_tables():
    with tempfile.TemporaryDirectory() as tmp:
        db_file = os.path.join(tmp, 'test.db')
        run_migrations(db_file)

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

        assert {'watchlist', 'intraday_smart', 'trades_simules'} <= tables
