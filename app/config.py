"""
پیکربندی مرکزی برنامه - کاملاً محلی
هیچ تنظیمات ابری یا سرور خارجی وجود ندارد.
"""
import os
import sys
from pathlib import Path

# مسیر ریشه برنامه
if getattr(sys, 'frozen', False):
    # وقتی با PyInstaller بسته‌بندی شده
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# پوشه داده محلی
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "database.sqlite"
BROWSER_PROFILE_DIR = DATA_DIR / "browser_profile"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = DATA_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"

# ایجاد پوشه‌ها در صورت نیاز
for d in [DATA_DIR, BROWSER_PROFILE_DIR, ATTACHMENTS_DIR, EXPORTS_DIR, LOGS_DIR, BACKUPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# حالت Debug محلی (فقط لاگ بیشتر روی دیسک)
DEBUG = True

# تنظیمات Playwright / مرورگر
# از Chromium محلی Playwright استفاده می‌شود
HEADLESS = False  # برای دیدن WhatsApp Web معمولاً False باشد
BROWSER_TIMEOUT = 60000  # میلی‌ثانیه
PAGE_LOAD_TIMEOUT = 30000

# تنظیمات ارسال
DEFAULT_DELAY_MIN = 3.0   # ثانیه حداقل تأخیر بین پیام‌ها
DEFAULT_DELAY_MAX = 8.0   # ثانیه حداکثر تأخیر
MAX_RETRIES = 2

# نرمال‌سازی شماره (پیش‌فرض ایران)
DEFAULT_COUNTRY = "IR"
DEFAULT_COUNTRY_CODE = "98"

# نسخه برنامه
APP_NAME = "WhatsApp Local Sender"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Local Desktop App"

# مسیر لاگ
LOG_FILE = LOGS_DIR / "app.log"
DEBUG_LOG_FILE = LOGS_DIR / "debug.log"
