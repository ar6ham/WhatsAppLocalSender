"""
سرویس ایمپورت مخاطبین از فایل‌های محلی (CSV / Excel)
"""
from pathlib import Path
from typing import List, Dict, Tuple
import csv

from app.utils.phone_normalizer import normalize_phone
from app.database import models
from app.utils.logger import logger


def import_from_csv(file_path: str, phone_col: str = "phone",
                    name_col: str = "name") -> Dict:
    path = Path(file_path)
    if not path.exists():
        return {"error": "فایل یافت نشد", "added": 0, "skipped": 0, "failed": 0}

    contacts = []
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw = row.get(phone_col) or row.get("Phone") or row.get("شماره") or ""
                name = row.get(name_col) or row.get("Name") or row.get("نام") or ""
                normalized, region, ok = normalize_phone(raw)
                if ok and normalized:
                    contacts.append({
                        "phone": normalized,
                        "name": name.strip() if name else None,
                        "region": region
                    })
    except Exception as e:
        logger.error(f"خطا در خواندن CSV: {e}")
        return {"error": str(e), "added": 0, "skipped": 0, "failed": 0}

    result = models.bulk_add_contacts(contacts)
    result["total_parsed"] = len(contacts)
    return result


def import_from_excel(file_path: str, phone_col: str = "phone",
                      name_col: str = "name") -> Dict:
    try:
        import pandas as pd
    except ImportError:
        return {"error": "pandas نصب نیست", "added": 0, "skipped": 0, "failed": 0}

    path = Path(file_path)
    if not path.exists():
        return {"error": "فایل یافت نشد", "added": 0, "skipped": 0, "failed": 0}

    try:
        df = pd.read_excel(path)
        # پیدا کردن ستون‌های ممکن
        cols = {c.lower(): c for c in df.columns}
        p_col = cols.get(phone_col.lower()) or cols.get("phone") or cols.get("شماره") or list(df.columns)[0]
        n_col = cols.get(name_col.lower()) or cols.get("name") or cols.get("نام")

        contacts = []
        for _, row in df.iterrows():
            raw = str(row.get(p_col, "")).strip()
            name = str(row.get(n_col, "")).strip() if n_col else ""
            if name.lower() in ("nan", "none"):
                name = ""
            normalized, region, ok = normalize_phone(raw)
            if ok and normalized:
                contacts.append({
                    "phone": normalized,
                    "name": name or None,
                    "region": region
                })

        result = models.bulk_add_contacts(contacts)
        result["total_parsed"] = len(contacts)
        return result
    except Exception as e:
        logger.error(f"خطا در خواندن Excel: {e}")
        return {"error": str(e), "added": 0, "skipped": 0, "failed": 0}


def import_from_text(text: str) -> Dict:
    """ایمپورت از متن ساده (هر خط یک شماره)"""
    contacts = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # اگر با , یا | جدا شده
        parts = [p.strip() for p in line.replace("|", ",").split(",")]
        raw = parts[0]
        name = parts[1] if len(parts) > 1 else None
        normalized, region, ok = normalize_phone(raw)
        if ok and normalized:
            contacts.append({"phone": normalized, "name": name, "region": region})

    result = models.bulk_add_contacts(contacts)
    result["total_parsed"] = len(contacts)
    return result
