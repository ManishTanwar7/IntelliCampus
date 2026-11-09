"""
Goal Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class Goal:
    goal_id: Optional[int]
    student_id: str
    title: str
    target_type: str  # 'Target_CGPA', 'Min_Attendance', 'Subject_Grade', 'Study_Hours', 'Custom'
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    deadline: Optional[str] = None
    status: str = "Active"  # 'Active', 'Achieved', 'Missed'

    @property
    def progress_percentage(self) -> float:
        if self.target_value <= 0:
            return 100.0 if self.current_value >= self.target_value else 0.0
        pct = (self.current_value / self.target_value) * 100.0
        return min(100.0, round(pct, 1))

    @classmethod
    def get_for_student(cls, student_id: str) -> List['Goal']:
        db = DatabaseManager()
        rows = db.fetch_all("SELECT * FROM goals WHERE student_id = %s ORDER BY deadline ASC;", (student_id,))
        return [
            cls(
                goal_id=r.get("goal_id"),
                student_id=r["student_id"],
                title=r["title"],
                target_type=r["target_type"],
                target_value=float(r.get("target_value", 0.0)),
                current_value=float(r.get("current_value", 0.0)),
                unit=r.get("unit", ""),
                deadline=str(r["deadline"]) if r.get("deadline") else None,
                status=r.get("status", "Active")
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        if self.goal_id:
            query = """
                UPDATE goals SET
                    title = %s, target_type = %s, target_value = %s,
                    current_value = %s, unit = %s, deadline = %s, status = %s
                WHERE goal_id = %s;
            """
            db.execute_update(query, (
                self.title, self.target_type, self.target_value,
                self.current_value, self.unit, self.deadline, self.status, self.goal_id
            ))
        else:
            query = """
                INSERT INTO goals (student_id, title, target_type, target_value, current_value, unit, deadline, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.goal_id = db.execute_update(query, (
                self.student_id, self.title, self.target_type, self.target_value,
                self.current_value, self.unit, self.deadline, self.status
            ))
        return True
