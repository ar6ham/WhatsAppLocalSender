"""
اجرای کمپین به صورت محلی با صف و تأخیر تصادفی
"""
import time
import random
from typing import Optional, Callable
from datetime import datetime

from app.database import models
from app.database.db import now_iso
from app.whatsapp.controller import WhatsAppController, run_async
from app.utils.logger import logger


class CampaignRunner:
    def __init__(self):
        self.controller = WhatsAppController()
        self._stop_flag = False
        self._running = False
        self._on_progress: Optional[Callable] = None
        self._on_status: Optional[Callable] = None

    def set_callbacks(self, on_progress=None, on_status=None):
        self._on_progress = on_progress
        self._on_status = on_status
        self.controller.set_status_callback(on_status)

    def stop(self):
        self._stop_flag = True

    @property
    def is_running(self) -> bool:
        return self._running

    def start_browser(self) -> bool:
        return run_async(self.controller.start())

    def close_browser(self):
        run_async(self.controller.close())

    def run_campaign(self, campaign_id: int) -> dict:
        """اجرای کامل یک کمپین - مسدودکننده (در Thread جداگانه فراخوانی شود)"""
        self._stop_flag = False
        self._running = True
        campaign = models.get_campaign(campaign_id)
        if not campaign:
            self._running = False
            return {"error": "کمپین یافت نشد"}

        if not self.controller.is_ready:
            ok = self.start_browser()
            if not ok:
                self._running = False
                return {"error": "مرورگر آماده نشد. QR را اسکن کنید."}

        models.update_campaign_status(campaign_id, "running", started_at=now_iso())
        pending = models.get_campaign_contacts(campaign_id, status="pending")
        total = len(pending)
        sent = failed = 0

        delay_min = campaign.get("delay_min") or 3.0
        delay_max = campaign.get("delay_max") or 8.0
        message = campaign.get("message") or ""
        attachment = campaign.get("attachment_path")

        self._notify(f"شروع کمپین «{campaign['name']}» با {total} مخاطب")

        for i, cc in enumerate(pending):
            if self._stop_flag:
                self._notify("توقف توسط کاربر")
                break

            phone = cc["phone"]
            cc_id = cc["id"]
            contact_id = cc["contact_id"]

            self._notify(f"[{i+1}/{total}] ارسال به {phone} ...")

            success, err = run_async(
                self.controller.send_message(phone, message, attachment)
            )

            if success:
                models.update_campaign_contact_status(cc_id, "sent", sent_at=now_iso())
                models.add_send_log(campaign_id, contact_id, phone, "sent", message[:100])
                sent += 1
            else:
                models.update_campaign_contact_status(cc_id, "failed", error_message=err)
                models.add_send_log(campaign_id, contact_id, phone, "failed", err)
                failed += 1
                self._notify(f"خطا: {err}")

            if self._on_progress:
                try:
                    self._on_progress(i + 1, total, sent, failed)
                except Exception:
                    pass

            # تأخیر تصادفی (به جز آخرین)
            if i < total - 1 and not self._stop_flag:
                delay = random.uniform(delay_min, delay_max)
                self._notify(f"تأخیر {delay:.1f} ثانیه...")
                time.sleep(delay)

        final_status = "completed" if not self._stop_flag else "stopped"
        models.update_campaign_status(
            campaign_id, final_status, finished_at=now_iso()
        )
        self._running = False
        result = {"sent": sent, "failed": failed, "total": total, "status": final_status}
        self._notify(f"پایان کمپین: {result}")
        return result

    def _notify(self, msg: str):
        logger.info(msg)
        if self._on_status:
            try:
                self._on_status(msg)
            except Exception:
                pass
