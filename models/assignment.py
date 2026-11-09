"""
Assignment Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class Assignment:
    assignment_id: Optional[int]
    student_id: str
    subject_code: str
    subject_name: str
    title: str
    description: Optional[str]
    due_date: str
    status: str = "Pending"  # 'Pending', 'In Progress', 'Submitted', 'Graded'
    max_marks: float = 100.0
    marks_awarded: Optional[float] = None
    submission_notes: Optional[str] = None

    @classmethod
    def get_for_student(cls, student_id: str, status_filter: Optional[str] = None) -> List['Assignment']:
        db = DatabaseManager()
        if status_filter:
            query = """
                SELECT a.*, s.subject_name
                FROM assignments a
                JOIN subjects s ON a.subject_code = s.subject_code
                WHERE a.student_id = %s AND a.status = %s
                ORDER BY a.due_date ASC;
            """
            rows = db.fetch_all(query, (student_id, status_filter))
        else:
            query = """
                SELECT a.*, s.subject_name
                FROM assignments a
                JOIN subjects s ON a.subject_code = s.subject_code
                WHERE a.student_id = %s
                ORDER BY a.due_date ASC;
            """
            rows = db.fetch_all(query, (student_id,))

        return [
            cls(
                assignment_id=r.get("assignment_id"),
                student_id=r["student_id"],
                subject_code=r["subject_code"],
                subject_name=r.get("subject_name", r["subject_code"]),
                title=r["title"],
                description=r.get("description"),
                due_date=str(r["due_date"]),
                status=r.get("status", "Pending"),
                max_marks=float(r.get("max_marks", 100.0)),
                marks_awarded=float(r["marks_awarded"]) if r.get("marks_awarded") is not None else None,
                submission_notes=r.get("submission_notes")
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        if self.assignment_id:
            query = """
                UPDATE assignments SET
                    subject_code = %s, title = %s, description = %s,
                    due_date = %s, status = %s, max_marks = %s,
                    marks_awarded = %s, submission_notes = %s
                WHERE assignment_id = %s;
            """
            db.execute_update(query, (
                self.subject_code, self.title, self.description,
                self.due_date, self.status, self.max_marks,
                self.marks_awarded, self.submission_notes, self.assignment_id
            ))
        else:
            query = """
                INSERT INTO assignments (student_id, subject_code, title, description, due_date, status, max_marks, marks_awarded, submission_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.assignment_id = db.execute_update(query, (
                self.student_id, self.subject_code, self.title, self.description,
                self.due_date, self.status, self.max_marks, self.marks_awarded, self.submission_notes
            ))
        return True
