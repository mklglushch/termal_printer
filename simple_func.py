import sqlite3


def add_users(user_info,db_path="info.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. Створюємо таблицю, якщо вона ще не існує
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                        telegram_id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        username TEXT
                    );
                   """)

    
    cursor.execute("""
    INSERT INTO users (telegram_id, first_name, username)
    VALUES (?, ?, ?)
    ON CONFLICT(telegram_id) DO UPDATE SET
        first_name = excluded.first_name,
        username = excluded.username
    """, (user_info.id, user_info.first_name, user_info.username))

    
    conn.commit()
    conn.close()
    
    
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
def list_institution(db_path="info.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT zaklad FROM checks")
    rows = list(cursor.fetchall())
    conn.close()
    
    zaklady = [row[0] for row in rows]
    
    return "\n".join(zaklady)