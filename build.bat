@echo off
chcp 65001 >nul
title ساخت فایل اجرایی
echo ========================================
echo   ساخت فایل اجرایی با PyInstaller
echo ========================================
echo.

python -m pip install pyinstaller >nul 2>&1

echo در حال بسته‌بندی...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "WhatsAppLocalSender" ^
    --add-data "app;app" ^
    --hidden-import=PySide6 ^
    --hidden-import=playwright ^
    --hidden-import=phonenumbers ^
    --hidden-import=pandas ^
    --collect-all PySide6 ^
    app\main.py

echo.
if exist "dist\WhatsAppLocalSender\WhatsAppLocalSender.exe" (
    echo [موفق] فایل اجرایی در پوشه dist ساخته شد.
    echo توجه: پوشه data را کنار exe قرار دهید.
) else (
    echo [خطا] ساخت ناموفق بود.
)
pause
