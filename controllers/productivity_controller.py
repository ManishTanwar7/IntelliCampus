"""
IntelliCampus: Productivity Controller
Coordinates Assignments, Tasks, Goals, and Study Plans.
"""
from typing import List, Optional, Dict, Any
from models.assignment import Assignment
from models.task import Task
from models.goal import Goal
from models.study_plan import StudyPlan

class ProductivityController:

    # --- Assignments ---
    @classmethod
    def get_assignments(cls, student_id: str, status_filter: Optional[str] = None) -> List[Assignment]:
        return Assignment.get_for_student(student_id, status_filter)

    @classmethod
    def create_assignment(cls, student_id: str, subject_code: str, title: str, description: str, due_date: str, max_marks: float = 100.0) -> Assignment:
        asg = Assignment(
            assignment_id=None,
            student_id=student_id,
            subject_code=subject_code,
            subject_name="",
            title=title,
            description=description,
            due_date=due_date,
            status="Pending",
            max_marks=max_marks
        )
        asg.save()
        return asg

    @classmethod
    def update_assignment_status(cls, assignment_id: int, new_status: str) -> bool:
        from services.database import DatabaseManager
        db = DatabaseManager()
        db.execute_update("UPDATE assignments SET status = %s WHERE assignment_id = %s;", (new_status, assignment_id))
        return True

    # --- Tasks ---
    @classmethod
    def get_tasks(cls, student_id: str, completed_filter: Optional[bool] = None) -> List[Task]:
        return Task.get_for_student(student_id, completed_filter)

    @classmethod
    def add_task(cls, student_id: str, title: str, category: str = "General", priority: str = "Medium", due_date: Optional[str] = None) -> Task:
        t = Task(
            task_id=None,
            student_id=student_id,
            title=title,
            category=category,
            priority=priority,
            due_date=due_date,
            is_completed=False
        )
        t.save()
        return t

    @classmethod
    def toggle_task_completion(cls, task_id: int, completed: bool):
        from services.database import DatabaseManager
        db = DatabaseManager()
        db.execute_update("UPDATE tasks SET is_completed = %s WHERE task_id = %s;", (1 if completed else 0, task_id))

    # --- Goals ---
    @classmethod
    def get_goals(cls, student_id: str) -> List[Goal]:
        return Goal.get_for_student(student_id)

    @classmethod
    def add_goal(cls, student_id: str, title: str, target_type: str, target_value: float, current_value: float, unit: str, deadline: str) -> Goal:
        g = Goal(
            goal_id=None,
            student_id=student_id,
            title=title,
            target_type=target_type,
            target_value=target_value,
            current_value=current_value,
            unit=unit,
            deadline=deadline,
            status="Active"
        )
        g.save()
        return g

    # --- Study Plans ---
    @classmethod
    def get_study_plans(cls, student_id: str) -> List[StudyPlan]:
        return StudyPlan.get_for_student(student_id)

    @classmethod
    def add_study_plan(cls, student_id: str, subject_code: str, scheduled_date: str, start_time: str, duration_minutes: int, topic: str, notes: str) -> StudyPlan:
        plan = StudyPlan(
            plan_id=None,
            student_id=student_id,
            subject_code=subject_code,
            subject_name="",
            scheduled_date=scheduled_date,
            start_time=start_time,
            duration_minutes=duration_minutes,
            topic=topic,
            notes=notes,
            is_completed=False
        )
        plan.save()
        return plan
