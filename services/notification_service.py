"""
IntelliCampus: Notification Service
Manages real-time alerts, academic triggers, and notification center status.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from services.database import DatabaseManager
from models.attendance import SubjectAttendance
from models.assignment import Assignment

class NotificationService:

    @classmethod
    def get_unread_count(cls, student_id: str) -> int:
        db = DatabaseManager()
        row = db.fetch_one("SELECT COUNT(*) AS count FROM notifications WHERE student_id = %s AND is_read = 0;", (student_id,))
        return int(row["count"]) if row else 0

    @classmethod
    def get_notifications(cls, student_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        db = DatabaseManager()
        query = """
            SELECT * FROM notifications
            WHERE student_id = %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        return db.fetch_all(query, (student_id, limit))

    @classmethod
    def add_notification(cls, student_id: str, title: str, message: str, category: str = "System", action_url: Optional[str] = None) -> int:
        db = DatabaseManager()
        # Avoid duplicate alerts for same title within today
        today = datetime.now().strftime("%Y-%m-%d")
        existing = db.fetch_one(
            "SELECT notification_id FROM notifications WHERE student_id = %s AND title = %s AND DATE(created_at) = %s;",
            (student_id, title, today)
        )
        if existing:
            return existing["notification_id"]

        query = """
            INSERT INTO notifications (student_id, title, message, category, action_url, is_read)
            VALUES (%s, %s, %s, %s, %s, 0);
        """
        return db.execute_update(query, (student_id, title, message, category, action_url))

    @classmethod
    def mark_as_read(cls, notification_id: int):
        db = DatabaseManager()
        db.execute_update("UPDATE notifications SET is_read = 1 WHERE notification_id = %s;", (notification_id,))

    @classmethod
    def mark_all_as_read(cls, student_id: str):
        db = DatabaseManager()
        db.execute_update("UPDATE notifications SET is_read = 1 WHERE student_id = %s;", (student_id,))

    @classmethod
    def run_system_health_checks(cls, student_id: str):
        """Scans for attendance shortages, impending assignment deadlines, etc."""
        # 1. Attendance checks
        att_list = SubjectAttendance.get_for_student(student_id)
        for att in att_list:
            if att.calculated_percentage < 75.0:
                needed = att.lectures_needed(75.0)
                cls.add_notification(
                    student_id=student_id,
                    title=f"Attendance Shortage Alert: {att.subject_code}",
                    message=f"Attendance in {att.subject_name} is currently {att.calculated_percentage}%. Attend next {needed} lectures consecutively to clear shortage.",
                    category="Attendance"
                )

        # 2. Assignment deadlines
        assignments = Assignment.get_for_student(student_id, status_filter="Pending")
        now = datetime.now()
        for a in assignments:
            try:
                due_dt = datetime.fromisoformat(str(a.due_date))
                time_diff = due_dt - now
                if timedelta(hours=0) < time_diff <= timedelta(hours=48):
                    cls.add_notification(
                        student_id=student_id,
                        title=f"Assignment Due Soon: {a.title}",
                        message=f"'{a.title}' for {a.subject_name} is due in {round(time_diff.total_seconds() / 3600, 1)} hours.",
                        category="Assignment"
                    )
            except Exception:
                pass
