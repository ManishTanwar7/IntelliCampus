"""
Task Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class Task:
    task_id: Optional[int]
    student_id: str
    title: str
    category: str = "General"  # 'Study', 'Assignment', 'Exam', 'Project', 'General'
    priority: str = "Medium"   # 'High', 'Medium', 'Low'
    due_date: Optional[str] = None
    is_completed: bool = False

    @classmethod
    def get_for_student(cls, student_id: str, completed_filter: Optional[bool] = None) -> List['Task']:
        db = DatabaseManager()
        if completed_filter is not None:
            query = """
                SELECT * FROM tasks
                WHERE student_id = %s AND is_completed = %s
                ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, due_date ASC;
            """
            rows = db.fetch_all(query, (student_id, 1 if completed_filter else 0))
        else:
            query = """
                SELECT * FROM tasks
                WHERE student_id = %s
                ORDER BY is_completed ASC, CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, due_date ASC;
            """
            rows = db.fetch_all(query, (student_id,))

        return [
            cls(
                task_id=r.get("task_id"),
                student_id=r["student_id"],
                title=r["title"],
                category=r.get("category", "General"),
                priority=r.get("priority", "Medium"),
                due_date=str(r["due_date"]) if r.get("due_date") else None,
                is_completed=bool(r.get("is_completed", 0))
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        if self.task_id:
            query = """
                UPDATE tasks SET
                    title = %s, category = %s, priority = %s, due_date = %s, is_completed = %s
                WHERE task_id = %s;
            """
            db.execute_update(query, (
                self.title, self.category, self.priority, self.due_date,
                1 if self.is_completed else 0, self.task_id
            ))
        else:
            query = """
                INSERT INTO tasks (student_id, title, category, priority, due_date, is_completed)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            self.task_id = db.execute_update(query, (
                self.student_id, self.title, self.category, self.priority,
                self.due_date, 1 if self.is_completed else 0
            ))
        return True
