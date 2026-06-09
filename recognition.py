"""
Module 2 — Real-time Face Recognition
Opens webcam, detects faces, identifies registered users.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cv2
import numpy as np
import face_recognition
from datetime import datetime

from config.settings import RECOGNITION_THRESHOLD, CAMERA_INDEX
from database.models import load_all_encodings
from app.attendance import process_attendance
from app.security import handle_unknown_detection


# Colours (BGR)
GREEN  = (0, 220, 100)
RED    = (0, 60, 220)
YELLOW = (0, 200, 220)
WHITE  = (255, 255, 255)
DARK   = (20, 20, 20)


def _draw_box(frame, loc, label, color):
    top, right, bottom, left = loc
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.rectangle(frame, (left, bottom - 26), (right, bottom), color, cv2.FILLED)
    cv2.putText(frame, label, (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, DARK, 1)


def _overlay_stats(frame, total, present, unknown):
    cv2.rectangle(frame, (0, 0), (260, 60), DARK, cv2.FILLED)
    cv2.putText(frame, f"Registered: {total}  Present: {present}  Alerts: {unknown}",
                (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, WHITE, 1)
    cv2.putText(frame, datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
                (8, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)


def run_recognition():
    """
    Main recognition loop.
    Loads all stored encodings, opens webcam, processes every frame.
    Press Q to quit.
    """
    print("🔄 Loading face encodings from database…")
    user_ids, known_encodings = load_all_encodings()

    if not known_encodings:
        print("⚠️  No registered users found. Register users first.")
        return

    print(f"✅ Loaded {len(known_encodings)} encodings. Starting camera…\n"
          f"   Press Q to quit.\n")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Cannot open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Throttle: track recently-processed faces to avoid hammering DB/alerts
    last_processed: dict[int | str, float] = {}
    COOLDOWN = 10  # seconds between re-processing same face

    unknown_count = 0
    present_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame read failed.")
            break

        # Downsample for faster detection
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb_small, model="hog")
        encodings = face_recognition.face_encodings(rgb_small, locations)

        now = datetime.now().timestamp()

        for enc, loc in zip(encodings, locations):
            # Scale location back to full frame
            top, right, bottom, left = [c * 4 for c in loc]
            full_loc = (top, right, bottom, left)

            distances = face_recognition.face_distance(known_encodings, enc)
            best_idx  = int(np.argmin(distances))
            best_dist = float(distances[best_idx])

            if best_dist < RECOGNITION_THRESHOLD:
                uid        = user_ids[best_idx]
                confidence = round(1 - best_dist, 3)

                # Cooldown check
                if now - last_processed.get(uid, 0) > COOLDOWN:
                    result = process_attendance(uid, confidence)
                    print(result["message"])
                    last_processed[uid] = now
                    if result.get("recorded"):
                        present_count += 1

                name = result["name"] if "result" in dir() else f"User {uid}"
                label = f"{name}  {confidence:.0%}"
                _draw_box(frame, full_loc, label, GREEN)

            else:
                key = "unknown"
                if now - last_processed.get(key, 0) > COOLDOWN:
                    handle_unknown_detection(frame.copy())
                    last_processed[key] = now
                    unknown_count += 1

                _draw_box(frame, full_loc, "Unknown — Alert Sent", RED)

        _overlay_stats(frame, len(known_encodings), present_count, unknown_count)
        cv2.imshow("Smart Attendance System  —  press Q to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n📋 Session summary — Present: {present_count}  Security alerts: {unknown_count}")


if __name__ == "__main__":
    run_recognition()
