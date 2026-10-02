@echo off
chcp 65001 >nul
title نصب WhatsApp Local Sender
echo ========================================
echo   نصب وابستگی‌های محلی برنامه
echo ========================================
echo.

REM بررسی Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [خطا] Python پیدا نشد. لطفاً Python 3.10 یا بالاتر را نصب کنید.
    echo دانلود: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] در حال نصب پکیج‌های Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [خطا] نصب پکیج‌ها ناموفق بود.
    pause
    exit /b 1
)

echo.
echo [2/3] در حال نصب مرورگر Chromium برای Playwright...
python -m playwright install chromium
if errorlevel 1 (
    echo [هشدار] نصب Chromium ممکن است نیاز به اینترنت داشته باشد.
)

echo.
echo [3/3] ایجاد پوشه‌های داده...
if not exist "data" mkdir data
if not exist "data\browser_profile" mkdir data\browser_profile
if not exist "data\attachments" mkdir data\attachments
if not exist "data\exports" mkdir data\exports
if not exist "data\logs" mkdir data\logs
if not exist "data\backups" mkdir data\backups

echo.
echo ========================================
echo   نصب با موفقیت انجام شد!
echo   برای اجرا: run.bat را دوبار کلیک کنید
echo ========================================
pause
