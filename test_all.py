"""
Test suite for Smart Attendance System.
Run: python -m pytest tests/test_all.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, time, date
import numpy as np


class TestAttendanceLogic(unittest.TestCase):

    def test_classify_present(self):
        """Employee arriving before cutoff is classified as Present."""
        from app.attendance import classify_status
        with patch("app.attendance.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 8, 30)
            self.assertEqual(classify_status(), "Present")

    def test_classify_late(self):
        """Employee arriving after cutoff is classified as Late."""
        from app.attendance import classify_status
        with patch("app.attendance.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 9, 30)
            self.assertEqual(classify_status(), "Late")

    def test_duplicate_prevention(self):
        """Second attendance record for same user/day should not be written."""
        from database.models import already_recorded_today
        with patch("database.models.execute_query", return_value=[{"1": 1}]):
            self.assertTrue(already_recorded_today(1))

    def test_no_duplicate_new_day(self):
        """New day means no duplicate."""
        from database.models import already_recorded_today
        with patch("database.models.execute_query", return_value=[]):
            self.assertFalse(already_recorded_today(1))


class TestAnalytics(unittest.TestCase):

    def _sample_df(self):
        import pandas as pd
        return pd.DataFrame([
            {"date": date.today(), "full_name": "Alice", "employee_id": "E01",
             "department": "IT", "check_in_time": "08:55:00", "status": "Present"},
            {"date": date.today(), "full_name": "Bob", "employee_id": "E02",
             "department": "HR", "check_in_time": "09:15:00", "status": "Late"},
        ])

    def test_insights_generated(self):
        from app.analytics import generate_insights
        kpis = {
            "attendance_rate_30d": 88.0, "rate_change_pct": 2.5,
            "late_today": 1, "top_department": "IT",
            "security_incidents_30d": 0,
        }
        insights = generate_insights(kpis)
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)

    def test_trend_shape(self):
        from app.analytics import attendance_trend
        df = self._sample_df()
        trend = attendance_trend(df)
        self.assertIn("status", trend.columns)
        self.assertIn("count", trend.columns)

    def test_department_summary(self):
        from app.analytics import department_summary
        df = self._sample_df()
        summary = department_summary(df)
        self.assertFalse(summary.empty)


class TestAlerts(unittest.TestCase):

    @patch("app.alerts.requests.post")
    def test_telegram_called(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        from app.alerts import send_telegram_alert
        import config.settings as s
        s.TELEGRAM_TOKEN   = "fake_token"
        s.TELEGRAM_CHAT_ID = "fake_chat"
        result = send_telegram_alert("/nonexistent.jpg", datetime.now())
        # requests.post should have been called
        mock_post.assert_called_once()


class TestEncodings(unittest.TestCase):

    def test_load_returns_lists(self):
        """load_all_encodings should return two equal-length lists."""
        import json
        fake_enc = json.dumps(list(np.zeros(128).tolist()))
        mock_rows = [
            {"user_id": 1, "face_encoding": fake_enc},
            {"user_id": 2, "face_encoding": fake_enc},
        ]
        with patch("database.models.execute_query", return_value=mock_rows):
            from database.models import load_all_encodings
            ids, encs = load_all_encodings()
            self.assertEqual(len(ids), len(encs))
            self.assertEqual(len(ids), 2)
            self.assertEqual(encs[0].shape, (128,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
