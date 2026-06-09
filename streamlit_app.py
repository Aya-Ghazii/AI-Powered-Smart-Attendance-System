"""
Module 7 — Streamlit Dashboard
Interactive analytics dashboard for attendance and security monitoring.
Run: streamlit run dashboard/streamlit_app.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: #f0f4ff;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #1a73e8;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 { font-size: 2rem; margin: 0; color: #1a73e8; }
    .metric-card p  { margin: 0; color: #555; font-size: 0.85rem; }
    .insight-box {
        background: #fffbe6;
        border-left: 4px solid #f9a825;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
    }
    .danger-box {
        background: #fff0f0;
        border-left: 4px solid #e53935;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] { background: #f8f9fb; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/face-id.png", width=60)
    st.title("Smart Attendance")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Employees", "📅 Attendance Log",
         "🔒 Security", "📈 Analytics", "📄 Reports"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    date_range = st.selectbox("Date range", ["Last 7 days", "Last 30 days", "Last 90 days"], index=1)
    days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
    DAYS = days_map[date_range]
    st.caption(f"Showing data for past {DAYS} days")


# ── Data loading (cached) ─────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(days):
    try:
        from database.models import get_attendance_df, get_security_logs_df, get_total_employees
        from app.analytics import compute_kpis, generate_insights, attendance_trend, department_summary, hourly_distribution
        att_df  = get_attendance_df(days=days)
        sec_df  = get_security_logs_df(days=days)
        total   = get_total_employees()
        kpis    = compute_kpis()
        insights = generate_insights(kpis)
        return att_df, sec_df, total, kpis, insights
    except Exception as e:
        st.warning(f"Database not connected — showing demo data. ({e})")
        return _demo_data()


def _demo_data():
    import numpy as np
    np.random.seed(42)
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(30)]
    depts = ["Engineering", "HR", "Marketing", "IT", "Finance"]
    names = ["Aya Ghazi", "Omar Hassan", "Lina Nasser", "Khalid Farhat", "Sara Moussa",
             "Ahmad Karimi", "Dina Saad", "Rami Haddad", "Nour Khalil", "Tarek Nassar"]
    statuses = np.random.choice(["Present", "Late", "Absent"], size=(len(names), len(dates)),
                                 p=[0.75, 0.12, 0.13])
    rows = []
    for i, name in enumerate(names):
        for j, d in enumerate(dates):
            if statuses[i, j] != "Absent":
                rows.append({
                    "date": d,
                    "full_name": name,
                    "employee_id": f"EMP{i+1:03d}",
                    "department": depts[i % len(depts)],
                    "check_in_time": f"0{8+np.random.randint(0,3)}:{np.random.randint(0,59):02d}:00",
                    "status": statuses[i, j],
                    "confidence": round(np.random.uniform(0.7, 0.99), 2),
                })
    att_df = pd.DataFrame(rows)
    sec_rows = [{"log_id": i, "image_path": f"security_captures/unknown_{i}.jpg",
                  "detected_at": today - timedelta(hours=np.random.randint(0, 720)),
                  "alert_sent": bool(np.random.randint(0,2)),
                  "notes": ""} for i in range(1, 6)]
    sec_df = pd.DataFrame(sec_rows)
    total  = len(names)
    today_str = str(today)
    today_df = att_df[att_df["date"].astype(str) == today_str]
    present_today = len(today_df[today_df["status"].isin(["Present", "Late"])])
    late_today    = len(today_df[today_df["status"] == "Late"])
    kpis = {
        "total_employees": total, "present_today": present_today,
        "late_today": late_today, "absent_today": total - present_today,
        "attendance_rate_30d": 87.3, "attendance_rate_prev": 84.1,
        "rate_change_pct": 3.2, "security_incidents_30d": 5,
        "top_department": "IT",
    }
    insights = [
        "📈 Attendance improved by 3.2% compared to the previous period.",
        "✅ Overall attendance rate is 87.3% — solid performance.",
        "🏆 IT department has the highest attendance rate.",
        "⚠️ 5 security incidents detected in the last 30 days.",
    ]
    return att_df, sec_df, total, kpis, insights


att_df, sec_df, total, kpis, insights = load_data(DAYS)
today_str = str(date.today())
today_df  = att_df[att_df["date"].astype(str) == today_str] if not att_df.empty else pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  PAGE: Dashboard
# ══════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Attendance Dashboard")
    st.caption(f"Today: {date.today().strftime('%A, %d %B %Y')}")

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Employees",   kpis["total_employees"])
    c2.metric("✅ Present Today",      kpis["present_today"],
              delta=f"{kpis['rate_change_pct']:+.1f}% vs prev period")
    c3.metric("❌ Absent Today",       kpis["absent_today"])
    c4.metric("🕐 Late Today",         kpis["late_today"])
    c5.metric("🚨 Security Alerts",    kpis["security_incidents_30d"])

    st.markdown("---")

    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("Attendance Trend")
        if not att_df.empty:
            att_df["date"] = pd.to_datetime(att_df["date"])
            trend = att_df.groupby(["date", "status"]).size().reset_index(name="count")
            color_map = {"Present": "#1a73e8", "Late": "#f9a825", "Absent": "#e53935"}
            fig = px.area(trend, x="date", y="count", color="status",
                          color_discrete_map=color_map,
                          template="plotly_white")
            fig.update_layout(legend_title="", height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance data yet.")

    with col_r:
        st.subheader("Today's Status")
        if not today_df.empty:
            status_counts = today_df["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            color_map = {"Present": "#1a73e8", "Late": "#f9a825", "Absent": "#e53935"}
            fig2 = px.pie(status_counts, names="status", values="count",
                          color="status", color_discrete_map=color_map,
                          hole=0.5, template="plotly_white")
            fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                               showlegend=True, legend_orientation="h")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data for today yet.")

    # Department chart
    st.subheader("Department Attendance Rate")
    if not att_df.empty and "department" in att_df.columns:
        dept = att_df[att_df["status"].isin(["Present","Late"])] \
                     .groupby("department").size().reset_index(name="present")
        total_dept = att_df.groupby("department").size().reset_index(name="total")
        dept = dept.merge(total_dept, on="department")
        dept["rate"] = (dept["present"] / dept["total"] * 100).round(1)
        fig3 = px.bar(dept.sort_values("rate", ascending=True),
                      x="rate", y="department", orientation="h",
                      template="plotly_white",
                      color="rate", color_continuous_scale="Blues",
                      labels={"rate": "Attendance %"})
        fig3.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    # Insights
    st.subheader("🤖 AI Insights")
    for ins in insights:
        box_class = "danger-box" if "🚨" in ins or "📉" in ins else "insight-box"
        st.markdown(f'<div class="{box_class}">{ins}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PAGE: Employees
# ══════════════════════════════════════════════════════════════
elif page == "👥 Employees":
    st.title("👥 Employee Directory")
    try:
        from database.models import get_all_users
        users = get_all_users()
        if users:
            df_users = pd.DataFrame(users)
            display_cols = ["employee_id", "full_name", "email", "department", "phone", "created_at"]
            avail = [c for c in display_cols if c in df_users.columns]
            st.dataframe(df_users[avail], use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(df_users)} employees")
        else:
            st.info("No employees registered yet.")
    except Exception:
        st.info("Demo mode — connect database to see real employees.")


# ══════════════════════════════════════════════════════════════
#  PAGE: Attendance Log
# ══════════════════════════════════════════════════════════════
elif page == "📅 Attendance Log":
    st.title("📅 Attendance Log")

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_date = st.date_input("Filter by date", value=date.today())
    with col2:
        status_filter = st.multiselect("Filter by status",
                                       ["Present", "Late", "Absent"],
                                       default=["Present", "Late", "Absent"])

    if not att_df.empty:
        filtered = att_df.copy()
        filtered["date"] = pd.to_datetime(filtered["date"]).dt.date
        filtered = filtered[
            (filtered["date"] == selected_date) &
            (filtered["status"].isin(status_filter))
        ]
        st.dataframe(filtered.drop(columns=["confidence"], errors="ignore"),
                     use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} records")
    else:
        st.info("No attendance records found.")


# ══════════════════════════════════════════════════════════════
#  PAGE: Security
# ══════════════════════════════════════════════════════════════
elif page == "🔒 Security":
    st.title("🔒 Security Monitoring")

    c1, c2 = st.columns(2)
    c1.metric("Total Incidents (30d)", len(sec_df))
    c2.metric("Alerts Sent",
              sec_df["alert_sent"].sum() if not sec_df.empty else 0)

    if not sec_df.empty:
        st.subheader("Incident Log")
        display = sec_df.copy()
        if "detected_at" in display.columns:
            display["detected_at"] = pd.to_datetime(display["detected_at"])
        st.dataframe(display, use_container_width=True, hide_index=True)

        # Incidents over time
        if "detected_at" in sec_df.columns:
            sec_df["day"] = pd.to_datetime(sec_df["detected_at"]).dt.date
            by_day = sec_df.groupby("day").size().reset_index(name="count")
            fig = px.bar(by_day, x="day", y="count",
                         title="Daily Security Incidents",
                         template="plotly_white", color_discrete_sequence=["#e53935"])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No security incidents in this period.")


# ══════════════════════════════════════════════════════════════
#  PAGE: Analytics
# ══════════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics")

    if not att_df.empty:
        tab1, tab2, tab3 = st.tabs(["Monthly Heatmap", "Check-in Time", "Department Breakdown"])

        with tab1:
            att_df["date_dt"] = pd.to_datetime(att_df["date"])
            att_df["week"]    = att_df["date_dt"].dt.isocalendar().week.astype(int)
            att_df["weekday"] = att_df["date_dt"].dt.day_name()
            heat = att_df.groupby(["week", "weekday"]).size().reset_index(name="count")
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            fig = px.density_heatmap(heat, x="week", y="weekday",
                                     z="count", category_orders={"weekday": day_order},
                                     color_continuous_scale="Blues",
                                     template="plotly_white")
            fig.update_layout(title="Weekly Attendance Heatmap")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if "check_in_time" in att_df.columns:
                att_df["hour"] = pd.to_datetime(
                    att_df["check_in_time"].astype(str), format="%H:%M:%S", errors="coerce"
                ).dt.hour
                hour_dist = att_df.groupby("hour").size().reset_index(name="count")
                fig2 = px.bar(hour_dist, x="hour", y="count",
                              title="Check-in Time Distribution",
                              template="plotly_white",
                              color="count", color_continuous_scale="Blues",
                              labels={"hour": "Hour of Day", "count": "Check-ins"})
                st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            dept_present = att_df[att_df["status"].isin(["Present","Late"])]
            dept_summary = dept_present.groupby(["department","status"]).size().reset_index(name="count")
            color_map = {"Present": "#1a73e8", "Late": "#f9a825"}
            fig3 = px.bar(dept_summary, x="department", y="count", color="status",
                          barmode="stack", template="plotly_white",
                          color_discrete_map=color_map,
                          title="Attendance by Department (stacked)")
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data available for the selected period.")


# ══════════════════════════════════════════════════════════════
#  PAGE: Reports
# ══════════════════════════════════════════════════════════════
elif page == "📄 Reports":
    st.title("📄 Generate Reports")
    st.markdown("Generate PDF or Excel reports for selected periods.")

    col1, col2 = st.columns(2)
    with col1:
        report_type   = st.selectbox("Report type", ["daily", "weekly", "monthly"])
    with col2:
        report_format = st.selectbox("Format", ["PDF", "Excel", "Both"])

    if st.button("🚀 Generate Report", type="primary"):
        with st.spinner("Generating…"):
            try:
                from reports.report_generator import generate_pdf_report, generate_excel_report
                paths = []
                if report_format in ("PDF", "Both"):
                    p = generate_pdf_report(report_type)
                    paths.append(p)
                if report_format in ("Excel", "Both"):
                    p = generate_excel_report(report_type)
                    paths.append(p)
                for path in paths:
                    ext = path.split(".")[-1].upper()
                    with open(path, "rb") as f:
                        st.download_button(
                            f"⬇️ Download {ext} Report",
                            data=f.read(),
                            file_name=os.path.basename(path),
                            mime="application/octet-stream",
                        )
                st.success("✅ Reports generated successfully!")
            except Exception as e:
                st.error(f"Could not generate report: {e}")

    st.markdown("---")
    st.subheader("Previous Reports")
    try:
        from config.settings import REPORTS_DIR
        report_files = list(REPORTS_DIR.glob("*.pdf")) + list(REPORTS_DIR.glob("*.xlsx"))
        if report_files:
            for f in sorted(report_files, key=os.path.getmtime, reverse=True)[:10]:
                col_a, col_b = st.columns([3, 1])
                col_a.text(f.name)
                with open(f, "rb") as fh:
                    col_b.download_button("⬇️", data=fh.read(),
                                          file_name=f.name, key=str(f))
        else:
            st.info("No reports generated yet.")
    except Exception:
        pass
