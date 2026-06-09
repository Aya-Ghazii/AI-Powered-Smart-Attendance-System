"""
Module 8 — AI Analytics
Generates statistical insights and natural-language summaries.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from datetime import date, timedelta
from database.models import get_attendance_df, get_security_logs_df, get_total_employees


def get_attendance_rate(df: pd.DataFrame, status_filter=("Present", "Late")) -> float:
    if df.empty:
        return 0.0
    present = df[df["status"].isin(status_filter)]
    total_employee_days = get_total_employees() * df["date"].nunique()
    return round(len(present) / total_employee_days * 100, 1) if total_employee_days else 0.0


def compute_kpis() -> dict:
    """Return a dict of all dashboard KPIs."""
    df_30  = get_attendance_df(days=30)
    df_60  = get_attendance_df(days=60)
    df_7   = get_attendance_df(days=7)
    sec_df = get_security_logs_df(days=30)
    total  = get_total_employees()

    today = date.today().isoformat()
    today_df = df_30[df_30["date"].astype(str) == today] if not df_30.empty else pd.DataFrame()

    present_today = len(today_df[today_df["status"].isin(["Present", "Late"])])
    late_today    = len(today_df[today_df["status"] == "Late"])
    absent_today  = total - present_today

    rate_30 = get_attendance_rate(df_30)
    rate_prev = get_attendance_rate(df_60[df_60["date"] < (date.today() - timedelta(days=30))])

    # Department with highest attendance
    top_dept = ""
    if not df_30.empty and "department" in df_30.columns:
        dept_rates = df_30.groupby("department").apply(
            lambda g: len(g[g["status"].isin(["Present", "Late"])]) / len(g) * 100
        )
        top_dept = dept_rates.idxmax() if not dept_rates.empty else ""

    return {
        "total_employees":      total,
        "present_today":        present_today,
        "late_today":           late_today,
        "absent_today":         absent_today,
        "attendance_rate_30d":  rate_30,
        "attendance_rate_prev": rate_prev,
        "rate_change_pct":      round(rate_30 - rate_prev, 1),
        "security_incidents_30d": len(sec_df),
        "top_department":       top_dept,
    }


def generate_insights(kpis: dict) -> list[str]:
    """Produce natural-language insight strings from KPI data."""
    insights = []
    rate = kpis["attendance_rate_30d"]
    change = kpis["rate_change_pct"]

    if change > 0:
        insights.append(f"📈 Attendance improved by {abs(change):.1f}% compared to the previous period.")
    elif change < 0:
        insights.append(f"📉 Attendance dropped by {abs(change):.1f}% compared to the previous period.")
    else:
        insights.append("📊 Attendance rate is stable compared to the previous period.")

    if rate >= 90:
        insights.append(f"✅ Excellent overall attendance rate of {rate}% in the last 30 days.")
    elif rate >= 75:
        insights.append(f"⚠️ Attendance rate is {rate}% — consider reviewing absence policies.")
    else:
        insights.append(f"🚨 Low attendance rate of {rate}% — immediate management attention needed.")

    if kpis["late_today"] > 0:
        insights.append(f"🕐 {kpis['late_today']} employee(s) arrived late today.")

    if kpis["top_department"]:
        insights.append(f"🏆 {kpis['top_department']} department has the highest attendance rate.")

    incidents = kpis["security_incidents_30d"]
    if incidents == 0:
        insights.append("🔒 No security incidents in the last 30 days.")
    else:
        insights.append(f"⚠️ {incidents} security incident(s) detected in the last 30 days.")

    return insights


def attendance_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily attendance counts per status for trend chart."""
    if df.empty:
        return pd.DataFrame()
    df["date"] = pd.to_datetime(df["date"])
    trend = df.groupby(["date", "status"]).size().reset_index(name="count")
    return trend


def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-department attendance rate."""
    if df.empty or "department" not in df.columns:
        return pd.DataFrame()
    summary = (
        df.groupby(["department", "status"])
          .size()
          .reset_index(name="count")
    )
    total_per_dept = df.groupby("department").size().reset_index(name="total")
    summary = summary.merge(total_per_dept, on="department")
    summary["rate"] = (summary["count"] / summary["total"] * 100).round(1)
    return summary


def hourly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Check-in time distribution by hour."""
    if df.empty or "check_in_time" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["hour"] = pd.to_datetime(df["check_in_time"].astype(str), format="%H:%M:%S", errors="coerce").dt.hour
    return df.groupby("hour").size().reset_index(name="count")
