import sqlite3
import pandas as pd

conn = sqlite3.connect("data/trades.db")
df_info = pd.read_sql_query("PRAGMA table_info(watchlist);", conn)
conn.close()

print(df_info)
