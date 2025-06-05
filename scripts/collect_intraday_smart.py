# scripts/collect_intraday_smart.py
import time
import asyncio
import sqlite3
import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.smart_collector import SmartFinancialDataCollector
except ImportError as e:
    print(f"Import error: {e}")
    from smart_collector import SmartFinancialDataCollector

DB_PATH = "data/trades.db"

def ensure_db_exists():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS intraday_smart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                price REAL,
                change_val REAL,
                change_percent REAL,
                volume INTEGER,
                high REAL,
                low REAL,
                source TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_watchlist_tickers():
    ensure_db_exists()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT DISTINCT ticker FROM watchlist WHERE ticker IS NOT NULL", conn)
        conn.close()
        tickers = df['ticker'].dropna().unique().tolist()
        return tickers if tickers else ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    except Exception as e:
        print(f"Erreur récupération watchlist: {e}")
        return ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

def insert_intraday_to_db(data_list):
    if not data_list:
        return

    ensure_db_exists()
    
    db_data = []
    for item in data_list:
        db_data.append({
            'ticker': item.get('ticker'),
            'price': item.get('price', 0),
            'change_val': item.get('change', 0),
            'change_percent': item.get('change_percent', 0),
            'volume': item.get('volume', 0),
            'high': item.get('high', 0),
            'low': item.get('low', 0),
            'source': item.get('source', 'unknown'),
            'timestamp': str(item.get('timestamp', datetime.now()))
        })
    
    df = pd.DataFrame(db_data)
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df.to_sql("intraday_smart", conn, if_exists="append", index=False)
        print(f"✅ {len(df)} enregistrements insérés.")
    except Exception as e:
        print(f"❌ Erreur insertion DB: {e}")

async def telecharger_intraday_smart(ticker: str):
    collector = SmartFinancialDataCollector()
    
    try:
        await collector.create_session_pool()
        result = await collector.fetch_ticker_smart(ticker)
        
        if result:
            insert_intraday_to_db([result])
            print(f"[OK] {ticker} → Succès")
            return pd.DataFrame([result])
        else:
            print(f"[FAIL] {ticker} → Échec")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"[ERROR] {ticker} → {e}")
        return pd.DataFrame()
        
    finally:
        await collector.cleanup()
