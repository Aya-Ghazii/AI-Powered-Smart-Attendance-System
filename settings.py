"""
App-wide configuration loaded from .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "config" / ".env"
load_dotenv(ENV_PATH)

# ── Database ────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "smart_attendance"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# ── Email ────────────────────────────────────────────────────
EMAIL_SENDER   = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
SMTP_HOST      = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", 587))

# ── Telegram ─────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Recognition ──────────────────────────────────────────────
RECOGNITION_THRESHOLD = float(os.getenv("RECOGNITION_THRESHOLD", 0.5))
CAMERA_INDEX          = int(os.getenv("CAMERA_INDEX", 0))
CAPTURE_SAMPLES       = int(os.getenv("CAPTURE_SAMPLES", 10))

# ── Attendance rules ─────────────────────────────────────────
LATE_CUTOFF_HOUR   = int(os.getenv("LATE_CUTOFF_HOUR", 9))
LATE_CUTOFF_MINUTE = int(os.getenv("LATE_CUTOFF_MINUTE", 0))

# ── Paths ─────────────────────────────────────────────────────
FACE_DATA_DIR      = BASE_DIR / "face_data"
CAPTURES_DIR       = FACE_DATA_DIR / "captures"
ENCODINGS_DIR      = FACE_DATA_DIR / "encodings"
SECURITY_DIR       = BASE_DIR / "security_captures"
REPORTS_DIR        = BASE_DIR / "reports" / "output"

for d in [CAPTURES_DIR, ENCODINGS_DIR, SECURITY_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
