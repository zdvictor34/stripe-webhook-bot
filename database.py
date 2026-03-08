import sqlite3
from datetime import datetime, timedelta

DB_NAME = "vip_users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            vip_until TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_or_update_user(telegram_id, vip_days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    vip_until = datetime.utcnow() + timedelta(days=vip_days)

    cursor.execute("""
        INSERT OR REPLACE INTO users (telegram_id, vip_until)
        VALUES (?, ?)
    """, (telegram_id, vip_until.isoformat()))

    conn.commit()
    conn.close()


def is_user_active(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT vip_until FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result:
        return False

    vip_until = datetime.fromisoformat(result[0])
    return vip_until > datetime.utcnow()
