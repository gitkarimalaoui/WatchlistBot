import os
import tempfile
from sqlalchemy import create_engine, inspect
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
        engine = create_engine(f'sqlite:///{db_file}')
        insp = inspect(engine)
        tables = set(insp.get_table_names())
        assert {'watchlist', 'intraday_smart', 'trades_simules'} <= tables
