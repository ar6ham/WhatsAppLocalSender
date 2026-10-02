"""
لایه دسترسی به داده - عملیات CRUD محلی
"""
from typing import List, Optional, Dict, Any
from app.database.db import db_session, now_iso
from app.utils.logger import logger


# ──────────────────── Contacts ────────────────────

def add_contact(phone: str, name: str = None, region: str = None,
                tags: str = None, notes: str = None) -> Optional[int]:
    with db_session() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO contacts (phone, name, region, tags, notes, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (phone, name, region, tags, notes, now_iso(), now_iso())
            )
            return cur.lastrowid
        except Exception as e:
            if "UNIQUE" in str(e).upper():
                return None  # تکراری
            raise


def get_contact_by_phone(phone: str) -> Optional[Dict]:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE phone = ?", (phone,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_all_contacts() -> List[Dict]:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]


def delete_contact(contact_id: int) -> bool:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        return cur.rowcount > 0


def bulk_add_contacts(contacts: List[Dict]) -> Dict[str, int]:
    """افزودن دسته‌ای. برمی‌گرداند: added, skipped, failed"""
    added = skipped = failed = 0
    with db_session() as conn:
        cur = conn.cursor()
        for c in contacts:
            try:
                cur.execute(
                    """INSERT INTO contacts (phone, name, region, tags, notes, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        c["phone"],
                        c.get("name"),
                        c.get("region"),
                        c.get("tags"),
                        c.get("notes"),
                        now_iso(),
                        now_iso()
                    )
                )
                added += 1
            except Exception as e:
                if "UNIQUE" in str(e).upper():
                    skipped += 1
                else:
                    failed += 1
                    logger.debug(f"خطا در افزودن مخاطب: {e}")
    return {"added": added, "skipped": skipped, "failed": failed}


def clear_all_contacts() -> int:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM contacts")
        return cur.rowcount


# ──────────────────── Campaigns ────────────────────

def create_campaign(name: str, message: str, attachment_path: str = None,
                    delay_min: float = 3.0, delay_max: float = 8.0) -> int:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO campaigns (name, message, attachment_path, status, delay_min, delay_max, created_at, updated_at)
               VALUES (?, ?, ?, 'draft', ?, ?, ?, ?)""",
            (name, message, attachment_path, delay_min, delay_max, now_iso(), now_iso())
        )
        return cur.lastrowid


def get_campaign(campaign_id: int) -> Optional[Dict]:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_all_campaigns() -> List[Dict]:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM campaigns ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]


def update_campaign_status(campaign_id: int, status: str, **kwargs):
    fields = ["status = ?", "updated_at = ?"]
    values = [status, now_iso()]
    if "started_at" in kwargs:
        fields.append("started_at = ?")
        values.append(kwargs["started_at"])
    if "finished_at" in kwargs:
        fields.append("finished_at = ?")
        values.append(kwargs["finished_at"])
    values.append(campaign_id)
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE campaigns SET {', '.join(fields)} WHERE id = ?", values)


def delete_campaign(campaign_id: int) -> bool:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
        return cur.rowcount > 0


def add_contacts_to_campaign(campaign_id: int, contact_ids: List[int]) -> int:
    added = 0
    with db_session() as conn:
        cur = conn.cursor()
        for cid in contact_ids:
            try:
                cur.execute(
                    """INSERT INTO campaign_contacts (campaign_id, contact_id, status)
                       VALUES (?, ?, 'pending')""",
                    (campaign_id, cid)
                )
                added += 1
            except Exception:
                pass  # تکراری
    return added


def get_campaign_contacts(campaign_id: int, status: str = None) -> List[Dict]:
    with db_session() as conn:
        cur = conn.cursor()
        if status:
            cur.execute(
                """SELECT cc.*, c.phone, c.name
                   FROM campaign_contacts cc
                   JOIN contacts c ON c.id = cc.contact_id
                   WHERE cc.campaign_id = ? AND cc.status = ?
                   ORDER BY cc.id""",
                (campaign_id, status)
            )
        else:
            cur.execute(
                """SELECT cc.*, c.phone, c.name
                   FROM campaign_contacts cc
                   JOIN contacts c ON c.id = cc.contact_id
                   WHERE cc.campaign_id = ?
                   ORDER BY cc.id""",
                (campaign_id,)
            )
        return [dict(r) for r in cur.fetchall()]


def update_campaign_contact_status(cc_id: int, status: str,
                                   error_message: str = None, sent_at: str = None):
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE campaign_contacts
               SET status = ?, error_message = ?, sent_at = ?, attempts = attempts + 1
               WHERE id = ?""",
            (status, error_message, sent_at or now_iso() if status == "sent" else None, cc_id)
        )


def get_campaign_stats(campaign_id: int) -> Dict[str, int]:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT status, COUNT(*) as cnt
               FROM campaign_contacts WHERE campaign_id = ?
               GROUP BY status""",
            (campaign_id,)
        )
        stats = {"pending": 0, "sent": 0, "failed": 0, "skipped": 0}
        for row in cur.fetchall():
            stats[row["status"]] = row["cnt"]
        stats["total"] = sum(stats.values())
        return stats


# ──────────────────── Logs ────────────────────

def add_send_log(campaign_id: int, contact_id: int, phone: str,
                 status: str, message: str = None):
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO send_logs (campaign_id, contact_id, phone, status, message, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (campaign_id, contact_id, phone, status, message, now_iso())
        )


def get_recent_logs(limit: int = 200) -> List[Dict]:
    with db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM send_logs ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in cur.fetchall()]
