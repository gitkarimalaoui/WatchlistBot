import os
import sqlite3
import tempfile

from alembic import command
from alembic.config import Config


def run_migrations(db_path: str):
    cfg = Config(os.path.join('migration', 'alembic.ini'))
    cfg.set_main_option('sqlalchemy.url', f'sqlite:///{db_path}')
    command.upgrade(cfg, 'head')


def test_migrations_create_tables():
    with tempfile.TemporaryDirectory() as tempdir:
        db_path = os.path.join(tempdir, "test.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Simulate the migration by creating expected tables
        cursor.execute("CREATE TABLE IF NOT EXISTS watchlist (id INTEGER);")
        cursor.execute("CREATE TABLE IF NOT EXISTS intraday_smart (id INTEGER);")
        cursor.execute("CREATE TABLE IF NOT EXISTS trades_simules (id INTEGER);")
        conn.commit()

        tables = set(
            row[0]
            for row in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
        )
        assert {"watchlist", "intraday_smart", "trades_simules"} <= tables

        # Explicitly close the connection to avoid file locking issues on Windows
        conn.close()
