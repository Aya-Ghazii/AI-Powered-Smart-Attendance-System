const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat, TableOfContents,
  PageBreak
} = require("docx");
const fs = require("fs");

const PAGE_W = 12240;
const MARGIN = 1440;
const CONTENT_W = PAGE_W - 2 * MARGIN;
const ACCENT = "1A73E8";
const LIGHT_BLUE = "E8F0FE";
const LIGHT_GRAY = "F5F5F5";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial", color: ACCENT })],
    spacing: { before: 360, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 4 } },
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial" })],
    spacing: { before: 280, after: 120 },
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, size: 22, font: "Arial" })],
    spacing: { before: 200, after: 80 },
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })],
    spacing: { after: 100 },
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, size: 22, font: "Arial" })],
    spacing: { after: 60 },
  });
}

function numbered(text) {
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    children: [new TextRun({ text, size: 22, font: "Arial" })],
    spacing: { after: 60 },
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function space() {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: 80 } });
}

function headerRow(cells, widths) {
  return new TableRow({
    children: cells.map((text, i) =>
      new TableCell({
        borders,
        width: { size: widths[i], type: WidthType.DXA },
        shading: { fill: ACCENT, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text, bold: true, size: 20, font: "Arial", color: "FFFFFF" })],
          alignment: AlignmentType.CENTER,
        })],
      })
    ),
  });
}

function dataRow(cells, widths, shade = false) {
  return new TableRow({
    children: cells.map((text, i) =>
      new TableCell({
        borders,
        width: { size: widths[i], type: WidthType.DXA },
        shading: { fill: shade ? LIGHT_BLUE : "FFFFFF", type: ShadingType.CLEAR },
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: String(text ?? ""), size: 20, font: "Arial" })],
        })],
      })
    ),
  });
}

function makeTable(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      headerRow(headers, widths),
      ...rows.map((r, i) => dataRow(r, widths, i % 2 === 1)),
    ],
  });
}

function codeBlock(lines) {
  return new Paragraph({
    children: [new TextRun({ text: lines, font: "Courier New", size: 18, color: "1A3A1A" })],
    shading: { fill: "F0F4F0", type: ShadingType.CLEAR },
    spacing: { after: 100, before: 60 },
    indent: { left: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 8, color: "1A73E8", space: 8 } },
  });
}

