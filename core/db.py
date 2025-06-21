import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.getenv("DB_PATH")
if DB_PATH:
    DB_PATH = Path(DB_PATH)
else:
    DB_PATH = Path("data/trades.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_session():
    return SessionLocal()
