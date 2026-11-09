"""
StudyPlan Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class StudyPlan:
    plan_id: Optional[int]
    student_id: str
    subject_code: str
    subject_name: str
    scheduled_date: str
    start_time: Optional[str]
    duration_minutes: int = 60
    topic: str = ""
    notes: Optional[str] = None
    is_completed: bool = False

    @classmethod
    def get_for_student(cls, student_id: str) -> List['StudyPlan']:
        db = DatabaseManager()
        query = """
            SELECT p.*, s.subject_name
            FROM study_plans p
            JOIN subjects s ON p.subject_code = s.subject_code
            WHERE p.student_id = %s
            ORDER BY p.scheduled_date ASC, p.start_time ASC;
        """
        rows = db.fetch_all(query, (student_id,))
        return [
            cls(
                plan_id=r.get("plan_id"),
                student_id=r["student_id"],
                subject_code=r["subject_code"],
                subject_name=r.get("subject_name", r["subject_code"]),
                scheduled_date=str(r["scheduled_date"]),
                start_time=str(r["start_time"]) if r.get("start_time") else None,
                duration_minutes=int(r.get("duration_minutes", 60)),
                topic=r.get("topic", ""),
                notes=r.get("notes"),
                is_completed=bool(r.get("is_completed", 0))
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        if self.plan_id:
            query = """
                UPDATE study_plans SET
                    subject_code = %s, scheduled_date = %s, start_time = %s,
                    duration_minutes = %s, topic = %s, notes = %s, is_completed = %s
                WHERE plan_id = %s;
            """
            db.execute_update(query, (
                self.subject_code, self.scheduled_date, self.start_time,
                self.duration_minutes, self.topic, self.notes,
                1 if self.is_completed else 0, self.plan_id
            ))
        else:
            query = """
                INSERT INTO study_plans (student_id, subject_code, scheduled_date, start_time, duration_minutes, topic, notes, is_completed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.plan_id = db.execute_update(query, (
                self.student_id, self.subject_code, self.scheduled_date, self.start_time,
                self.duration_minutes, self.topic, self.notes, 1 if self.is_completed else 0
            ))
        return True
