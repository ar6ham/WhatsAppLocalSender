"""
نرمال‌سازی شماره تلفن - کاملاً محلی با کتابخانه phonenumbers
"""
from typing import Optional, Tuple
import re

try:
    import phonenumbers
    from phonenumbers import NumberParseException, PhoneNumberFormat
except ImportError:
    phonenumbers = None

from app.config import DEFAULT_COUNTRY, DEFAULT_COUNTRY_CODE
from app.utils.logger import logger


def clean_raw_number(raw: str) -> str:
    """حذف کاراکترهای غیرعددی به جز +"""
    if not raw:
        return ""
    raw = str(raw).strip()
    # حفظ + در ابتدا
    if raw.startswith("+"):
        return "+" + re.sub(r"[^\d]", "", raw[1:])
    return re.sub(r"[^\d]", "", raw)


def normalize_phone(
    raw: str,
    default_region: str = DEFAULT_COUNTRY
) -> Tuple[Optional[str], Optional[str], bool]:
    """
    نرمال‌سازی شماره به فرمت E.164
    برمی‌گرداند: (شماره نرمال‌شده, منطقه, موفقیت)
    """
    if not raw or not str(raw).strip():
        return None, None, False

    cleaned = clean_raw_number(raw)
    if not cleaned or cleaned == "+":
        return None, None, False

    if phonenumbers is None:
        # fallback ساده بدون کتابخانه
        if cleaned.startswith("0") and len(cleaned) == 11:
            # فرض ایران
            normalized = f"+{DEFAULT_COUNTRY_CODE}{cleaned[1:]}"
            return normalized, DEFAULT_COUNTRY, True
        if cleaned.startswith(DEFAULT_COUNTRY_CODE) and len(cleaned) >= 12:
            return f"+{cleaned}", DEFAULT_COUNTRY, True
        if cleaned.startswith("+"):
            return cleaned, None, True
        return f"+{cleaned}", None, True

    try:
        # اگر با 0 شروع شود و منطقه پیش‌فرض داده شده
        if cleaned.startswith("0") and not cleaned.startswith("+"):
            number = phonenumbers.parse(cleaned, default_region)
        else:
            if not cleaned.startswith("+"):
                # اگر کد کشور نداشته باشد
                number = phonenumbers.parse(cleaned, default_region)
            else:
                number = phonenumbers.parse(cleaned, None)

        if not phonenumbers.is_possible_number(number):
            logger.debug(f"شماره ممکن نیست: {raw}")
            return None, None, False

        if not phonenumbers.is_valid_number(number):
            # بعضی شماره‌ها ممکن است معتبر نباشند ولی قابل استفاده باشند
            logger.debug(f"شماره معتبر نیست (ولی ممکن است کار کند): {raw}")

        e164 = phonenumbers.format_number(number, PhoneNumberFormat.E164)
        region = phonenumbers.region_code_for_number(number)
        return e164, region, True

    except NumberParseException as e:
        logger.debug(f"خطا در پارس شماره {raw}: {e}")
        return None, None, False
    except Exception as e:
        logger.debug(f"خطای غیرمنتظره در نرمال‌سازی {raw}: {e}")
        return None, None, False


def is_valid_phone(raw: str, default_region: str = DEFAULT_COUNTRY) -> bool:
    _, _, ok = normalize_phone(raw, default_region)
    return ok
