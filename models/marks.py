"""
Marks and Semester Results Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class MarkItem:
    mark_id: Optional[int]
    student_id: str
    subject_code: str
    subject_name: str
    semester: int
    component_type: str
    max_marks: float
    marks_obtained: float
    weightage_pct: float = 0.0
    grade: Optional[str] = None
    recorded_date: Optional[str] = None

    @property
    def percentage(self) -> float:
        if self.max_marks <= 0:
            return 0.0
        return round((self.marks_obtained / self.max_marks) * 100.0, 2)

    @classmethod
    def get_for_student(cls, student_id: str, semester: Optional[int] = None) -> List['MarkItem']:
        db = DatabaseManager()
        if semester:
            query = """
                SELECT m.*, s.subject_name
                FROM marks m
                JOIN subjects s ON m.subject_code = s.subject_code
                WHERE m.student_id = %s AND m.semester = %s
                ORDER BY m.subject_code, m.component_type;
            """
            rows = db.fetch_all(query, (student_id, semester))
        else:
            query = """
                SELECT m.*, s.subject_name
                FROM marks m
                JOIN subjects s ON m.subject_code = s.subject_code
                WHERE m.student_id = %s
                ORDER BY m.semester DESC, m.subject_code, m.component_type;
            """
            rows = db.fetch_all(query, (student_id,))
            
        return [
            cls(
                mark_id=r.get("mark_id"),
                student_id=r["student_id"],
                subject_code=r["subject_code"],
                subject_name=r.get("subject_name", r["subject_code"]),
                semester=int(r.get("semester", 1)),
                component_type=r["component_type"],
                max_marks=float(r.get("max_marks", 100.0)),
                marks_obtained=float(r.get("marks_obtained", 0.0)),
                weightage_pct=float(r.get("weightage_pct", 0.0)),
                grade=r.get("grade"),
                recorded_date=str(r.get("recorded_date")) if r.get("recorded_date") else None
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        if self.mark_id:
            query = """
                UPDATE marks SET
                    marks_obtained = %s, max_marks = %s, weightage_pct = %s, grade = %s
                WHERE mark_id = %s;
            """
            db.execute_update(query, (self.marks_obtained, self.max_marks, self.weightage_pct, self.grade, self.mark_id))
        else:
            query = """
                INSERT INTO marks (student_id, subject_code, semester, component_type, max_marks, marks_obtained, weightage_pct, grade, recorded_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.mark_id = db.execute_update(query, (
                self.student_id, self.subject_code, self.semester, self.component_type,
                self.max_marks, self.marks_obtained, self.weightage_pct, self.grade, self.recorded_date
            ))
        return True


@dataclass
class SemesterResult:
    result_id: Optional[int]
    student_id: str
    semester: int
    total_credits: float
    earned_credits: float
    sgpa: float
    cgpa: float
    status: str = "Passed"
    published_date: Optional[str] = None

    @classmethod
    def get_for_student(cls, student_id: str) -> List['SemesterResult']:
        db = DatabaseManager()
        query = """
            SELECT * FROM semester_results
            WHERE student_id = %s
            ORDER BY semester ASC;
        """
        rows = db.fetch_all(query, (student_id,))
        return [
            cls(
                result_id=r.get("result_id"),
                student_id=r["student_id"],
                semester=int(r["semester"]),
                total_credits=float(r.get("total_credits", 0.0)),
                earned_credits=float(r.get("earned_credits", 0.0)),
                sgpa=float(r.get("sgpa", 0.0)),
                cgpa=float(r.get("cgpa", 0.0)),
                status=r.get("status", "Passed"),
                published_date=str(r.get("published_date")) if r.get("published_date") else None
            ) for r in rows
        ]

    @classmethod
    def get_current_cgpa(cls, student_id: str) -> float:
        history = cls.get_for_student(student_id)
        if history:
            return history[-1].cgpa
        return 0.0
