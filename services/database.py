"""
IntelliCampus: Database Management Service
Provides unified database access supporting MySQL (primary) and SQLite (automatic fallback)
with transaction support, automated migrations, and seed data initialization.
"""
import os
import re
import sqlite3
import pymysql
import pymysql.cursors
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

from config import DB_CONFIG, DATA_DIR, BASE_DIR

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.engine_type = DB_CONFIG["engine"]  # 'mysql' or 'sqlite'
        self.mysql_config = DB_CONFIG["mysql"]
        self.sqlite_db_path = DB_CONFIG["sqlite"]["database"]
        self._active_connection = None
        self._using_sqlite_fallback = False
        self._initialize_connection()
        self._initialized = True

    def _initialize_connection(self):
        """Attempts connection to MySQL; falls back gracefully to SQLite if unavailable."""
        if self.engine_type == "mysql":
            try:
                # First try connecting to MySQL server directly
                test_conn = pymysql.connect(
                    host=self.mysql_config["host"],
                    port=self.mysql_config["port"],
                    user=self.mysql_config["user"],
                    password=self.mysql_config["password"],
                    charset=self.mysql_config["charset"],
                    connect_timeout=self.mysql_config["connect_timeout"]
                )
                with test_conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.mysql_config['database']}` CHARACTER SET utf8mb4;")
                test_conn.close()

                # Connect to the specific database
                self._test_mysql_active = True
                self._using_sqlite_fallback = False
                print(f"[DatabaseManager] Successfully connected to MySQL at {self.mysql_config['host']}:{self.mysql_config['port']}")
            except Exception as e:
                print(f"[DatabaseManager] MySQL connection failed ({e}). Switching to embedded SQLite fallback.")
                self._using_sqlite_fallback = True
        else:
            self._using_sqlite_fallback = True

        # Initialize schema and seed data if needed
        self.init_database()

    def get_connection(self):
        """Returns a live connection based on current engine."""
        if not self._using_sqlite_fallback:
            return pymysql.connect(
                host=self.mysql_config["host"],
                port=self.mysql_config["port"],
                user=self.mysql_config["user"],
                password=self.mysql_config["password"],
                database=self.mysql_config["database"],
                charset=self.mysql_config["charset"],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        else:
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    def _translate_query_for_sqlite(self, query: str) -> str:
        """Adapts MySQL query syntax to SQLite syntax."""
        # Replace %s with ? for parameters
        q = query.replace("%s", "?")
        # Replace MySQL specific data types / clauses
        q = re.sub(r'ON DUPLICATE KEY UPDATE.*?;', ';', q, flags=re.IGNORECASE)
        q = re.sub(r'GENERATED ALWAYS AS.*?(?=,)', 'DEFAULT 0.00', q, flags=re.IGNORECASE)
        q = re.sub(r'AUTO_INCREMENT', 'AUTOINCREMENT', q, flags=re.IGNORECASE)
        q = re.sub(r'LONGTEXT', 'TEXT', q, flags=re.IGNORECASE)
        q = re.sub(r'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', 'DATETIME DEFAULT CURRENT_TIMESTAMP', q, flags=re.IGNORECASE)
        q = re.sub(r'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP', q, flags=re.IGNORECASE)
        q = re.sub(r'ENGINE\s*=\s*InnoDB', '', q, flags=re.IGNORECASE)
        return q

    def execute_update(self, query: str, params: Union[Tuple, List, None] = None) -> int:
        """Executes INSERT, UPDATE, DELETE queries and returns lastrowid or affected rows."""
        conn = self.get_connection()
        try:
            if self._using_sqlite_fallback:
                cursor = conn.cursor()
                sqlite_q = self._translate_query_for_sqlite(query)
                cursor.execute(sqlite_q, params or ())
                conn.commit()
                last_id = cursor.lastrowid
                row_count = cursor.rowcount
                cursor.close()
                return last_id if last_id else row_count
            else:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    conn.commit()
                    return cursor.lastrowid or cursor.rowcount
        finally:
            conn.close()

    def fetch_all(self, query: str, params: Union[Tuple, List, None] = None) -> List[Dict[str, Any]]:
        """Fetches all matching records as a list of dictionaries."""
        conn = self.get_connection()
        try:
            if self._using_sqlite_fallback:
                cursor = conn.cursor()
                sqlite_q = self._translate_query_for_sqlite(query)
                cursor.execute(sqlite_q, params or ())
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                cursor.close()
                return results
            else:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    return cursor.fetchall()
        finally:
            conn.close()

    def fetch_one(self, query: str, params: Union[Tuple, List, None] = None) -> Optional[Dict[str, Any]]:
        """Fetches a single record as a dictionary or None."""
        results = self.fetch_all(query, params)
        return results[0] if results else None

    def init_database(self):
        """Initializes tables and seeds basic demo data if database is empty."""
        if not self._using_sqlite_fallback:
            schema_file = BASE_DIR / "database" / "schema.sql"
            seed_file = BASE_DIR / "database" / "seed_data.sql"
            if schema_file.exists():
                self._run_sql_script_mysql(schema_file)
            # Check if students table has rows
            student_count = self.fetch_one("SELECT COUNT(*) AS count FROM students;")
            if student_count and student_count.get("count", 0) == 0 and seed_file.exists():
                self._run_sql_script_mysql(seed_file)
        else:
            self._init_sqlite_schema()

    def _run_sql_script_mysql(self, file_path: Path):
        """Executes a multi-statement MySQL SQL script."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove comments
        content = re.sub(r'--.*?\n', '\n', content)
        statements = content.split(";")
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt and not stmt.upper().startswith("USE ") and not stmt.upper().startswith("CREATE DATABASE"):
                        try:
                            cursor.execute(stmt)
                        except Exception as e:
                            # Log and proceed on non-fatal statement warnings
                            pass
                conn.commit()
        finally:
            conn.close()

    def _init_sqlite_schema(self):
        """Creates tables in SQLite corresponding to the MySQL schema."""
        conn = sqlite3.connect(self.sqlite_db_path)
        cursor = conn.cursor()
        
        # Create SQLite tables
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            program TEXT NOT NULL,
            semester INTEGER NOT NULL DEFAULT 1,
            section TEXT,
            batch TEXT,
            avatar_url TEXT,
            uims_username TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            token TEXT,
            cookies_json TEXT,
            is_active INTEGER DEFAULT 1,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS user_credentials (
            credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            uims_user_id TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            encryption_salt TEXT NOT NULL,
            is_remembered INTEGER DEFAULT 0,
            last_sync_at TIMESTAMP NULL,
            sync_status TEXT DEFAULT 'IDLE',
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS subjects (
            subject_code TEXT PRIMARY KEY,
            subject_name TEXT NOT NULL,
            credits REAL NOT NULL DEFAULT 3.0,
            semester INTEGER NOT NULL,
            faculty_name TEXT,
            subject_type TEXT DEFAULT 'Theory',
            min_attendance_pct REAL DEFAULT 75.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            total_delivered INTEGER NOT NULL DEFAULT 0,
            total_attended INTEGER NOT NULL DEFAULT 0,
            duty_leave INTEGER NOT NULL DEFAULT 0,
            medical_leave INTEGER NOT NULL DEFAULT 0,
            percentage REAL DEFAULT 0.00,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, subject_code),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS attendance_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            lecture_date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT NOT NULL,
            topic_covered TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            semester INTEGER NOT NULL,
            component_type TEXT NOT NULL,
            max_marks REAL NOT NULL,
            marks_obtained REAL NOT NULL,
            weightage_pct REAL DEFAULT 0.00,
            grade TEXT,
            recorded_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS semester_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            semester INTEGER NOT NULL,
            total_credits REAL NOT NULL,
            earned_credits REAL NOT NULL,
            sgpa REAL NOT NULL,
            cgpa REAL NOT NULL,
            status TEXT DEFAULT 'Passed',
            published_date TEXT,
            UNIQUE(student_id, semester),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS timetable (
            timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            room_no TEXT,
            faculty_name TEXT,
            is_lab INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            max_marks REAL DEFAULT 100.0,
            marks_awarded REAL NULL,
            submission_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_value REAL NOT NULL,
            current_value REAL NOT NULL DEFAULT 0.00,
            unit TEXT DEFAULT '',
            deadline TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS study_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            scheduled_date TEXT NOT NULL,
            start_time TEXT,
            duration_minutes INTEGER NOT NULL DEFAULT 60,
            topic TEXT NOT NULL,
            notes TEXT,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ai_analytics (
            analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            predicted_cgpa REAL,
            weak_subjects_json TEXT,
            shortage_risk_subjects_json TEXT,
            attendance_safe_skips_json TEXT,
            recommendations_json TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            category TEXT DEFAULT 'System',
            is_read INTEGER DEFAULT 0,
            action_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # Check if student exists
        cursor.execute("SELECT COUNT(*) FROM students;")
        count = cursor.fetchone()[0]
        if count == 0:
            self._seed_sqlite_demo_data(cursor)

        conn.commit()
        conn.close()

    def _seed_sqlite_demo_data(self, cursor: sqlite3.Cursor):
        """Seeds initial realistic student data into SQLite."""
        # 1. Student
        cursor.execute("""
            INSERT OR REPLACE INTO students (student_id, full_name, email, phone, program, semester, section, batch, uims_username)
            VALUES ('21BCS7492', 'Aarav Sharma', 'aarav.sharma@cuchd.in', '+91 98765 43210', 'B.E. Computer Science & Engineering', 5, 'CSE-04', '2023-2027', '21bcs7492');
        """)

        # 2. Subjects
        subjects = [
            ('21CS501', 'Design & Analysis of Algorithms', 4.0, 5, 'Dr. Rajesh Verma', 'Theory', 75.0),
            ('21CS502', 'Database Management Systems', 4.0, 5, 'Prof. Sunita Menon', 'Theory', 75.0),
            ('21CS503', 'Operating Systems & System Prog.', 4.0, 5, 'Dr. Amitav Ghosh', 'Theory', 75.0),
            ('21CS504', 'Machine Learning & AI Foundations', 3.0, 5, 'Dr. Neha Kulkarni', 'Theory', 75.0),
            ('21CS505', 'Computer Networks & Security', 3.0, 5, 'Prof. Vikram Chauhan', 'Theory', 75.0),
            ('21CSP51', 'DBMS Laboratory & Mini Project', 1.5, 5, 'Prof. Sunita Menon', 'Practical', 75.0),
            ('21CSP52', 'Algorithms & Coding Lab', 1.5, 5, 'Dr. Rajesh Verma', 'Practical', 75.0)
        ]
        cursor.executemany("""
            INSERT OR REPLACE INTO subjects (subject_code, subject_name, credits, semester, faculty_name, subject_type, min_attendance_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, subjects)

        # 3. Attendance
        # Notice 21CS504 has attendance below 75% for AI prediction testing
        attendance = [
            ('21BCS7492', '21CS501', 42, 36, 2, 0, 90.48),
            ('21BCS7492', '21CS502', 38, 32, 1, 0, 86.84),
            ('21BCS7492', '21CS503', 40, 31, 0, 0, 77.50),
            ('21BCS7492', '21CS504', 35, 23, 1, 0, 68.57),
            ('21BCS7492', '21CS505', 36, 29, 2, 0, 86.11),
            ('21BCS7492', '21CSP51', 14, 13, 0, 0, 92.86),
            ('21BCS7492', '21CSP52', 14, 12, 1, 0, 92.86)
        ]
        cursor.executemany("""
            INSERT OR REPLACE INTO attendance (student_id, subject_code, total_delivered, total_attended, duty_leave, medical_leave, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, attendance)

        # 4. Detailed Attendance Records
        records = [
            ('21BCS7492', '21CS501', '2026-11-02', '09:00 - 10:00', 'Present', 'Dynamic Programming - Bellman Ford'),
            ('21BCS7492', '21CS502', '2026-11-02', '10:00 - 11:00', 'Present', 'Query Optimization & B+ Trees'),
            ('21BCS7492', '21CS503', '2026-11-03', '11:15 - 12:15', 'Absent',  'Virtual Memory & Demand Paging'),
            ('21BCS7492', '21CS504', '2026-11-03', '13:00 - 14:00', 'Absent',  'Support Vector Machines (SVM)'),
            ('21BCS7492', '21CS505', '2026-11-04', '09:00 - 10:00', 'Present', 'TCP Flow & Congestion Control'),
            ('21BCS7492', '21CSP51', '2026-11-04', '14:00 - 16:00', 'Present', 'PL/SQL Triggers & Stored Procedures'),
            ('21BCS7492', '21CS504', '2026-11-05', '10:00 - 11:00', 'Duty Leave', 'Robotics Hackathon Participation'),
            ('21BCS7492', '21CS501', '2026-11-06', '09:00 - 10:00', 'Present', 'Greedy Techniques & Matroids'),
            ('21BCS7492', '21CS502', '2026-11-06', '11:15 - 12:15', 'Present', 'Concurrency Control & 2PL')
        ]
        cursor.executemany("""
            INSERT INTO attendance_records (student_id, subject_code, lecture_date, time_slot, status, topic_covered)
            VALUES (?, ?, ?, ?, ?, ?);
        """, records)

        # 5. Marks
        marks_data = [
            ('21BCS7492', '21CS501', 5, 'Internal_MST1', 30.0, 27.5, 20.0, 'A+', '2026-09-20'),
            ('21BCS7492', '21CS501', 5, 'Internal_MST2', 30.0, 28.0, 20.0, 'A+', '2026-10-25'),
            ('21BCS7492', '21CS501', 5, 'Assignment',    20.0, 19.0, 10.0, 'O',  '2026-10-15'),
            ('21BCS7492', '21CS502', 5, 'Internal_MST1', 30.0, 25.0, 20.0, 'A',  '2026-09-21'),
            ('21BCS7492', '21CS502', 5, 'Internal_MST2', 30.0, 26.5, 20.0, 'A+', '2026-10-26'),
            ('21BCS7492', '21CS502', 5, 'Assignment',    20.0, 18.0, 10.0, 'A+', '2026-10-16'),
            ('21BCS7492', '21CS503', 5, 'Internal_MST1', 30.0, 23.0, 20.0, 'B+', '2026-09-22'),
            ('21BCS7492', '21CS503', 5, 'Internal_MST2', 30.0, 24.0, 20.0, 'A',  '2026-10-27'),
            ('21BCS7492', '21CS503', 5, 'Assignment',    20.0, 17.0, 10.0, 'A',  '2026-10-17'),
            ('21BCS7492', '21CS504', 5, 'Internal_MST1', 30.0, 16.5, 20.0, 'C',  '2026-09-23'),
            ('21BCS7492', '21CS504', 5, 'Internal_MST2', 30.0, 18.0, 20.0, 'B',  '2026-10-28'),
            ('21BCS7492', '21CS504', 5, 'Assignment',    20.0, 14.0, 10.0, 'B',  '2026-10-18'),
            ('21BCS7492', '21CS505', 5, 'Internal_MST1', 30.0, 26.0, 20.0, 'A+', '2026-09-24'),
            ('21BCS7492', '21CS505', 5, 'Internal_MST2', 30.0, 25.5, 20.0, 'A',  '2026-10-29'),
            ('21BCS7492', '21CS505', 5, 'Assignment',    20.0, 19.5, 10.0, 'O',  '2026-10-19')
        ]
        cursor.executemany("""
            INSERT INTO marks (student_id, subject_code, semester, component_type, max_marks, marks_obtained, weightage_pct, grade, recorded_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, marks_data)

        # 6. Semester Results
        results = [
            ('21BCS7492', 1, 21.0, 21.0, 8.45, 8.45, 'Passed', '2024-01-15'),
            ('21BCS7492', 2, 22.5, 22.5, 8.70, 8.58, 'Passed', '2024-06-20'),
            ('21BCS7492', 3, 23.0, 23.0, 8.30, 8.48, 'Passed', '2025-01-18'),
            ('21BCS7492', 4, 22.0, 22.0, 8.85, 8.57, 'Passed', '2025-06-25')
        ]
        cursor.executemany("""
            INSERT OR REPLACE INTO semester_results (student_id, semester, total_credits, earned_credits, sgpa, cgpa, status, published_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, results)

        # 7. Timetable
        tt_entries = [
            ('21BCS7492', 'Monday', '09:00:00', '10:00:00', '21CS501', 'C-302', 'Dr. Rajesh Verma', 0),
            ('21BCS7492', 'Monday', '10:00:00', '11:00:00', '21CS502', 'C-302', 'Prof. Sunita Menon', 0),
            ('21BCS7492', 'Monday', '11:15:00', '12:15:00', '21CS503', 'C-302', 'Dr. Amitav Ghosh', 0),
            ('21BCS7492', 'Monday', '13:00:00', '15:00:00', '21CSP51', 'Lab-5', 'Prof. Sunita Menon', 1),
            ('21BCS7492', 'Tuesday', '09:00:00', '10:00:00', '21CS504', 'C-304', 'Dr. Neha Kulkarni', 0),
            ('21BCS7492', 'Tuesday', '10:00:00', '11:00:00', '21CS505', 'C-304', 'Prof. Vikram Chauhan', 0),
            ('21BCS7492', 'Tuesday', '11:15:00', '12:15:00', '21CS501', 'C-304', 'Dr. Rajesh Verma', 0),
            ('21BCS7492', 'Tuesday', '13:00:00', '15:00:00', '21CSP52', 'Lab-2', 'Dr. Rajesh Verma', 1),
            ('21BCS7492', 'Wednesday', '09:00:00', '10:00:00', '21CS503', 'C-302', 'Dr. Amitav Ghosh', 0),
            ('21BCS7492', 'Wednesday', '10:00:00', '11:00:00', '21CS502', 'C-302', 'Prof. Sunita Menon', 0),
            ('21BCS7492', 'Wednesday', '11:15:00', '12:15:00', '21CS505', 'C-302', 'Prof. Vikram Chauhan', 0),
            ('21BCS7492', 'Wednesday', '13:00:00', '14:00:00', '21CS504', 'C-302', 'Dr. Neha Kulkarni', 0),
            ('21BCS7492', 'Thursday', '09:00:00', '10:00:00', '21CS501', 'C-302', 'Dr. Rajesh Verma', 0),
            ('21BCS7492', 'Thursday', '10:00:00', '11:00:00', '21CS504', 'C-302', 'Dr. Neha Kulkarni', 0),
            ('21BCS7492', 'Thursday', '11:15:00', '12:15:00', '21CS503', 'C-302', 'Dr. Amitav Ghosh', 0),
            ('21BCS7492', 'Friday', '09:00:00', '10:00:00', '21CS505', 'C-302', 'Prof. Vikram Chauhan', 0),
            ('21BCS7492', 'Friday', '10:00:00', '11:00:00', '21CS502', 'C-302', 'Prof. Sunita Menon', 0),
            ('21BCS7492', 'Friday', '11:15:00', '12:15:00', '21CS501', 'C-302', 'Dr. Rajesh Verma', 0)
        ]
        cursor.executemany("""
            INSERT INTO timetable (student_id, day_of_week, start_time, end_time, subject_code, room_no, faculty_name, is_lab)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, tt_entries)

        # 8. Assignments
        assignments = [
            ('21BCS7492', '21CS504', 'Hyperparameter Tuning in SVM', 'Implement GridSearch and RandomSearch on the MNIST dataset and analyze accuracy curves.', '2026-11-12 23:59:00', 'Pending', 100.0, None),
            ('21BCS7492', '21CS502', 'E-Commerce Schema Normalization', 'Provide 3NF and BCNF decompositions for the given relational order catalog.', '2026-11-15 17:00:00', 'In Progress', 50.0, None),
            ('21BCS7492', '21CS501', 'Divide & Conquer Convex Hull', 'Algorithm formulation and test benchmark with randomized 2D coordinate clusters.', '2026-11-20 23:59:00', 'Pending', 50.0, None),
            ('21BCS7492', '21CS503', 'Custom Shell with Pipes & Redirection', 'Build a POSIX C shell supporting stdin/stdout redirection and concurrent pipelines.', '2026-10-30 23:59:00', 'Graded', 100.0, 94.0)
        ]
        cursor.executemany("""
            INSERT INTO assignments (student_id, subject_code, title, description, due_date, status, max_marks, marks_awarded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, assignments)

        # 9. Tasks
        tasks = [
            ('21BCS7492', 'Read SVM Kernels & Slack Variables in Bishop Book', 'Study', 'High', '2026-11-10', 0),
            ('21BCS7492', 'Prepare 10 Practice Problems for Dynamic Programming', 'Study', 'Medium', '2026-11-11', 0),
            ('21BCS7492', 'Submit ML Assignment 3 on Portal', 'Assignment', 'High', '2026-11-12', 0),
            ('21BCS7492', 'Review OS Chapter 8 (Deadlock Prevention & Banker Algorithm)', 'Exam', 'Medium', '2026-11-14', 0),
            ('21BCS7492', 'Attend IEEE Student Branch Tech Talk on Generative AI', 'General', 'Low', '2026-11-16', 1)
        ]
        cursor.executemany("""
            INSERT INTO tasks (student_id, title, category, priority, due_date, is_completed)
            VALUES (?, ?, ?, ?, ?, ?);
        """, tasks)

        # 10. Goals
        goals = [
            ('21BCS7492', 'Achieve Overall Semester 5 CGPA Target', 'Target_CGPA', 8.80, 8.57, 'GPA', '2026-12-30', 'Active'),
            ('21BCS7492', 'Restore Machine Learning Attendance above Threshold', 'Min_Attendance', 75.00, 68.57, '%', '2026-11-30', 'Active'),
            ('21BCS7492', 'Maintain 90%+ in Algorithms & DBMS', 'Min_Attendance', 90.00, 88.66, '%', '2026-12-15', 'Active'),
            ('21BCS7492', 'Complete 120 Weekly Study Hours across Semester', 'Study_Hours', 120.00, 84.50, 'Hours', '2026-12-20', 'Active')
        ]
        cursor.executemany("""
            INSERT INTO goals (student_id, title, target_type, target_value, current_value, unit, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, goals)

        # 11. Study Plans
        plans = [
            ('21BCS7492', '21CS504', '2026-11-09', '18:00:00', 90, 'SVM Kernels and Loss Function Derivations', 'Focus on Lagrange multipliers and dual problem.', 0),
            ('21BCS7492', '21CS501', '2026-11-10', '19:30:00', 60, 'Knapsack and Subset Sum DP formulation', 'Solve 3 LeetCode Mediums.', 0),
            ('21BCS7492', '21CS502', '2026-11-11', '17:00:00', 75, 'B+ Tree Splitting & Merge Algorithm', 'Diagram tree rebalancing cases.', 0)
        ]
        cursor.executemany("""
            INSERT INTO study_plans (student_id, subject_code, scheduled_date, start_time, duration_minutes, topic, notes, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, plans)

        # 12. Notifications
        notifs = [
            ('21BCS7492', 'Attendance Warning: Machine Learning', 'Your attendance in 21CS504 is 68.57%, which is below the mandatory 75% limit. You need to attend the next 9 consecutive lectures without missing any.', 'Attendance', 0),
            ('21BCS7492', 'Assignment Due Soon: SVM Tuning', 'Assignment "Hyperparameter Tuning in SVM" is due on Nov 12, 2026.', 'Assignment', 0),
            ('21BCS7492', 'Mid-Semester Exam Results Released', 'Internal MST2 marks for Algorithms, DBMS, and OS have been posted.', 'Exam', 1)
        ]
        cursor.executemany("""
            INSERT INTO notifications (student_id, title, message, category, is_read)
            VALUES (?, ?, ?, ?, ?);
        """, notifs)
