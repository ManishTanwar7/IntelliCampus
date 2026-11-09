"""
Student Model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from services.database import DatabaseManager

@dataclass
class Student:
    student_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    program: str = "B.E. Computer Science & Engineering"
    semester: int = 1
    section: Optional[str] = None
    batch: Optional[str] = None
    avatar_url: Optional[str] = None
    uims_username: Optional[str] = None

    @classmethod
    def get_by_id(cls, student_id: str) -> Optional['Student']:
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM students WHERE student_id = %s;", (student_id,))
        if row:
            return cls(
                student_id=row["student_id"],
                full_name=row["full_name"],
                email=row["email"],
                phone=row.get("phone"),
                program=row.get("program", "B.E. Computer Science"),
                semester=int(row.get("semester", 1)),
                section=row.get("section"),
                batch=row.get("batch"),
                avatar_url=row.get("avatar_url"),
                uims_username=row.get("uims_username")
            )
        return None

    @classmethod
    def search(cls, query: str) -> Optional['Student']:
        db = DatabaseManager()
        q = f"%{query.strip().lower()}%"
        row = db.fetch_one("""
            SELECT * FROM students 
            WHERE LOWER(student_id) LIKE %s 
               OR LOWER(full_name) LIKE %s 
               OR LOWER(uims_username) LIKE %s 
            LIMIT 1;
        """, (q, q, q))
        if row:
            return cls(
                student_id=row["student_id"],
                full_name=row["full_name"],
                email=row["email"],
                phone=row.get("phone"),
                program=row.get("program", "B.E. Computer Science"),
                semester=int(row.get("semester", 1)),
                section=row.get("section"),
                batch=row.get("batch"),
                avatar_url=row.get("avatar_url"),
                uims_username=row.get("uims_username")
            )
        return None

    @classmethod
    def get_all(cls) -> List['Student']:
        db = DatabaseManager()
        rows = db.fetch_all("SELECT * FROM students ORDER BY student_id;")
        return [
            cls(
                student_id=r["student_id"],
                full_name=r["full_name"],
                email=r["email"],
                phone=r.get("phone"),
                program=r.get("program", "B.E. Computer Science"),
                semester=int(r.get("semester", 1)),
                section=r.get("section"),
                batch=r.get("batch"),
                avatar_url=r.get("avatar_url"),
                uims_username=r.get("uims_username")
            ) for r in rows
        ]

    @classmethod
    def get_first_or_default(cls) -> Optional['Student']:
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM students LIMIT 1;")
        if row:
            return cls(
                student_id=row["student_id"],
                full_name=row["full_name"],
                email=row["email"],
                phone=row.get("phone"),
                program=row.get("program", "B.E. Computer Science"),
                semester=int(row.get("semester", 1)),
                section=row.get("section"),
                batch=row.get("batch"),
                avatar_url=row.get("avatar_url"),
                uims_username=row.get("uims_username")
            )
        return None

    def save(self) -> bool:
        db = DatabaseManager()
        existing = db.fetch_one("SELECT student_id FROM students WHERE student_id = %s;", (self.student_id,))
        if existing:
            query = """
                UPDATE students SET
                    full_name = %s, email = %s, phone = %s, program = %s,
                    semester = %s, section = %s, batch = %s, avatar_url = %s, uims_username = %s
                WHERE student_id = %s;
            """
            db.execute_update(query, (
                self.full_name, self.email, self.phone, self.program,
                self.semester, self.section, self.batch, self.avatar_url, self.uims_username,
                self.student_id
            ))
        else:
            query = """
                INSERT INTO students (student_id, full_name, email, phone, program, semester, section, batch, avatar_url, uims_username)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            db.execute_update(query, (
                self.student_id, self.full_name, self.email, self.phone, self.program,
                self.semester, self.section, self.batch, self.avatar_url, self.uims_username
            ))
        return True
