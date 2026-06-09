-- ============================================================
--  Smart Attendance & Security System — MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_attendance
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_attendance;

-- ── Users ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id       INT            AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100)   NOT NULL,
    employee_id   VARCHAR(20)    UNIQUE NOT NULL,
    email         VARCHAR(100)   UNIQUE,
    phone         VARCHAR(20),
    department    VARCHAR(50),
    face_encoding LONGTEXT,                        -- JSON-serialised numpy array
    created_at    DATETIME       DEFAULT CURRENT_TIMESTAMP,
    is_active     BOOLEAN        DEFAULT TRUE
) ENGINE=InnoDB;

-- ── Attendance ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT          AUTO_INCREMENT PRIMARY KEY,
    user_id       INT          NOT NULL,
    date          DATE         NOT NULL,
    check_in_time TIME         NOT NULL,
    status        ENUM('Present','Late','Absent') NOT NULL,
    confidence    FLOAT,                            -- recognition confidence 0-1
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY no_duplicate_per_day (user_id, date)
) ENGINE=InnoDB;

-- ── Security logs ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS security_logs (
    log_id       INT          AUTO_INCREMENT PRIMARY KEY,
    image_path   VARCHAR(255),
    detected_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    alert_sent   BOOLEAN      DEFAULT FALSE,
    notes        VARCHAR(255)
) ENGINE=InnoDB;

-- ── Useful indexes ────────────────────────────────────────────
CREATE INDEX idx_attendance_date       ON attendance (date);
CREATE INDEX idx_attendance_user_date  ON attendance (user_id, date);
CREATE INDEX idx_security_detected_at ON security_logs (detected_at);

-- ── Sample seed data (optional, remove in production) ─────────
INSERT INTO users (full_name, employee_id, email, department, phone)
VALUES
    ('Aya Ghazi',    'EMP001', 'aya@company.com',    'Engineering', '+961 70 000 001'),
    ('Omar Hassan',  'EMP002', 'omar@company.com',   'HR',          '+961 70 000 002'),
    ('Lina Nasser',  'EMP003', 'lina@company.com',   'Marketing',   '+961 70 000 003'),
    ('Khalid Farhat','EMP004', 'khalid@company.com', 'IT',          '+961 70 000 004'),
    ('Sara Moussa',  'EMP005', 'sara@company.com',   'Finance',     '+961 70 000 005');
