import sqlite3
from datetime import datetime
import os
from telegram import Bot

# Utiliser la base de données fusionnée
DB_PATH = "data/project_tracker.db"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_bot_token")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")

bot = Bot(token=TELEGRAM_TOKEN)

def connect():
    return sqlite3.connect(DB_PATH)

def add_task(us_id, description, type="tech", due_date=None, reminder=True):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (us_id, type, description, due_date, done, reminder) VALUES (?, ?, ?, ?, 0, ?)",
        (us_id, type, description, due_date, int(reminder))
    )
    conn.commit()
    conn.close()

def get_todo_today():
    conn = connect()
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    cursor.execute(
        "SELECT id, description, due_date FROM tasks WHERE done = 0 AND (reminder = 1 OR due_date = ?)",
        (today,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def mark_task_done(task_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def send_telegram_reminders():
    tasks = get_todo_today()
    if not tasks:
        return
    message = "\U0001F4CB *BOTV7 – Today's Tasks:*\n"
    for task in tasks:
        message += f"\n✅ Task #{task[0]}: {task[1]} (Due: {task[2] or 'Anytime'})"
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    send_telegram_reminders()