// ── Document ─────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
      },
      {
        reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
      },
    ],
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
        run: { size: 32, bold: true, font: "Arial", color: ACCENT },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
        run: { size: 26, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal",
        run: { size: 22, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: 15840 },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: "AI-Powered Smart Attendance & Security System", size: 18, font: "Arial", color: "666666" }),
              new TextRun({ text: "  |  Graduation Project", size: 18, font: "Arial", color: "999999" }),
            ],
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT, space: 4 } },
            spacing: { after: 0 },
          }),
        ],
      }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: "Page ", size: 18, font: "Arial", color: "999999" }),
              new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: "999999" }),
              new TextRun({ text: " of ", size: 18, font: "Arial", color: "999999" }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Arial", color: "999999" }),
            ],
            alignment: AlignmentType.CENTER,
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: ACCENT, space: 4 } },
          }),
        ],
      }),
    },
    children: [

      // ── COVER PAGE ────────────────────────────────────────
      ...Array(6).fill(null).map(() => space()),
      new Paragraph({
        children: [new TextRun({ text: "AI-Powered Smart Attendance", bold: true, size: 52, font: "Arial", color: ACCENT })],
        alignment: AlignmentType.CENTER, spacing: { after: 100 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "and Security System", bold: true, size: 52, font: "Arial", color: ACCENT })],
        alignment: AlignmentType.CENTER, spacing: { after: 240 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Using Face Recognition, Automation, and Data Analytics", size: 28, font: "Arial", color: "444444" })],
        alignment: AlignmentType.CENTER, spacing: { after: 60 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Graduation Project — Data Science & Artificial Intelligence", size: 24, font: "Arial", color: "666666", italics: true })],
        alignment: AlignmentType.CENTER, spacing: { after: 480 },
      }),
      makeTable(
        [], [
          ["Project Type",   "Graduation Project — Level 4"],
          ["Department",     "Data Science & Artificial Intelligence"],
          ["Technology Stack", "Python · OpenCV · MySQL · Streamlit · n8n"],
          ["Year",           "2025 / 2026"],
        ],
        [3600, 5760]
      ),
      pageBreak(),

      // ── ABSTRACT ──────────────────────────────────────────
      h1("Abstract"),
      p("This project presents the design and implementation of an AI-Powered Smart Attendance and Security System that leverages facial recognition technology to automate workplace attendance management and enhance facility security. The system uses deep learning-based face embeddings generated by the face_recognition library (built on dlib) to identify registered individuals in real time via a standard webcam."),
      space(),
      p("When a registered face is detected, the system automatically records attendance with a status classification of Present or Late based on configurable cutoff rules, prevents duplicate entries within the same day, and stores all records in a relational MySQL database. Unknown individuals trigger an immediate security response: a screenshot is captured, a security log entry is created, and automated alerts are dispatched via email and Telegram."),
      space(),
      p("A Streamlit-based interactive dashboard provides real-time KPI metrics, attendance trend charts, department-level analytics, and AI-generated insights powered by Pandas and NumPy. Automated PDF and Excel reports are generated for daily, weekly, and monthly periods using ReportLab and OpenPyXL."),
      space(),
      p("The system is designed to be scalable to 1,000+ users, supports multi-camera deployment, and provides a clean foundation for future enhancements including anti-spoofing, mobile access, and large language model-driven analytics."),
      pageBreak(),

      // ── TABLE OF CONTENTS ────────────────────────────────
      h1("Table of Contents"),
      new TableOfContents("Table of Contents", {
        hyperlink: true,
        headingStyleRange: "1-3",
      }),
      pageBreak(),

      // ── 1. INTRODUCTION ───────────────────────────────────
      h1("1. Introduction"),
      h2("1.1 Background"),
      p("Traditional attendance systems relying on manual registers, swipe cards, or PIN codes are time-consuming, error-prone, and vulnerable to proxy attendance (where one person records attendance on behalf of another). The proliferation of affordable webcams and advances in deep learning face recognition have made it practical to build systems that identify individuals automatically, accurately, and in real time."),
      space(),
      p("Face recognition systems encode the unique geometric features of a human face as a high-dimensional vector (embedding). Comparing embeddings using Euclidean distance allows the system to determine whether a detected face matches a registered identity, with sub-second latency suitable for real-world deployment."),

      h2("1.2 Problem Statement"),
      p("Organisations face significant challenges in attendance management: manual processes are slow and inaccurate; existing RFID or fingerprint systems require physical contact (a hygiene concern post-COVID); and security teams lack automated tools to detect and log unauthorised access. A unified system that handles attendance, security monitoring, analytics, and automated alerting from a single platform is needed."),

      h2("1.3 Project Objectives"),
      bullet("Detect and recognise registered faces in real time using a webcam."),
      bullet("Record attendance automatically with status classification (Present / Late / Absent)."),
      bullet("Detect unknown individuals and trigger multi-channel security alerts."),
      bullet("Store all data in a structured relational database with referential integrity."),
      bullet("Provide an interactive analytics dashboard with KPIs and visualisations."),
      bullet("Generate automated PDF and Excel reports for daily, weekly, and monthly periods."),
      bullet("Support scalability to 1,000+ users and multi-camera deployment."),

      h2("1.4 Scope"),
      p("The system covers employee attendance at a single-site organisation. The current release uses a single USB or built-in webcam; the architecture supports multi-camera extension. Face data is stored as JSON-serialised numpy arrays in the database; a future release may migrate to a dedicated vector database for improved retrieval performance at very large scale."),
      pageBreak(),

      // ── 2. SYSTEM REQUIREMENTS ────────────────────────────
      h1("2. System Requirements"),
      h2("2.1 Functional Requirements"),
      makeTable(
        ["Module", "Requirement", "Priority"],
        [
          ["Registration",    "Capture 10 face samples, compute average embedding, save to DB", "High"],
          ["Recognition",     "Identify faces in real time with < 2 s latency",                 "High"],
          ["Attendance",      "Classify Present / Late based on configurable time cutoff",        "High"],
          ["Attendance",      "Prevent duplicate records for the same user on the same day",       "High"],
          ["Security",        "Detect unknown faces and capture screenshot",                      "High"],
          ["Alerts",          "Send email alert with attached screenshot",                        "High"],
          ["Alerts",          "Send Telegram message with photo via Bot API",                     "High"],
          ["Database",        "Store users, attendance, and security logs in MySQL",              "High"],
          ["Dashboard",       "Display real-time KPIs: total, present, absent, late, incidents",  "High"],
          ["Dashboard",       "Show attendance trend, department breakdown, heatmap charts",      "Medium"],
          ["Analytics",       "Generate natural-language AI insights from statistics",            "Medium"],
          ["Reports",         "Export daily / weekly / monthly PDF and Excel reports",            "Medium"],
        ],
        [2400, 5400, 1560]
      ),
      space(),

      h2("2.2 Non-Functional Requirements"),
      makeTable(
        ["Category", "Requirement"],
        [
          ["Performance",  "Face recognition loop: < 2 seconds per frame on standard hardware"],
          ["Scalability",  "Support 1,000+ registered users; multi-camera thread architecture"],
          ["Security",     "Database credentials stored in .env (never hard-coded); passwords excluded from all logs"],
          ["Reliability",  "Duplicate prevention via unique DB constraint; camera reconnect on frame failure"],
          ["Usability",    "CLI registration wizard; Streamlit dashboard accessible from browser"],
          ["Portability",  "Runs on Ubuntu 22.04 LTS and Windows 10/11 with Python 3.10+"],
          ["Maintainability", "Modular architecture — each concern in a separate Python module"],
        ],
        [2400, 6960]
      ),
      pageBreak(),

      // ── 3. SYSTEM ARCHITECTURE ────────────────────────────
      h1("3. System Architecture"),
      h2("3.1 High-Level Architecture"),
      p("The system follows a layered architecture with five distinct tiers:"),
      space(),
      numbered("Input Layer — Webcam video feed or registration UI"),
      numbered("Processing Layer — Face detection (OpenCV) and recognition (face_recognition)"),
      numbered("Logic Layer — Attendance rules, security handling, alert dispatch"),
      numbered("Data Layer — MySQL database with three core tables"),
      numbered("Presentation Layer — Streamlit dashboard and generated reports"),
      space(),

      h2("3.2 Module Descriptions"),
      makeTable(
        ["Module", "File", "Responsibility"],
        [
          ["Registration",  "app/registration.py",       "Capture face samples, compute embeddings, save to DB"],
          ["Recognition",   "app/recognition.py",        "Real-time face detection and identity matching"],
          ["Attendance",    "app/attendance.py",         "Status classification and duplicate prevention"],
          ["Security",      "app/security.py",           "Unknown detection, screenshot capture, DB logging"],
          ["Alerts",        "app/alerts.py",             "Email (SMTP) and Telegram Bot API alerting"],
          ["Analytics",     "app/analytics.py",          "KPI computation and NL insight generation"],
          ["Dashboard",     "dashboard/streamlit_app.py","Interactive Streamlit web dashboard"],
          ["Reports",       "reports/report_generator.py","PDF (ReportLab) and Excel (OpenPyXL) reports"],
          ["DB Config",     "database/db_config.py",     "MySQL connection pool manager"],
          ["Models",        "database/models.py",        "All SQL queries and ORM-style helpers"],
          ["Settings",      "config/settings.py",        "Centralised config loaded from .env"],
        ],
        [2400, 3200, 3760]
      ),
      space(),

      h2("3.3 Technology Stack"),
      makeTable(
        ["Layer", "Technology", "Version", "Purpose"],
        [
          ["Face Detection",  "OpenCV",                "4.9.0", "Camera capture, frame processing, display"],
          ["Face Recognition","face_recognition + dlib","1.3.0", "128-d face embeddings, distance matching"],
          ["Backend",         "Python",                "3.10+",  "Core application logic"],
          ["Database",        "MySQL",                 "8.0",    "Structured data storage"],
          ["Dashboard",       "Streamlit + Plotly",    "1.35 / 5.22", "Interactive web UI"],
          ["Email Alerts",    "Python smtplib",        "stdlib", "SMTP email with attachment"],
          ["Telegram Alerts", "Telegram Bot API",      "REST",   "Bot messages with photo"],
          ["PDF Reports",     "ReportLab",             "4.2.0",  "Programmatic PDF generation"],
          ["Excel Reports",   "OpenPyXL",              "3.1.4",  "XLSX workbook generation"],
          ["Analytics",       "Pandas + NumPy",        "2.2 / 1.26", "Statistical analysis"],
        ],
        [2400, 2400, 1440, 3120]
      ),
      pageBreak(),

      // ── 4. DATABASE DESIGN ────────────────────────────────
      h1("4. Database Design"),
      h2("4.1 Entity-Relationship Overview"),
      p("The database contains three primary entities: Users (registered employees with face embeddings), Attendance (daily check-in records per user), and Security_Logs (timestamped unknown-face detection events). The Users-to-Attendance relationship is one-to-many (one user has many attendance records). Security logs are independent of users by design, as they record unidentified individuals."),

      h2("4.2 Users Table"),
      makeTable(
        ["Column", "Type", "Constraints", "Description"],
        [
          ["user_id",       "INT",       "PK, AUTO_INCREMENT",       "Unique user identifier"],
          ["full_name",     "VARCHAR(100)", "NOT NULL",              "Employee full name"],
          ["employee_id",   "VARCHAR(20)",  "UNIQUE, NOT NULL",      "Organisation employee code"],
          ["email",         "VARCHAR(100)", "UNIQUE",                "Email address"],
          ["phone",         "VARCHAR(20)",  "",                      "Contact phone"],
          ["department",    "VARCHAR(50)",  "",                      "Organisational department"],
          ["face_encoding", "LONGTEXT",     "",                      "JSON-serialised 128-d embedding"],
          ["created_at",    "DATETIME",     "DEFAULT NOW()",         "Registration timestamp"],
          ["is_active",     "BOOLEAN",      "DEFAULT TRUE",          "Soft delete flag"],
        ],
        [2000, 1800, 2400, 3160]
      ),
      space(),

      h2("4.3 Attendance Table"),
      makeTable(
        ["Column", "Type", "Constraints", "Description"],
        [
          ["attendance_id", "INT",     "PK, AUTO_INCREMENT",          "Unique record identifier"],
          ["user_id",       "INT",     "FK → users.user_id",          "Linked employee"],
          ["date",          "DATE",    "NOT NULL",                    "Check-in date"],
          ["check_in_time", "TIME",    "NOT NULL",                    "Check-in time"],
          ["status",        "ENUM",    "Present | Late | Absent",     "Attendance status"],
          ["confidence",    "FLOAT",   "",                            "Recognition confidence score"],
          ["created_at",    "DATETIME","DEFAULT NOW()",               "Record creation timestamp"],
          ["—",             "UNIQUE KEY", "(user_id, date)",          "Prevents duplicate entries"],
        ],
        [2000, 1800, 2400, 3160]
      ),
      space(),

      h2("4.4 Security Logs Table"),
      makeTable(
        ["Column", "Type", "Constraints", "Description"],
        [
          ["log_id",      "INT",       "PK, AUTO_INCREMENT",  "Unique log identifier"],
          ["image_path",  "VARCHAR(255)", "",                  "Path to captured screenshot"],
          ["detected_at", "DATETIME",  "DEFAULT NOW()",        "Detection timestamp"],
          ["alert_sent",  "BOOLEAN",   "DEFAULT FALSE",        "Whether alert was dispatched"],
          ["notes",       "VARCHAR(255)", "",                  "Optional operator notes"],
        ],
        [2000, 1800, 2400, 3160]
      ),
      pageBreak(),

      // ── 5. MODULE IMPLEMENTATION ──────────────────────────
      h1("5. Module Implementation"),

      h2("5.1 Face Registration (Module 1)"),
      p("The registration module guides the operator through a CLI form to collect employee metadata, then opens the webcam and collects CAPTURE_SAMPLES (default 10) face frames. For each frame, face_recognition.face_encodings() extracts a 128-dimensional vector. The vectors are averaged to produce a robust composite embedding that is JSON-serialised and stored in the face_encoding column of the users table. Raw capture frames are also saved to face_data/captures/<name>/ for audit purposes."),

      h2("5.2 Real-Time Face Recognition (Module 2)"),
      p("The recognition engine loads all known embeddings from the database at startup, then processes each webcam frame in a detect-encode-match loop. Frames are downsampled to 25% resolution for detection speed before being upscaled for display. For each detected face, face_recognition.face_distance() computes the Euclidean distance to every stored embedding; the minimum distance is compared to RECOGNITION_THRESHOLD (default 0.5, lower = stricter)."),
      space(),
      p("A per-identity cooldown of 10 seconds prevents the same face from re-triggering attendance or alerts within a session. The display overlay shows name, confidence percentage, a colour-coded bounding box (green = known, red = unknown), and a live statistics bar showing total employees, present count, and security alert count."),

      h2("5.3 Attendance Logic (Module 3)"),
      p("Status classification compares datetime.now().time() to the LATE_CUTOFF constant (default 09:00). Before writing to the database, already_recorded_today() queries the attendance table for an existing record with the same (user_id, date) pair. If found, the new record is silently skipped. MySQL's UNIQUE KEY constraint on (user_id, date) provides a second line of defence via INSERT IGNORE."),

      h2("5.4 Security Monitoring (Module 4)"),
      p("When an unknown face is detected (distance > threshold), handle_unknown_detection() is called with a copy of the current frame. The frame is written to security_captures/ with a microsecond-precision timestamp filename. The file path is inserted into security_logs and the log_id is passed to the alert pipeline."),

      h2("5.5 Alert Automation (Module 5)"),
      p("Email alerts are composed using Python's email.mime package, with the screenshot attached as a MIMEImage part. The message is sent via SMTP with STARTTLS on port 587. Telegram alerts use the sendPhoto endpoint of the Bot API, posting the captured image with a formatted caption. Both channels are attempted independently; if either fails (e.g. no network), the other proceeds. On success of any channel, mark_alert_sent() updates the security log record."),

      h2("5.6 AI Analytics (Module 8)"),
      p("The analytics module computes KPIs by querying the last 30 days of attendance data. The attendance rate is computed as (present + late records) / (total employees × days with data). A comparison against the preceding 30-day window produces a rate_change_pct value that drives the trend insight. The top-performing department is identified via a groupby operation. Natural-language insights are assembled from conditional rules mapping KPI ranges to human-readable sentences."),
      pageBreak(),

      // ── 6. DASHBOARD ──────────────────────────────────────
      h1("6. Streamlit Dashboard"),
      p("The dashboard provides five main sections accessible via the sidebar:"),
      space(),
      makeTable(
        ["Section", "Content"],
        [
          ["Dashboard",     "KPI metrics row, attendance trend area chart, today's status pie chart, department bar chart, AI insights panel"],
          ["Employees",     "Full employee directory table with filtering"],
          ["Attendance Log","Date and status-filtered attendance records"],
          ["Security",      "Security incident log, alert status, daily incidents bar chart"],
          ["Analytics",     "Weekly heatmap, check-in time distribution, stacked department chart"],
          ["Reports",       "Report period/format selector, generate and download buttons, previous reports list"],
        ],
        [2400, 6960]
      ),
      space(),
      p("The dashboard is fully functional in demo mode (no database required): when the database connection fails, realistic synthetic data is generated so the UI can be demonstrated during presentations. The demo data generation uses a fixed numpy random seed for reproducibility."),
      pageBreak(),

      // ── 7. TESTING ────────────────────────────────────────
      h1("7. Testing Plan"),
      h2("7.1 Unit Tests"),
      makeTable(
        ["Test Case", "Method", "Expected Result"],
        [
          ["Present classification",     "Mock datetime to 08:30",                  "classify_status() returns 'Present'"],
          ["Late classification",         "Mock datetime to 09:30",                  "classify_status() returns 'Late'"],
          ["Duplicate prevention",        "Mock DB to return existing record",        "already_recorded_today() returns True"],
          ["No duplicate on new day",     "Mock DB to return empty result",           "already_recorded_today() returns False"],
          ["Encoding load",               "Mock DB rows with 128-d JSON arrays",     "Two equal-length lists returned"],
          ["Insight generation",          "Pass sample KPI dict",                    "Non-empty list of string insights"],
          ["Trend DataFrame shape",       "Pass 2-row attendance DataFrame",         "Columns: date, status, count"],
          ["Telegram called",             "Mock requests.post",                      "requests.post called once"],
        ],
        [3000, 3200, 3160]
      ),
      space(),

      h2("7.2 Integration Tests"),
      makeTable(
        ["Scenario", "Steps", "Pass Criteria"],
        [
          ["Full registration flow",   "Register user via CLI → check DB",           "Row in users with face_encoding"],
          ["Recognition to attendance","Run recognition with known face",             "Row in attendance, status correct"],
          ["Unknown face alert",       "Present unknown face",                        "Screenshot saved, DB log inserted, alerts fired"],
          ["Duplicate same-day scan",  "Scan registered face twice in same session",  "Single attendance row for today"],
          ["PDF report generation",    "Call generate_pdf_report('daily')",           "Valid PDF in reports/output/"],
          ["Excel report generation",  "Call generate_excel_report('monthly')",       "Valid XLSX with 3 sheets"],
          ["Dashboard demo mode",      "Open dashboard without DB",                   "KPIs visible, no crash"],
        ],
        [2400, 3600, 3360]
      ),
      pageBreak(),

      // ── 8. DEPLOYMENT ─────────────────────────────────────
      h1("8. Deployment Guide"),
      h2("8.1 Prerequisites"),
      bullet("Python 3.10 or later"),
      bullet("MySQL 8.0 server (local or remote)"),
      bullet("cmake and C++ build tools (required by dlib)"),
      bullet("Ubuntu 22.04 LTS, Windows 10/11, or macOS 12+"),
      space(),

      h2("8.2 Local Setup"),
      codeBlock("# 1. Clone / extract the project\ncd smart_attendance"),
      codeBlock("# 2. Install system dependencies (Ubuntu)\nsudo apt-get update\nsudo apt-get install cmake libboost-all-dev libgl1-mesa-glx"),
      codeBlock("# 3. Install Python packages\npip install -r requirements.txt"),
      codeBlock("# 4. Configure environment\ncp config/.env.example config/.env\n# Edit config/.env with your credentials"),
      codeBlock("# 5. Create database\nmysql -u root -p < database/schema.sql"),
      codeBlock("# 6. Register first user\npython app/main.py --mode register"),
      codeBlock("# 7. Start recognition\npython app/main.py --mode recognize"),
      codeBlock("# 8. Launch dashboard (separate terminal)\nstreamlit run dashboard/streamlit_app.py"),
      space(),

      h2("8.3 Production Recommendations"),
      bullet("Run recognition loop as a systemd service for auto-restart on failure."),
      bullet("Deploy Streamlit dashboard behind nginx with HTTPS for external access."),
      bullet("Use a managed MySQL instance (AWS RDS, PlanetScale) for production data."),
      bullet("Set up daily cron job to call python app/main.py --mode report for automated reports."),
      bullet("Use Docker to containerise the application for consistent deployment."),
      pageBreak(),

      // ── 9. FUTURE IMPROVEMENTS ────────────────────────────
      h1("9. Future Improvements"),
      makeTable(
        ["Improvement", "Description", "Complexity"],
        [
          ["Anti-spoofing",         "Add liveness detection (blink / head-turn challenge) to prevent photo attacks", "High"],
          ["Multi-camera support",  "Thread-based camera manager supporting N concurrent webcam streams",            "Medium"],
          ["Mobile app",            "Flutter companion app for managers: view live attendance, approve exceptions",  "High"],
          ["LLM analytics",         "Natural language query interface: 'Who had most absences this month?'",         "Medium"],
          ["Edge deployment",       "Run on Raspberry Pi 4 with Coral USB TPU for sub-1s recognition",              "Medium"],
          ["GDPR compliance",       "Right-to-erasure endpoint; consent logging; face data encryption at rest",      "Medium"],
          ["Vector database",       "Migrate embeddings to Milvus or Pinecone for faster search at 10k+ users",     "Medium"],
          ["Shift scheduling",      "Integrate shift roster; auto-mark absent when shift starts with no check-in",  "Low"],
          ["Visitor management",    "Temporary registration for visitors with auto-expiry",                         "Low"],
          ["Emotion analysis",      "Optional wellness module detecting stress indicators (IRB ethics required)",   "High"],
        ],
        [3200, 4400, 1760]
      ),
      pageBreak(),

      // ── 10. CONCLUSION ────────────────────────────────────
      h1("10. Conclusion"),
      p("This project successfully demonstrates the integration of modern AI and automation technologies into a practical, deployable attendance and security system. The system achieves its core objectives: real-time face recognition with sub-2-second latency, automatic attendance classification with duplicate prevention, multi-channel security alerting, interactive analytics, and automated report generation."),
      space(),
      p("The modular architecture ensures that each component is independently testable and maintainable. The use of industry-standard libraries (OpenCV, face_recognition, Streamlit, MySQL, ReportLab) ensures long-term support and a clear upgrade path. The demo mode in the dashboard enables full presentation of the system's capabilities even in environments without a live database or camera, making it ideal for academic evaluation."),
      space(),
      p("The project provides a strong foundation for production deployment and academic publication. Future extensions — particularly anti-spoofing, edge deployment, and LLM-driven analytics — represent natural follow-on research directions that could form the basis of postgraduate work."),
      pageBreak(),

      // ── REFERENCES ────────────────────────────────────────
      h1("References"),
      numbered("Amos, B., Ludwiczuk, B., & Satyanarayanan, M. (2016). OpenFace: A general-purpose face recognition library with mobile applications. Technical Report, Carnegie Mellon University."),
      numbered("King, D. E. (2009). Dlib-ml: A machine learning toolkit. Journal of Machine Learning Research, 10, 1755–1758."),
      numbered("Schroff, F., Kalenichenko, D., & Philbin, J. (2015). FaceNet: A unified embedding for face recognition and clustering. CVPR 2015."),
      numbered("Bradski, G. (2000). The OpenCV library. Dr. Dobb's Journal of Software Tools."),
      numbered("McKinney, W. (2010). Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference."),
      numbered("Streamlit Inc. (2024). Streamlit documentation. https://docs.streamlit.io"),
      numbered("MySQL AB. (2024). MySQL 8.0 reference manual. https://dev.mysql.com/doc/"),
      numbered("Python Software Foundation. (2024). smtplib — SMTP protocol client. Python 3 Documentation."),
      numbered("Telegram. (2024). Telegram Bot API documentation. https://core.telegram.org/bots/api"),
      numbered("OpenPyXL contributors. (2024). OpenPyXL documentation. https://openpyxl.readthedocs.io"),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/smart_attendance/docs/Project_Documentation.docx", buffer);
  console.log("✅ Documentation saved.");
});
