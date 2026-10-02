"""
کنترلر WhatsApp Web با Playwright - کاملاً محلی
Session و Profile روی دیسک کاربر ذخیره می‌شود.
هیچ داده‌ای به سرور واسط ارسال نمی‌شود.
"""
import asyncio
import time
import random
from pathlib import Path
from typing import Optional, Callable

from app.config import (
    BROWSER_PROFILE_DIR, HEADLESS, BROWSER_TIMEOUT,
    PAGE_LOAD_TIMEOUT, ATTACHMENTS_DIR
)
from app.utils.logger import logger

# Playwright به صورت lazy import می‌شود تا بدون اینترنت هم GUI باز شود


class WhatsAppController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_ready = False
        self._on_status: Optional[Callable] = None

    def set_status_callback(self, callback: Callable):
        self._on_status = callback

    def _status(self, msg: str):
        logger.info(msg)
        if self._on_status:
            try:
                self._on_status(msg)
            except Exception:
                pass

    async def start(self) -> bool:
        """راه‌اندازی مرورگر محلی با Profile اختصاصی"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            self._status("Playwright نصب نیست. ابتدا install.bat را اجرا کنید.")
            return False

        try:
            self._status("در حال راه‌اندازی مرورگر محلی...")
            self.playwright = await async_playwright().start()

            BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=HEADLESS,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="Asia/Tehran",
            )

            # صفحه موجود یا جدید
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()

            self.page.set_default_timeout(BROWSER_TIMEOUT)
            self.page.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT)

            self._status("در حال باز کردن WhatsApp Web...")
            await self.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

            # منتظر لاگین یا QR
            ready = await self._wait_for_login(timeout=120)
            if ready:
                self.is_ready = True
                self._status("WhatsApp Web آماده است (Session محلی).")
            else:
                self._status("Login انجام نشد یا زمان تمام شد. QR را اسکن کنید.")
            return ready

        except Exception as e:
            self._status(f"خطا در راه‌اندازی مرورگر: {e}")
            logger.exception(e)
            return False

    async def _wait_for_login(self, timeout: int = 120) -> bool:
        """منتظر می‌ماند تا کاربر لاگین کند یا Session قبلی معتبر باشد"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                selectors = [
                    'div[data-testid="chat-list"]',
                    'div[aria-label="Chat list"]',
                    '#side',
                    'div[data-testid="default-user"]',
                    'canvas[aria-label="Scan this QR code"]',
                ]
                for sel in selectors:
                    el = await self.page.query_selector(sel)
                    if el:
                        if "QR" in (await el.get_attribute("aria-label") or ""):
                            self._status("لطفاً QR Code را با گوشی اسکن کنید...")
                            break
                        chat = await self.page.query_selector('div[data-testid="chat-list"], #side')
                        if chat:
                            return True
            except Exception:
                pass
            await asyncio.sleep(2)

        try:
            chat = await self.page.query_selector('div[data-testid="chat-list"], #side')
            return chat is not None
        except Exception:
            return False

    async def send_message(self, phone: str, message: str,
                           attachment_path: Optional[str] = None) -> tuple[bool, str]:
        """
        ارسال پیام به شماره مشخص.
        phone باید به فرمت E.164 باشد (مثلاً +98912...)
        """
        if not self.page or not self.is_ready:
            return False, "مرورگر آماده نیست"

        try:
            number = phone.lstrip("+")
            url = f"https://web.whatsapp.com/send?phone={number}"

            self._status(f"باز کردن چت برای {phone}...")
            await self.page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            input_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][title="Type a message"]',
                'footer div[contenteditable="true"]',
                'div[data-testid="conversation-compose-box-input"]',
            ]

            input_box = None
            for _ in range(15):
                for sel in input_selectors:
                    input_box = await self.page.query_selector(sel)
                    if input_box:
                        break
                if input_box:
                    break
                invalid = await self.page.query_selector('div[data-testid="popup-contents"]')
                if invalid:
                    text = await invalid.inner_text()
                    if "invalid" in text.lower() or "phone" in text.lower():
                        return False, "شماره نامعتبر یا در واتساپ نیست"
                await asyncio.sleep(1)

            if not input_box:
                return False, "باکس پیام پیدا نشد (شاید شماره نامعتبر است)"

            if attachment_path and Path(attachment_path).exists():
                ok, err = await self._send_attachment(attachment_path)
                if not ok:
                    return False, err
                await asyncio.sleep(1)

            if message and message.strip():
                await input_box.click()
                await asyncio.sleep(0.3)
                await self.page.keyboard.type(message, delay=20)
                await asyncio.sleep(0.5)

            send_selectors = [
                'button[data-testid="compose-btn-send"]',
                'button[aria-label="Send"]',
                'span[data-icon="send"]',
            ]
            sent = False
            for sel in send_selectors:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    sent = True
                    break

            if not sent:
                await self.page.keyboard.press("Enter")

            await asyncio.sleep(1.5)
            self._status(f"پیام به {phone} ارسال شد.")
            return True, "ارسال موفق"

        except Exception as e:
            logger.exception(e)
            return False, str(e)

    async def _send_attachment(self, file_path: str) -> tuple[bool, str]:
        try:
            attach_btn = await self.page.query_selector('div[title="Attach"], span[data-icon="attach-menu-plus"], button[aria-label="Attach"]')
            if attach_btn:
                await attach_btn.click()
                await asyncio.sleep(0.5)

            file_input = await self.page.query_selector('input[type="file"]')
            if not file_input:
                return False, "ورودی فایل پیدا نشد"

            await file_input.set_input_files(file_path)
            await asyncio.sleep(2)

            send_btn = await self.page.query_selector(
                'div[data-testid="media-send"], span[data-icon="send"], button[aria-label="Send"]'
            )
            if send_btn:
                await send_btn.click()
                await asyncio.sleep(1.5)
            return True, "فایل ارسال شد"
        except Exception as e:
            return False, f"خطا در ارسال فایل: {e}"

    async def close(self):
        self.is_ready = False
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.debug(f"خطا در بستن مرورگر: {e}")
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self._status("مرورگر بسته شد.")


def run_async(coro):
    """اجرای coroutine در event loop جدید (مناسب برای Thread)"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
