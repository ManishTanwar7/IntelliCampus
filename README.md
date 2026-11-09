# 🎓 IntelliCampus

> **A Modern Student Productivity & Academic Analytics Desktop Platform**  
> *Inspired by Collegia • Engineered with Python, PyQt6, Playwright, MySQL, Pandas & Plotly*

---

## 🌟 Overview

**IntelliCampus** is a student academic analytics and productivity desktop application designed for higher education students. Modeled after **Collegia**, it integrates with university management portals (**UIMS**) using user-provided credentials to streamline attendance tracking, assessment evaluation, timetable scheduling, goal management, and predictive AI analytics.

### 🛡️ Critical Security & CAPTCHA Compliance
**The system strictly complies with university security and anti-abuse policies and never bypasses CAPTCHA.**  
Whenever a security challenge or CAPTCHA appears during portal synchronization:
1. Playwright isolates the CAPTCHA image element.
2. The image is rendered immediately to the user inside a dedicated modal verification dialog (`CaptchaDialog`).
3. The background thread halts and **waits for the user's manual entry**.
4. The user's input is passed directly to the portal submission form.

---

## 🏗️ Architecture & OOP Design (MVC)

IntelliCampus is constructed strictly following **Model-View-Controller (MVC)** architecture and strict **Object-Oriented Programming (OOP)** principles:

```
IntelliCampus/
├── database/
│   ├── schema.sql                 # Complete MySQL 8.0 DDL Schema
│   └── seed_data.sql              # Realistic student data, subjects, attendance, marks
├── models/                        # Domain Models & Data Access Objects (DAO)
│   ├── student.py                 # Student identity and profile
│   ├── subject.py                 # Academic courses & faculty mapping
│   ├── attendance.py              # Course attendance, safe skips, recovery streak math
│   ├── marks.py                   # Internal MSTs, assignments, SGPA/CGPA history
│   ├── timetable.py               # Day-wise lecture schedule & labs
│   ├── assignment.py              # Course assignments & grading
│   ├── task.py                    # To-Do tasks with priority & categories
│   ├── goal.py                    # Target CGPA & attendance goals
│   ├── study_plan.py              # Scheduled study blocks
│   ├── session.py                 # Active user sessions & encrypted credentials
│   └── analytics.py               # Persisted AI predictions & snapshots
├── controllers/                   # Application Controllers
│   ├── auth_controller.py         # Login, AES-Fernet encryption, session state
│   ├── academic_controller.py     # Attendance, marks, timetable, grade math
│   ├── productivity_controller.py # Tasks, assignments, goals, planner
│   ├── analytics_controller.py    # AI model execution & cache
│   ├── report_controller.py       # PDF & Excel document generation
│   └── uims_sync_controller.py    # Threaded Playwright worker with CAPTCHA bridge
├── services/                      # Core Business & Infrastructure Services
│   ├── database.py                # Dual-engine DB manager (MySQL primary + SQLite fallback)
│   ├── security_service.py        # AES-Fernet symmetric encryption & salt generation
│   ├── ai_analytics_service.py    # Predictive algorithms (Shortage, CGPA, Weak Subjects)
│   ├── uims_scraper.py            # Playwright automation engine with manual CAPTCHA hook
│   ├── export_service.py          # ReportLab PDF generator & Pandas Excel exporter
│   └── notification_service.py    # Alert dispatcher & threshold monitors
├── views/                         # PyQt6 Presentation Layer
│   ├── main_window.py             # Collegia-style layout (sidebar + header + stack)
│   ├── components/
│   │   ├── theme.py               # Dark and Light QSS theme system
│   │   ├── cards.py               # Metric cards, progress bars, status pills
│   │   ├── charts.py              # Plotly interactive charts via QWebEngineView
│   │   └── captcha_dialog.py      # Manual CAPTCHA entry verification modal
│   └── pages/
│       ├── dashboard_page.py      # Collegia dashboard with metrics, alerts & charts
│       ├── attendance_page.py     # Course breakdown, "What-If" simulator & logs
│       ├── marks_page.py          # Internal marks & semester progression
│       ├── timetable_page.py      # Weekly schedule with today auto-jump
│       ├── productivity_page.py   # Assignment tracker, tasks, goals & study planner
│       ├── analytics_page.py      # AI shortage predictor, expected CGPA & recommendations
│       ├── reports_page.py        # One-click PDF & Excel download center
│       └── settings_page.py       # UIMS credentials, DB config & theme switcher
├── tests/
│   └── test_intellicampus.py      # Automated unit & integration tests
├── config.py                      # Application configuration & constants
├── requirements.txt               # Python package dependencies
├── run.bat                        # Windows batch launcher
├── run.ps1                        # PowerShell launcher
└── main.py                        # Desktop application entry point
```

