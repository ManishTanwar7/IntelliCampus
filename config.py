"""
IntelliCampus: Application Configuration & Constants
"""
import os
import sys
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

for folder in [DATA_DIR, EXPORTS_DIR, ASSETS_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# App Metadata
APP_NAME = "IntelliCampus"
APP_SUBTITLE = "Smart Academic Analytics & Productivity Platform"
APP_VERSION = "1.0.0"
AUTHOR = "Antigravity Engineering"

# Database Configuration
import urllib.parse
raw_db_url = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL")
mysql_host = os.environ.get("INTELLICAMPUS_DB_HOST", "127.0.0.1")
mysql_port = int(os.environ.get("INTELLICAMPUS_DB_PORT", 3306))
mysql_user = os.environ.get("INTELLICAMPUS_DB_USER", "root")
mysql_pass = os.environ.get("INTELLICAMPUS_DB_PASS", "")
mysql_name = os.environ.get("INTELLICAMPUS_DB_NAME", "intellicampus_db")

if raw_db_url:
    try:
        parsed_url = urllib.parse.urlparse(raw_db_url)
        mysql_host = parsed_url.hostname or mysql_host
        mysql_port = parsed_url.port or mysql_port
        mysql_user = parsed_url.username or mysql_user
        mysql_pass = parsed_url.password or mysql_pass
        mysql_name = parsed_url.path.lstrip('/') or mysql_name
    except Exception:
        pass

DB_CONFIG = {
    "engine": "mysql",  # 'mysql' or 'sqlite'
    "mysql": {
        "host": mysql_host,
        "port": mysql_port,
        "user": mysql_user,
        "password": mysql_pass,
        "database": mysql_name,
        "charset": "utf8mb4",
        "connect_timeout": 5
    },
    "sqlite": {
        "database": str(DATA_DIR / "intellicampus.db")
    }
}

# Academic Rules & Thresholds
ACADEMIC_RULES = {
    "min_attendance_pct": 75.0,
    "warning_attendance_pct": 80.0,
    "target_attendance_pct": 85.0,
    "target_cgpa": 8.5,
    "lecture_duration_minutes": 60,
    "lab_duration_minutes": 120
}

# UIMS Portal Settings
UIMS_CONFIG = {
    "login_url": "https://uims.cuchd.in/uims/",
    "home_url": "https://uims.cuchd.in/uims/frmStudentDashboard.aspx",
    "attendance_url": "https://uims.cuchd.in/uims/frmStudentCourseWiseAttendanceSummary.aspx",
    "marks_url": "https://uims.cuchd.in/uims/frmStudentMarksView.aspx",
    "timetable_url": "https://uims.cuchd.in/uims/frmMyTimeTable.aspx",
    "headless": False,  # Show browser during manual CAPTCHA entry or login if needed
    "timeout_ms": 30000,
    "demo_mode": False  # When True, simulated portal responds with real-like data
}

# Security Configuration
SECURITY_KEY_FILE = DATA_DIR / ".secret.key"
