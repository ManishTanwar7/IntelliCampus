-- =======================================================================
-- IntelliCampus: Database Schema (MySQL 8.0+)
-- Modern Student Productivity & Academic Analytics Platform
-- =======================================================================

CREATE DATABASE IF NOT EXISTS intellicampus_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE intellicampus_db;

-- Disable FK checks during table setup
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Students Table
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    student_id VARCHAR(32) PRIMARY KEY, -- e.g. UIMS UID (21BCS1001)
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    program VARCHAR(100) NOT NULL, -- e.g. B.E. Computer Science & Engineering
    semester INT NOT NULL DEFAULT 1,
    section VARCHAR(16),
    batch VARCHAR(16),             -- e.g. 2023-2027
    avatar_url VARCHAR(255),
    uims_username VARCHAR(64) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Sessions Table (for active UIMS sessions and desktop app auth)
DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    token TEXT,
    cookies_json LONGTEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. User Credentials (Secure encrypted storage for UIMS)
DROP TABLE IF EXISTS user_credentials;
CREATE TABLE user_credentials (
    credential_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL UNIQUE,
    uims_user_id VARCHAR(64) NOT NULL,
    encrypted_password TEXT NOT NULL,
    encryption_salt VARCHAR(64) NOT NULL,
    is_remembered BOOLEAN DEFAULT FALSE,
    last_sync_at TIMESTAMP NULL,
    sync_status ENUM('SUCCESS', 'FAILED', 'IN_PROGRESS', 'IDLE') DEFAULT 'IDLE',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Subjects Table
DROP TABLE IF EXISTS subjects;
CREATE TABLE subjects (
    subject_code VARCHAR(32) PRIMARY KEY, -- e.g. 21CS301
    subject_name VARCHAR(150) NOT NULL,
    credits DECIMAL(3,1) NOT NULL DEFAULT 3.0,
    semester INT NOT NULL,
    faculty_name VARCHAR(120),
    subject_type ENUM('Theory', 'Practical', 'Project', 'Elective') DEFAULT 'Theory',
    min_attendance_pct DECIMAL(5,2) DEFAULT 75.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Attendance Summary Table (Aggregated by subject)
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    subject_code VARCHAR(32) NOT NULL,
    total_delivered INT NOT NULL DEFAULT 0,
    total_attended INT NOT NULL DEFAULT 0,
    duty_leave INT NOT NULL DEFAULT 0,
    medical_leave INT NOT NULL DEFAULT 0,
    percentage DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN total_delivered = 0 THEN 0.00
            ELSE ROUND(((total_attended + duty_leave + medical_leave) * 100.0) / total_delivered, 2)
        END
    ) STORED,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_subject (student_id, subject_code),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Attendance Detailed Records (Individual lecture records)
DROP TABLE IF EXISTS attendance_records;
CREATE TABLE attendance_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    subject_code VARCHAR(32) NOT NULL,
    lecture_date DATE NOT NULL,
    time_slot VARCHAR(32) NOT NULL,
    status ENUM('Present', 'Absent', 'Duty Leave', 'Medical Leave') NOT NULL,
    topic_covered VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Marks & Assessments Table
DROP TABLE IF EXISTS marks;
CREATE TABLE marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    subject_code VARCHAR(32) NOT NULL,
    semester INT NOT NULL,
    component_type ENUM('Internal_MST1', 'Internal_MST2', 'Assignment', 'Quiz', 'Surprise_Test', 'Practical_Internal', 'External_Final') NOT NULL,
    max_marks DECIMAL(5,2) NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    weightage_pct DECIMAL(5,2) DEFAULT 0.00,
    grade VARCHAR(4),
    recorded_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Semester Results Table (SGPA / CGPA history)
DROP TABLE IF EXISTS semester_results;
CREATE TABLE semester_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    semester INT NOT NULL,
    total_credits DECIMAL(4,1) NOT NULL,
    earned_credits DECIMAL(4,1) NOT NULL,
    sgpa DECIMAL(4,2) NOT NULL,
    cgpa DECIMAL(4,2) NOT NULL,
    status ENUM('Passed', 'Reappear', 'Pending') DEFAULT 'Passed',
    published_date DATE,
    UNIQUE KEY uq_student_semester (student_id, semester),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Timetable Table
DROP TABLE IF EXISTS timetable;
CREATE TABLE timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    subject_code VARCHAR(32) NOT NULL,
    room_no VARCHAR(32),
    faculty_name VARCHAR(120),
    is_lab BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 10. Assignments Table
DROP TABLE IF EXISTS assignments;
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    subject_code VARCHAR(32) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATETIME NOT NULL,
    status ENUM('Pending', 'In Progress', 'Submitted', 'Graded') DEFAULT 'Pending',
    max_marks DECIMAL(5,2) DEFAULT 100.0,
    marks_awarded DECIMAL(5,2) NULL,
    submission_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Tasks Table (Productivity / To-Do)
DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    title VARCHAR(200) NOT NULL,
    category ENUM('Study', 'Assignment', 'Exam', 'Project', 'General') DEFAULT 'General',
    priority ENUM('High', 'Medium', 'Low') DEFAULT 'Medium',
    due_date DATE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. Goals Table
DROP TABLE IF EXISTS goals;
CREATE TABLE goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    title VARCHAR(150) NOT NULL,
    target_type ENUM('Target_CGPA', 'Min_Attendance', 'Subject_Grade', 'Study_Hours', 'Custom') NOT NULL,
    target_value DECIMAL(6,2) NOT NULL,
    current_value DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    unit VARCHAR(32) DEFAULT '',
    deadline DATE,
    status ENUM('Active', 'Achieved', 'Missed') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 13. Study Plans Table
DROP TABLE IF EXISTS study_plans;
CREATE TABLE study_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    subject_code VARCHAR(32) NOT NULL,
    scheduled_date DATE NOT NULL,
    start_time TIME,
    duration_minutes INT NOT NULL DEFAULT 60,
    topic VARCHAR(200) NOT NULL,
    notes TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 14. AI Analytics Table (Snapshots and predictions)
DROP TABLE IF EXISTS ai_analytics;
CREATE TABLE ai_analytics (
    analytics_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_cgpa DECIMAL(4,2),
    weak_subjects_json LONGTEXT,
    shortage_risk_subjects_json LONGTEXT,
    attendance_safe_skips_json LONGTEXT,
    recommendations_json LONGTEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 15. Notifications Table
DROP TABLE IF EXISTS notifications;
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(32) NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    category ENUM('Attendance', 'Assignment', 'Exam', 'System', 'Analytics') DEFAULT 'System',
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- Indexes for performance
CREATE INDEX idx_attendance_student ON attendance (student_id);
CREATE INDEX idx_marks_student ON marks (student_id);
CREATE INDEX idx_timetable_day ON timetable (day_of_week);
CREATE INDEX idx_assignments_due ON assignments (due_date);
CREATE INDEX idx_tasks_due ON tasks (due_date);
CREATE INDEX idx_notifications_unread ON notifications (student_id, is_read);
