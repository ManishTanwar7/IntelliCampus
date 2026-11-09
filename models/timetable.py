"""
Timetable Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class TimetableEntry:
    timetable_id: Optional[int]
    student_id: str
    day_of_week: str
    start_time: str
    end_time: str
    subject_code: str
    subject_name: str
    room_no: Optional[str] = None
    faculty_name: Optional[str] = None
    is_lab: bool = False

    @property
    def formatted_time(self) -> str:
        s = str(self.start_time)[:5]
        e = str(self.end_time)[:5]
        return f"{s} - {e}"

    @classmethod
    def get_for_student(cls, student_id: str, day: Optional[str] = None) -> List['TimetableEntry']:
        db = DatabaseManager()
        if day:
            query = """
                SELECT t.*, s.subject_name
                FROM timetable t
                JOIN subjects s ON t.subject_code = s.subject_code
                WHERE t.student_id = %s AND t.day_of_week = %s
                ORDER BY t.start_time ASC;
            """
            rows = db.fetch_all(query, (student_id, day))
        else:
            query = """
                SELECT t.*, s.subject_name
                FROM timetable t
                JOIN subjects s ON t.subject_code = s.subject_code
                WHERE t.student_id = %s
                ORDER BY 
                    CASE t.day_of_week
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        ELSE 7
                    END,
                    t.start_time ASC;
            """
            rows = db.fetch_all(query, (student_id,))

        return [
            cls(
                timetable_id=r.get("timetable_id"),
                student_id=r["student_id"],
                day_of_week=r["day_of_week"],
                start_time=str(r["start_time"]),
                end_time=str(r["end_time"]),
                subject_code=r["subject_code"],
                subject_name=r.get("subject_name", r["subject_code"]),
                room_no=r.get("room_no"),
                faculty_name=r.get("faculty_name"),
                is_lab=bool(r.get("is_lab", 0))
            ) for r in rows
        ]

    def save(self) -> bool:
        db = DatabaseManager()
        if self.timetable_id:
            query = """
                UPDATE timetable SET
                    day_of_week = %s, start_time = %s, end_time = %s,
                    subject_code = %s, room_no = %s, faculty_name = %s, is_lab = %s
                WHERE timetable_id = %s;
            """
            db.execute_update(query, (
                self.day_of_week, self.start_time, self.end_time,
                self.subject_code, self.room_no, self.faculty_name, 1 if self.is_lab else 0,
                self.timetable_id
            ))
        else:
            query = """
                INSERT INTO timetable (student_id, day_of_week, start_time, end_time, subject_code, room_no, faculty_name, is_lab)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            self.timetable_id = db.execute_update(query, (
                self.student_id, self.day_of_week, self.start_time, self.end_time,
                self.subject_code, self.room_no, self.faculty_name, 1 if self.is_lab else 0
            ))
        return True
