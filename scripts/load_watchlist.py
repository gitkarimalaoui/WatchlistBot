# scripts/load_watchlist.py

import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]
DB_FILE  = BASE_DIR / "data" / "trades.db"
TXT_FILE = BASE_DIR / "data" / "watchlist_jaguar.txt"

def main():
    conn = sqlite3.connect(DB_FILE)
    with open(TXT_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split("|", 1)]
            # Skip lines without a proper description
            if len(parts) != 2 or not parts[1]:
                continue

            ticker, desc = parts
            # Use INSERT OR REPLACE to update existing rows or insert new ones
            conn.execute("""
                INSERT OR REPLACE INTO watchlist
                  (ticker, source, date, description, updated_at)
                VALUES (?, 'Jaguar', ?, ?, CURRENT_TIMESTAMP)
            """, (
                ticker,
                datetime.now().isoformat(),  # scrape time
                desc
            ))

    conn.commit()
    conn.close()
    print("Load complete: watchlist_jaguar.txt upserted into database.")

if __name__ == "__main__":
    main()
