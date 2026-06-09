"""
Module 1 — User Registration
Captures face images, generates embeddings, saves to DB.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cv2
import numpy as np
import face_recognition
from datetime import datetime

from config.settings import CAPTURES_DIR, CAPTURE_SAMPLES
from database.models import create_user


def _draw_progress(frame, count, total):
    h, w = frame.shape[:2]
    pct = count / total
    bar_w = int(w * 0.6)
    x0 = (w - bar_w) // 2
    y0 = h - 50
    cv2.rectangle(frame, (x0, y0), (x0 + bar_w, y0 + 20), (60, 60, 60), -1)
    cv2.rectangle(frame, (x0, y0), (x0 + int(bar_w * pct), y0 + 20), (0, 220, 100), -1)
    cv2.putText(frame, f"Captured {count}/{total}", (x0, y0 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)


def capture_face_encodings(full_name: str) -> list | None:
    """
    Open webcam, collect CAPTURE_SAMPLES face encodings.
    Returns averaged encoding as a Python list, or None on failure.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return None

    encodings = []
    save_dir = CAPTURES_DIR / full_name.replace(" ", "_")
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"📷 Look at the camera. Capturing {CAPTURE_SAMPLES} samples for {full_name}…")

    while len(encodings) < CAPTURE_SAMPLES:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model="hog")
        found = face_recognition.face_encodings(rgb, locations)

        if found:
            encodings.append(found[0])
            ts = datetime.now().strftime("%H%M%S_%f")
            cv2.imwrite(str(save_dir / f"sample_{ts}.jpg"), frame)

        _draw_progress(frame, len(encodings), CAPTURE_SAMPLES)
        cv2.putText(frame, f"Registering: {full_name}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 100), 2)

        for (top, right, bottom, left) in locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 220, 100), 2)

        cv2.imshow("Registration — press Q to cancel", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Registration cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return None

    cap.release()
    cv2.destroyAllWindows()

    avg = np.mean(encodings, axis=0).tolist()
    print(f"✅ Face captured — {len(encodings)} samples averaged.")
    return avg


def register_user(full_name, employee_id, email, department, phone):
    """
    Full registration pipeline:
    1. Capture face via webcam
    2. Generate average embedding
    3. Save to database
    """
    print(f"\n── Registering: {full_name} ({employee_id}) ──")

    encoding = capture_face_encodings(full_name)
    if encoding is None:
        print("❌ Registration failed — no face encoding captured.")
        return False

    try:
        uid = create_user(full_name, employee_id, email, department, phone, encoding)
        print(f"✅ User registered successfully. DB ID: {uid}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def register_via_cli():
    """Interactive CLI registration form."""
    print("\n╔══════════════════════════════════╗")
    print("║   Smart Attendance — Register    ║")
    print("╚══════════════════════════════════╝\n")
    full_name   = input("Full name      : ").strip()
    employee_id = input("Employee ID    : ").strip()
    email       = input("Email          : ").strip()
    department  = input("Department     : ").strip()
    phone       = input("Phone          : ").strip()
    register_user(full_name, employee_id, email, department, phone)


if __name__ == "__main__":
    register_via_cli()
