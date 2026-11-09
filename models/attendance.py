"""
Attendance Model
"""
import math
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class SubjectAttendance:
    attendance_id: Optional[int]
    student_id: str
    subject_code: str
    subject_name: str
    total_delivered: int
    total_attended: int
    duty_leave: int = 0
    medical_leave: int = 0
    percentage: float = 0.0

    @property
    def effective_attended(self) -> int:
        return self.total_attended + self.duty_leave + self.medical_leave

    @property
    def calculated_percentage(self) -> float:
        if self.total_delivered == 0:
            return 100.0
        return round((self.effective_attended * 100.0) / self.total_delivered, 2)

    def safe_skips(self, target_pct: float = 75.0) -> int:
        """
        Calculates how many upcoming classes can be safely skipped while staying >= target_pct.
        Formula: floor((effective_attended / (target_pct / 100)) - delivered)
        """
        if self.calculated_percentage < target_pct or self.total_delivered == 0:
            return 0
        target_ratio = target_pct / 100.0
        skips = math.floor((self.effective_attended / target_ratio) - self.total_delivered)
        return max(0, skips)

    def lectures_needed(self, target_pct: float = 75.0) -> int:
        """
        Calculates consecutive classes to attend to reach target_pct when in shortage.
        Formula: ceil((target_pct * delivered - 100 * effective_attended) / (100 - target_pct))
        """
        if self.calculated_percentage >= target_pct:
            return 0
        target_ratio = target_pct / 100.0
        if target_ratio >= 1.0:
            return 999
        needed = math.ceil((target_ratio * self.total_delivered - self.effective_attended) / (1.0 - target_ratio))
        return max(0, needed)

    @classmethod
    def get_for_student(cls, student_id: str) -> List['SubjectAttendance']:
        db = DatabaseManager()
        query = """
            SELECT 
                a.attendance_id, a.student_id, a.subject_code,
                s.subject_name, a.total_delivered, a.total_attended,
                a.duty_leave, a.medical_leave, a.percentage
            FROM attendance a
            JOIN subjects s ON a.subject_code = s.subject_code
            WHERE a.student_id = %s
            ORDER BY a.subject_code;
        """
        rows = db.fetch_all(query, (student_id,))
        results = []
        for r in rows:
            obj = cls(
                attendance_id=r.get("attendance_id"),
                student_id=r["student_id"],
                subject_code=r["subject_code"],
                subject_name=r.get("subject_name", r["subject_code"]),
                total_delivered=int(r.get("total_delivered", 0)),
                total_attended=int(r.get("total_attended", 0)),
                duty_leave=int(r.get("duty_leave", 0)),
                medical_leave=int(r.get("medical_leave", 0)),
                percentage=float(r.get("percentage", 0.0))
            )
            obj.percentage = obj.calculated_percentage
            results.append(obj)
        return results

    def save(self) -> bool:
        db = DatabaseManager()
        self.percentage = self.calculated_percentage
        existing = db.fetch_one(
            "SELECT attendance_id FROM attendance WHERE student_id = %s AND subject_code = %s;",
            (self.student_id, self.subject_code)
        )
        if existing:
            query = """
                UPDATE attendance SET
                    total_delivered = %s, total_attended = %s,
                    duty_leave = %s, medical_leave = %s, percentage = %s
                WHERE student_id = %s AND subject_code = %s;
            """
            db.execute_update(query, (
                self.total_delivered, self.total_attended,
                self.duty_leave, self.medical_leave, self.percentage,
                self.student_id, self.subject_code
            ))
        else:
            query = """
                INSERT INTO attendance (student_id, subject_code, total_delivered, total_attended, duty_leave, medical_leave, percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            db.execute_update(query, (
                self.student_id, self.subject_code, self.total_delivered,
                self.total_attended, self.duty_leave, self.medical_leave, self.percentage
            ))
        return True


@dataclass
class AttendanceRecord:
    record_id: Optional[int]
    student_id: str
    subject_code: str
    subject_name: str
    lecture_date: str
    time_slot: str
    status: str
    topic_covered: Optional[str] = None

    @classmethod
    def get_history(cls, student_id: str, limit: int = 50) -> List['AttendanceRecord']:
        db = DatabaseManager()
        query = """
            SELECT r.*, s.subject_name
            FROM attendance_records r
            JOIN subjects s ON r.subject_code = s.subject_code
            WHERE r.student_id = %s
            ORDER BY r.lecture_date DESC, r.time_slot DESC
            LIMIT %s;
        """
        rows = db.fetch_all(query, (student_id, limit))
        return [
            cls(
                record_id=r.get("record_id"),
                student_id=r["student_id"],
                subject_code=r["subject_code"],
                subject_name=r.get("subject_name", r["subject_code"]),
                lecture_date=str(r.get("lecture_date")),
                time_slot=str(r.get("time_slot")),
                status=str(r.get("status")),
                topic_covered=r.get("topic_covered")
            ) for r in rows
        ]
