"""
Query helpers — all DB access goes through these functions.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pandas as pd
from datetime import date, datetime
from database.db_config import execute_query


# ── Users ─────────────────────────────────────────────────────

def create_user(full_name, employee_id, email, department, phone, encoding_list):
    sql = """
        INSERT INTO users (full_name, employee_id, email, department, phone, face_encoding)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    enc_json = json.dumps(encoding_list)
    return execute_query(sql, (full_name, employee_id, email, department, phone, enc_json))


def get_all_users():
    return execute_query("SELECT * FROM users WHERE is_active = TRUE", fetch=True)


def get_user_by_id(user_id):
    rows = execute_query("SELECT * FROM users WHERE user_id = %s", (user_id,), fetch=True)
    return rows[0] if rows else None


def load_all_encodings():
    """Return (user_ids, numpy_encodings) for face_recognition comparison."""
    import numpy as np
    rows = execute_query(
        "SELECT user_id, face_encoding FROM users WHERE is_active = TRUE AND face_encoding IS NOT NULL",
        fetch=True,
    )
    ids, encodings = [], []
    for row in rows:
        enc = json.loads(row["face_encoding"])
        ids.append(row["user_id"])
        encodings.append(np.array(enc))
    return ids, encodings


def get_total_employees():
    rows = execute_query("SELECT COUNT(*) AS cnt FROM users WHERE is_active = TRUE", fetch=True)
    return rows[0]["cnt"] if rows else 0


# ── Attendance ────────────────────────────────────────────────

def record_attendance(user_id, status, confidence=None):
    today = date.today()
    now_time = datetime.now().time()
    # Ignore duplicates silently
    sql = """
        INSERT IGNORE INTO attendance (user_id, date, check_in_time, status, confidence)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(sql, (user_id, today, now_time, status, confidence))


def get_attendance_today():
    rows = execute_query(
        """SELECT a.*, u.full_name, u.employee_id, u.department
           FROM attendance a JOIN users u ON a.user_id = u.user_id
           WHERE a.date = CURDATE()""",
        fetch=True,
    )
    return rows


def get_attendance_df(days: int = 30):
    sql = """
        SELECT a.date, a.check_in_time, a.status, a.confidence,
               u.full_name, u.employee_id, u.department
        FROM attendance a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY a.date DESC, a.check_in_time DESC
    """
    rows = execute_query(sql, (days,), fetch=True)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def already_recorded_today(user_id):
    rows = execute_query(
        "SELECT 1 FROM attendance WHERE user_id = %s AND date = CURDATE()",
        (user_id,), fetch=True,
    )
    return bool(rows)


def count_present_today():
    rows = execute_query(
        "SELECT COUNT(*) AS cnt FROM attendance WHERE date = CURDATE() AND status IN ('Present','Late')",
        fetch=True,
    )
    return rows[0]["cnt"] if rows else 0


def count_late_today():
    rows = execute_query(
        "SELECT COUNT(*) AS cnt FROM attendance WHERE date = CURDATE() AND status = 'Late'",
        fetch=True,
    )
    return rows[0]["cnt"] if rows else 0


# ── Security logs ─────────────────────────────────────────────

def log_security_event(image_path, notes=""):
    sql = "INSERT INTO security_logs (image_path, notes) VALUES (%s, %s)"
    return execute_query(sql, (image_path, notes))


def mark_alert_sent(log_id):
    execute_query("UPDATE security_logs SET alert_sent = TRUE WHERE log_id = %s", (log_id,))


def get_security_logs_df(days: int = 30):
    sql = """
        SELECT * FROM security_logs
        WHERE detected_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        ORDER BY detected_at DESC
    """
    rows = execute_query(sql, (days,), fetch=True)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def count_security_incidents(days: int = 1):
    rows = execute_query(
        "SELECT COUNT(*) AS cnt FROM security_logs WHERE detected_at >= DATE_SUB(NOW(), INTERVAL %s DAY)",
        (days,), fetch=True,
    )
    return rows[0]["cnt"] if rows else 0
