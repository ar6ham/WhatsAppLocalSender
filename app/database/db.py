"""
مدیریت SQLite محلی - تمام داده‌ها روی دیسک کاربر
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import DATABASE_PATH
from app.utils.logger import logger


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def db_session():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """ایجاد جداول در صورت عدم وجود"""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with db_session() as conn:
        cursor = conn.cursor()

        # جدول مخاطبین
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL UNIQUE,
                name TEXT,
                region TEXT,
                tags TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # جدول کمپین‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                attachment_path TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                delay_min REAL DEFAULT 3.0,
                delay_max REAL DEFAULT 8.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
        """)

        # ارتباط کمپین و مخاطب + وضعیت ارسال
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                contact_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                sent_at TEXT,
                attempts INTEGER DEFAULT 0,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                UNIQUE(campaign_id, contact_id)
            )
        """)

        # لاگ ارسال‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS send_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                contact_id INTEGER,
                phone TEXT,
                status TEXT,
                message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
            )
        """)

        # تنظیمات محلی
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cc_campaign ON campaign_contacts(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cc_status ON campaign_contacts(status)")

        logger.info("دیتابیس محلی با موفقیت مقداردهی شد.")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
