"""
لاگر محلی - هیچ داده‌ای به اینترنت ارسال نمی‌شود.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.config import LOG_FILE, DEBUG_LOG_FILE, DEBUG, LOGS_DIR


def setup_logger(name: str = "WhatsAppLocalSender") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # فایل اصلی
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # فایل Debug محلی
    if DEBUG:
        debug_handler = RotatingFileHandler(
            DEBUG_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)

    # کنسول
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


logger = setup_logger()
