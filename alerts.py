"""
Module 5 — Alert Automation
Sends email and Telegram alerts when an unknown person is detected.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

from config.settings import (
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER,
    SMTP_HOST, SMTP_PORT,
    TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
)
from database.models import mark_alert_sent


# ── Email ─────────────────────────────────────────────────────

def send_email_alert(image_path: str, timestamp: datetime, log_id: int = None):
    """Send security alert email with attached screenshot."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("⚠️  Email not configured — skipping email alert.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER
        msg["Subject"] = f"⚠️ Security Alert — Unknown Person Detected"

        body = f"""
        <html><body>
        <h2 style="color:#c0392b;">⚠️ Unknown Person Detected</h2>
        <table style="font-family:Arial;font-size:14px;border-collapse:collapse;">
          <tr><td style="padding:6px;font-weight:bold;">Date:</td>
              <td style="padding:6px;">{timestamp.strftime('%A, %d %B %Y')}</td></tr>
          <tr><td style="padding:6px;font-weight:bold;">Time:</td>
              <td style="padding:6px;">{timestamp.strftime('%I:%M:%S %p')}</td></tr>
          <tr><td style="padding:6px;font-weight:bold;">Log ID:</td>
              <td style="padding:6px;">{log_id or 'N/A'}</td></tr>
        </table>
        <p>Screenshot is attached. Please review the security footage immediately.</p>
        </body></html>
        """
        msg.attach(MIMEText(body, "html"))

        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                img = MIMEImage(f.read(), name=os.path.basename(image_path))
                msg.attach(img)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print("✅ Email alert sent.")
        return True

    except Exception as e:
        print(f"❌ Email alert failed: {e}")
        return False


# ── Telegram ──────────────────────────────────────────────────

def send_telegram_alert(image_path: str, timestamp: datetime, log_id: int = None):
    """Send Telegram bot message with photo."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured — skipping Telegram alert.")
        return False

    try:
        caption = (
            f"⚠️ *Unknown Person Detected*\n\n"
            f"📅 Date: {timestamp.strftime('%d-%m-%Y')}\n"
            f"🕐 Time: {timestamp.strftime('%I:%M %p')}\n"
            f"🔑 Log ID: {log_id or 'N/A'}\n\n"
            f"_Please review immediately._"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "Markdown"}

        if os.path.exists(image_path):
            with open(image_path, "rb") as photo:
                response = requests.post(url, data=payload, files={"photo": photo}, timeout=10)
        else:
            url_msg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            response = requests.post(url_msg, data={**payload, "text": caption}, timeout=10)

        if response.status_code == 200:
            print("✅ Telegram alert sent.")
            return True
        else:
            print(f"❌ Telegram alert failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Telegram alert error: {e}")
        return False


# ── Combined ──────────────────────────────────────────────────

def send_all_alerts(image_path: str, timestamp: datetime, log_id: int = None):
    """Fire all configured alert channels."""
    email_ok    = send_email_alert(image_path, timestamp, log_id)
    telegram_ok = send_telegram_alert(image_path, timestamp, log_id)

    if (email_ok or telegram_ok) and log_id:
        mark_alert_sent(log_id)

    return email_ok, telegram_ok