---

## ⚡ Core Modules

### 1. 🔐 Authentication & Session Security
- **Secure Encrypted Storage**: Passwords are encrypted on disk using industry-standard **AES-Fernet** symmetric encryption combined with per-user cryptographic salts.
- **Session Management**: Tracks active session tokens and persistent login states.
- **Manual CAPTCHA Flow**: Seamless bridge between Playwright background threads and the PyQt6 main thread via Qt signals/events and thread synchronizers.

### 2. 📅 Academic Module
- **Attendance Tracking**: Calculates overall and subject-level attendance percentage including duty leaves and medical leaves.
- **Safe Skips & Recovery Streaks**:
  - `Safe Skips`: Exact number of classes a student can safely miss while remaining $\ge 75\%$.
  - `Recovery Streak`: Exact number of consecutive classes a student must attend if currently in shortage.
- **Interactive "What-If" Simulator**: Allows students to simulate: *"If I attend/miss next $N$ classes, what will my attendance become?"* with instantaneous visual feedback.
- **Marks & Results**: Comprehensive tracking of MST1, MST2, Continuous Evaluations, External Finals, and historical SGPA/CGPA.
- **Timetable Management**: Tabbed day-wise schedule (Monday–Saturday) showing course codes, lab locations, and faculty names with auto-jump to today's schedule.

### 3. ⚡ Student Productivity Suite
- **Assignment Tracker**: Status management (`Pending`, `In Progress`, `Submitted`, `Graded`), submission deadlines, and score tracking.
- **Task Manager**: High/Medium/Low priority to-do list with category filtering (`Study`, `Exam`, `Assignment`, `Project`).
- **Academic Goals**: Visual progress bars towards target CGPA, study hours, or subject grades.
- **Study Planner**: Scheduled study blocks by course and duration.

### 4. 🤖 AI Academic Analytics
- **Attendance Shortage Predictor**: Calculates current trajectory and forecasts end-of-semester attendance ranges (best-case vs worst-case) assuming remaining lecture quotas.
- **Expected CGPA Predictor**: Computes weighted regression combining previous semester SGPAs with current internal assessment performance.
- **Weak Subject Diagnostic**: Computes a Composite Risk Index (0–100) identifying subjects with assessment score drops or attendance vulnerabilities.
- **Personalized Recommendations**: Context-aware recommendations tailored to the student's academic standing.

### 5. 📊 Collegia-Inspired Modern Dashboard
- Modern Dark Theme (deep slate `#0F172A` + indigo accents `#6366F1`) and Light Theme.
- High-resolution interactive **Plotly charts** embedded directly inside PyQt6 using `QWebEngineView`.
- Critical alert banners for any subject dropping below the $75\%$ attendance threshold.

### 6. 📑 Reporting & Export
- **PDF Academic Dossier**: Professional multi-page PDF document generated using **ReportLab** containing student identification, color-coded attendance tables, assessment results, and AI recommendations.
- **Multi-Sheet Excel Workbook**: Multi-tab `.xlsx` generated using **Pandas** and **OpenPyXL** covering Overview, Attendance, Marks, Timetable, and Assignments.

---

## 🚀 Quick Start Guide

### Prerequisites
- Windows 10/11
- Python 3.11+
- (Optional) MySQL Server 8.0. *Note: If MySQL is not running, IntelliCampus automatically falls back to an embedded SQLite local database with zero setup required.*

### Launching the Application
Simply double-click `run.bat` or run in PowerShell:
```powershell
.\run.ps1
```
Or directly with Python:
```powershell
.\.venv\Scripts\python.exe main.py
```

### Running the Test Suite
```powershell
.\.venv\Scripts\python.exe tests\test_intellicampus.py
```

---

## 🗄️ MySQL Database Setup (Optional)
If you wish to use a live MySQL 8.0 server:
1. Ensure your MySQL server is running on port 3306.
2. Create and seed the database using the provided scripts:
```sql
SOURCE database/schema.sql;
SOURCE database/seed_data.sql;
```
3. Update connection parameters in `config.py` or via the in-app **Settings & Portal** page.
