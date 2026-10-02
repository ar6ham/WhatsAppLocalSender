"""تست ساده نرمال‌سازی شماره - بدون نیاز به GUI"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.utils.phone_normalizer import normalize_phone, clean_raw_number


def test_iran_numbers():
    cases = [
        ("09121234567", "+989121234567"),
        ("9121234567", "+989121234567"),
        ("+989121234567", "+989121234567"),
        ("00989121234567", "+989121234567"),
        ("98 912 123 4567", "+989121234567"),
    ]
    for raw, expected in cases:
        normalized, region, ok = normalize_phone(raw, "IR")
        assert ok, f"Failed for {raw}"
        assert normalized == expected, f"{raw} -> {normalized} != {expected}"
        print(f"OK: {raw} -> {normalized}")


def test_invalid():
    for raw in ["", "123", "abc", None]:
        _, _, ok = normalize_phone(str(raw) if raw else "")
        assert not ok, f"Should fail for {raw}"
        print(f"OK (invalid): {raw}")


if __name__ == "__main__":
    test_iran_numbers()
    test_invalid()
    print("\nهمه تست‌ها پاس شدند.")
