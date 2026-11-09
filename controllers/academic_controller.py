"""
IntelliCampus: Academic Controller
Coordinates Attendance, Marks, Results, and Timetable logic.
"""
from typing import List, Dict, Any, Optional
from models.attendance import SubjectAttendance, AttendanceRecord
from models.marks import MarkItem, SemesterResult
from models.subject import Subject
from models.timetable import TimetableEntry

class AcademicController:

    @classmethod
    def get_attendance_overview(cls, student_id: str) -> Dict[str, Any]:
        """Calculates global attendance percentage, safe skips, and shortage count."""
        records = SubjectAttendance.get_for_student(student_id)
        if not records:
            return {
                "overall_percentage": 0.0,
                "total_delivered": 0,
                "total_attended": 0,
                "shortage_count": 0,
                "subjects": []
            }

        total_delivered = sum(r.total_delivered for r in records)
        total_effective = sum(r.effective_attended for r in records)
        overall_pct = round((total_effective * 100.0) / total_delivered, 2) if total_delivered > 0 else 0.0
        shortage_count = sum(1 for r in records if r.calculated_percentage < 75.0)

        return {
            "overall_percentage": overall_pct,
            "total_delivered": total_delivered,
            "total_attended": total_effective,
            "shortage_count": shortage_count,
            "subjects": records
        }

    @classmethod
    def get_subject_attendance(cls, student_id: str) -> List[SubjectAttendance]:
        return SubjectAttendance.get_for_student(student_id)

    @classmethod
    def get_attendance_logs(cls, student_id: str, limit: int = 50) -> List[AttendanceRecord]:
        return AttendanceRecord.get_history(student_id, limit)

    @classmethod
    def get_marks_by_semester(cls, student_id: str, semester: Optional[int] = None) -> List[MarkItem]:
        return MarkItem.get_for_student(student_id, semester)

    @classmethod
    def get_semester_results(cls, student_id: str) -> List[SemesterResult]:
        return SemesterResult.get_for_student(student_id)

    @classmethod
    def get_timetable(cls, student_id: str, day: Optional[str] = None) -> List[TimetableEntry]:
        return TimetableEntry.get_for_student(student_id, day)

    @classmethod
    def get_all_subjects(cls) -> List[Subject]:
        return Subject.get_all()
