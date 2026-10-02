@echo off
chcp 65001 >nul
title WhatsApp Local Sender
cd /d "%~dp0"

echo در حال اجرای برنامه محلی...
python -m app.main
if errorlevel 1 (
    echo.
    echo [خطا] برنامه با خطا بسته شد.
    echo مطمئن شوید که install.bat را قبلاً اجرا کرده‌اید.
    pause
)
