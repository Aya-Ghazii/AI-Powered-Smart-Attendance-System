"""
Module 3 — Attendance Logic
Handles status classification and duplicate prevention.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, time
from config.settings import LATE_CUTOFF_HOUR, LATE_CUTOFF_MINUTE
from database.models import record_attendance, already_recorded_today, get_user_by_id

LATE_CUTOFF = time(LATE_CUTOFF_HOUR, LATE_CUTOFF_MINUTE)


def classify_status() -> str:
    """Return 'Present' or 'Late' based on current time."""
    return "Late" if datetime.now().time() > LATE_CUTOFF else "Present"


def process_attendance(user_id: int, confidence: float = None) -> dict:
    """
    Attempt to record attendance for user_id.
    Returns a result dict with status and message.
    """
    if already_recorded_today(user_id):
        user = get_user_by_id(user_id)
        name = user["full_name"] if user else f"User {user_id}"
        return {
            "recorded": False,
            "reason": "duplicate",
            "message": f"Already recorded today — {name}",
            "name": name,
        }

    status = classify_status()
    record_attendance(user_id, status, confidence)
    user = get_user_by_id(user_id)
    name = user["full_name"] if user else f"User {user_id}"

    return {
        "recorded": True,
        "status": status,
        "name": name,
        "message": f"✅ {status} — Welcome, {name}!",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
