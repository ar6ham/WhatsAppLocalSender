"""
Backup و Restore محلی - ZIP روی دیسک کاربر
"""
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.config import (
    DATA_DIR, DATABASE_PATH, BROWSER_PROFILE_DIR,
    ATTACHMENTS_DIR, EXPORTS_DIR, LOGS_DIR, BACKUPS_DIR
)
from app.utils.logger import logger


def create_backup(include_browser_profile: bool = False) -> Optional[str]:
    """
    ایجاد فایل ZIP محلی از دیتابیس و داده‌های مهم.
    Session مرورگر به صورت پیش‌فرض در بکاپ نیست (حجم و امنیت).
    """
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.zip"
    backup_path = BACKUPS_DIR / backup_name

    try:
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # دیتابیس
            if DATABASE_PATH.exists():
                zf.write(DATABASE_PATH, "database.sqlite")

            # attachments
            if ATTACHMENTS_DIR.exists():
                for f in ATTACHMENTS_DIR.rglob("*"):
                    if f.is_file():
                        zf.write(f, f"attachments/{f.relative_to(ATTACHMENTS_DIR)}")

            # exports (اختیاری)
            if EXPORTS_DIR.exists():
                for f in EXPORTS_DIR.rglob("*"):
                    if f.is_file():
                        zf.write(f, f"exports/{f.relative_to(EXPORTS_DIR)}")

            # browser profile فقط اگر کاربر صریحاً خواسته
            if include_browser_profile and BROWSER_PROFILE_DIR.exists():
                for f in BROWSER_PROFILE_DIR.rglob("*"):
                    if f.is_file():
                        zf.write(f, f"browser_profile/{f.relative_to(BROWSER_PROFILE_DIR)}")

        logger.info(f"بکاپ محلی ایجاد شد: {backup_path}")
        return str(backup_path)
    except Exception as e:
        logger.error(f"خطا در ایجاد بکاپ: {e}")
        return None


def restore_backup(zip_path: str, restore_browser_profile: bool = False) -> bool:
    """بازیابی از فایل ZIP محلی"""
    path = Path(zip_path)
    if not path.exists() or not path.suffix.lower() == ".zip":
        logger.error("فایل بکاپ نامعتبر است")
        return False

    try:
        with zipfile.ZipFile(path, "r") as zf:
            # دیتابیس
            if "database.sqlite" in zf.namelist():
                # پشتیبان از دیتابیس فعلی
                if DATABASE_PATH.exists():
                    shutil.copy2(DATABASE_PATH, DATABASE_PATH.with_suffix(".sqlite.bak"))
                zf.extract("database.sqlite", DATA_DIR)

            # attachments
            for name in zf.namelist():
                if name.startswith("attachments/") and not name.endswith("/"):
                    target = ATTACHMENTS_DIR / name[len("attachments/"):]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(name) as src, open(target, "wb") as dst:
                        dst.write(src.read())

            if restore_browser_profile:
                for name in zf.namelist():
                    if name.startswith("browser_profile/") and not name.endswith("/"):
                        target = BROWSER_PROFILE_DIR / name[len("browser_profile/"):]
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(name) as src, open(target, "wb") as dst:
                            dst.write(src.read())

        logger.info(f"بازیابی از {zip_path} انجام شد")
        return True
    except Exception as e:
        logger.error(f"خطا در بازیابی: {e}")
        return False


def list_backups() -> list:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(BACKUPS_DIR.glob("backup_*.zip"), reverse=True)
    return [{"name": f.name, "path": str(f), "size": f.stat().st_size} for f in files]
