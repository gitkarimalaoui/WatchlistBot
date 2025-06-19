import sqlite3
from datetime import datetime
from utils.telegram_utils import send_telegram_message

# Utiliser la base de données fusionnée
DB_PATH = "data/project_tracker.db"

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
    send_telegram_message(message)

if __name__ == "__main__":
    send_telegram_reminders()