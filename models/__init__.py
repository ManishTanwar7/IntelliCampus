"""
IntelliCampus: Models Package
Contains domain entities and object-relational mappings adhering to OOP principles.
"""
from models.student import Student
from models.subject import Subject
from models.attendance import AttendanceRecord, SubjectAttendance
from models.marks import MarkItem, SemesterResult
from models.timetable import TimetableEntry
from models.assignment import Assignment
from models.task import Task
from models.goal import Goal
from models.study_plan import StudyPlan
from models.session import UserSession, UserCredential
from models.analytics import AnalyticsReport

__all__ = [
    "Student", "Subject", "AttendanceRecord", "SubjectAttendance",
    "MarkItem", "SemesterResult", "TimetableEntry", "Assignment",
    "Task", "Goal", "StudyPlan", "UserSession", "UserCredential",
    "AnalyticsReport"
]
