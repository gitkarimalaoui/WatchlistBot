from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from .db import Base


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    last_price = Column(Float)
    volume = Column(Integer)
    float = Column(Integer)
    change_percent = Column(Float)
    score = Column(Float)
    source = Column(String)
    date = Column(String)
    description = Column(String)
    has_fda = Column(Boolean, default=False)
    updated_at = Column(DateTime)


class IntradaySmart(Base):
    __tablename__ = "intraday_smart"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    price = Column(Float)
    change_val = Column(Float)
    change_percent = Column(Float)
    volume = Column(Integer)
    high = Column(Float)
    low = Column(Float)
    source = Column(String)
    timestamp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class TradeSimule(Base):
    __tablename__ = "trades_simules"

    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    prix_achat = Column(Float)
    quantite = Column(Integer)
    frais = Column(Float)
    montant_total = Column(Float)
    sl = Column(Float)
    tp = Column(Float)
    exit_price = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    provenance = Column(String)
    note = Column(String)


class TradeReel(Base):
    __tablename__ = "trades_reels"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Float)
    qty = Column(Integer)
    side = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
