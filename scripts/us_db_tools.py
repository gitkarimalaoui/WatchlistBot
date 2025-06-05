
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'user_stories.db'))

def connect_db():
    return sqlite3.connect(DB_PATH)

def get_user_stories_by_epic(epic):
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM user_stories WHERE epic = ?", conn, params=(epic,))
    conn.close()
    return df

def insert_user_story(row):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_stories (id, epic, story, criteria, module, priority, status, testable)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(row))
    conn.commit()
    conn.close()

def delete_user_story(us_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_stories WHERE id = ?", (us_id,))
    conn.commit()
    conn.close()

def import_from_excel(filepath):
    df = pd.read_excel(filepath)
    df = df[["ID", "Epic", "User Story", "Acceptance Criteria", "Module", "Priority", "Status", "Testable"]]
    df.columns = ["id", "epic", "story", "criteria", "module", "priority", "status", "testable"]
    conn = connect_db()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO user_stories (id, epic, story, criteria, module, priority, status, testable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
    conn.commit()
    conn.close()
