"""
Subject Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class Subject:
    subject_code: str
    subject_name: str
    credits: float = 3.0
    semester: int = 1
    faculty_name: Optional[str] = None
    subject_type: str = "Theory"
    min_attendance_pct: float = 75.00

    @classmethod
    def get_by_code(cls, subject_code: str) -> Optional['Subject']:
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM subjects WHERE subject_code = %s;", (subject_code,))
        if row:
            return cls(
                subject_code=row["subject_code"],
                subject_name=row["subject_name"],
                credits=float(row.get("credits", 3.0)),
                semester=int(row.get("semester", 1)),
                faculty_name=row.get("faculty_name"),
                subject_type=row.get("subject_type", "Theory"),
                min_attendance_pct=float(row.get("min_attendance_pct", 75.0))
            )
        return None

    @classmethod
    def get_all(cls, semester: Optional[int] = None) -> List['Subject']:
        db = DatabaseManager()
        if semester:
            rows = db.fetch_all("SELECT * FROM subjects WHERE semester = %s ORDER BY subject_code;", (semester,))
        else:
            rows = db.fetch_all("SELECT * FROM subjects ORDER BY semester, subject_code;")
        return [
            cls(
                subject_code=r["subject_code"],
                subject_name=r["subject_name"],
                credits=float(r.get("credits", 3.0)),
                semester=int(r.get("semester", 1)),
                faculty_name=r.get("faculty_name"),
                subject_type=r.get("subject_type", "Theory"),
                min_attendance_pct=float(r.get("min_attendance_pct", 75.0))
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        existing = db.fetch_one("SELECT subject_code FROM subjects WHERE subject_code = %s;", (self.subject_code,))
        if existing:
            query = """
                UPDATE subjects SET
                    subject_name = %s, credits = %s, semester = %s,
                    faculty_name = %s, subject_type = %s, min_attendance_pct = %s
                WHERE subject_code = %s;
            """
            db.execute_update(query, (
                self.subject_name, self.credits, self.semester,
                self.faculty_name, self.subject_type, self.min_attendance_pct,
                self.subject_code
            ))
        else:
            query = """
                INSERT INTO subjects (subject_code, subject_name, credits, semester, faculty_name, subject_type, min_attendance_pct)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            db.execute_update(query, (
                self.subject_code, self.subject_name, self.credits, self.semester,
                self.faculty_name, self.subject_type, self.min_attendance_pct
            ))
        return True
