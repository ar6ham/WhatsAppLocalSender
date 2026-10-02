"""
نقطه ورود اصلی برنامه - WhatsApp Local Sender
۱۰۰٪ محلی روی ویندوز
"""
import sys
from pathlib import Path

# اطمینان از وجود مسیر app در sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.config import APP_NAME, APP_VERSION
from app.database.db import init_database
from app.gui.main_window import MainWindow
from app.utils.logger import logger


def main():
    logger.info(f"شروع {APP_NAME} v{APP_VERSION}")
    init_database()

    # High DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("LocalDesktop")

    # فونت مناسب فارسی
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # راست‌چین پیش‌فرض برای فارسی
    app.setLayoutDirection(Qt.RightToLeft)

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    logger.info("برنامه بسته شد.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
