"""
Module 4 — Security Monitoring
Handles unknown face detection, screenshot saving, and DB logging.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cv2
from datetime import datetime
from config.settings import SECURITY_DIR
from database.models import log_security_event


def handle_unknown_detection(frame) -> dict:
    """
    Called when an unrecognised face is detected.
    Saves screenshot, logs to DB, triggers alerts.
    Returns log info dict.
    """
    ts = datetime.now()
    filename = f"unknown_{ts.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    image_path = str(SECURITY_DIR / filename)

    cv2.imwrite(image_path, frame)
    log_id = log_security_event(image_path)

    print(f"⚠️  Unknown person detected — saved to {image_path}")

    # Import here to avoid circular dependency at module load time
    from app.alerts import send_all_alerts
    send_all_alerts(image_path, ts, log_id)

    return {
        "log_id": log_id,
        "image_path": image_path,
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
    }
