# WhatsApp Local Sender

**برنامه دسکتاپ ۱۰۰٪ محلی برای ویندوز**

این نرم‌افزار تمام پردازش‌ها را روی کامپیوتر شما انجام می‌دهد. هیچ سرور، Cloud، VPS یا سرویس واسطی وجود ندارد.

---

## معماری

```
Windows PC
│
├── Python Application
│   ├── PySide6 GUI (فارسی)
│   ├── Campaign Manager
│   ├── Queue Manager
│   ├── Phone Normalizer
│   ├── SQLite محلی
│   └── Playwright
│
├── Local Chromium
│   └── WhatsApp Web
│
└── Local Storage
    ├── data/database.sqlite
    ├── data/browser_profile/   ← Session محلی
    ├── data/attachments/
    ├── data/exports/
    ├── data/logs/
    └── data/backups/
```

---

## ویژگی‌ها

- **کاملاً محلی**: دیتابیس SQLite، فایل‌ها، لاگ‌ها و Session مرورگر روی HDD/SSD شما
- **ایمپورت مخاطبین** از CSV و Excel
- **نرمال‌سازی شماره** با پشتیبانی از کد کشور ایران و بین‌المللی
- **حذف خودکار تکراری‌ها**
- **مدیریت کمپین** با متن + پیوست اختیاری
- **تأخیر تصادفی** بین پیام‌ها برای کاهش ریسک
- **Backup و Restore** محلی به صورت ZIP
- **بدون Telemetry** — هیچ داده‌ای از سیستم خارج نمی‌شود
- **حالت Debug محلی** (لاگ بیشتر روی دیسک)

---

## نصب (ویندوز)

1. **Python 3.10+** را از [python.org](https://www.python.org/downloads/) نصب کنید  
   (حتماً گزینه *Add Python to PATH* را فعال کنید)

2. این پوشه را در مسیر دلخواه کپی کنید.

3. روی **`install.bat`** دوبار کلیک کنید و صبر کنید تا وابستگی‌ها نصب شوند.

4. روی **`run.bat`** دوبار کلیک کنید تا برنامه باز شود.

---

## نحوه استفاده

1. تب **مخاطبین** → ایمپورت CSV/Excel یا افزودن دستی
2. تب **کمپین‌ها** → نام، متن پیام، پیوست (اختیاری) و تأخیر را تنظیم و کمپین بسازید
3. تب **ارسال**:
   - روی «باز کردن WhatsApp Web» کلیک کنید
   - در صورت نیاز QR Code را با گوشی اسکن کنید (فقط یک‌بار؛ Session ذخیره می‌شود)
   - کمپین را انتخاب و «شروع ارسال» را بزنید
4. تب **تنظیمات** → Backup / Restore محلی

---

## ساختار پوشه‌ها

```
WhatsAppLocalSender/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── gui/
│   ├── whatsapp/
│   ├── database/
│   ├── services/
│   └── utils/
├── data/                  ← تمام داده‌های شما اینجا است
│   ├── database.sqlite
│   ├── browser_profile/
│   ├── attachments/
│   ├── exports/
│   ├── logs/
│   └── backups/
├── requirements.txt
├── install.bat
├── run.bat
├── build.bat
└── README.md
```

---

## نکات مهم

- **اینترنت فقط برای WhatsApp Web** لازم است. بقیه قابلیت‌ها آفلاین کار می‌کنند.
- Session مرورگر در `data/browser_profile` ذخیره می‌شود و به هیچ سروری ارسال نمی‌شود.
- استفاده از اتوماسیون ممکن است با شرایط استفاده واتسپ مغایرت داشته باشد. مسئولیت استفاده بر عهده کاربر است.
- هیچ API Backend، Firebase، Supabase، MongoDB Cloud یا سرویس واسطی استفاده نشده است.

---

## ساخت فایل اجرایی (اختیاری)

```bat
build.bat
```

فایل اجرایی در پوشه `dist` ساخته می‌شود. پوشه `data` را کنار exe نگه دارید.

---

## مجوز و مسئولیت

این نرم‌افزار به صورت محلی و برای استفاده شخصی طراحی شده است.  
توسعه‌دهنده هیچ مسئولیتی در قبال مسدود شدن اکانت یا نقض قوانین واتسپ ندارد.
