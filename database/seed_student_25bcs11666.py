"""
IntelliCampus: Seed Data for Student 25BCS11666 (Manish Tanwar)
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.database import DatabaseManager
from models.student import Student
from services.ai_analytics_service import AIAnalyticsEngine

def seed_25bcs11666():
    db = DatabaseManager()
    print("[Seed] Initializing seed data for 25BCS11666...")

    # 1. Student Record
    db.execute_update("""
        INSERT OR REPLACE INTO students (
            student_id, full_name, email, phone, program, semester, section, batch, uims_username
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """, (
        '25BCS11666', 'Manish Tanwar', 'mstanwar567@gmail.com', '+91 98123 45678',
        'B.E. Computer Science & Engineering', 2, 'CSE-12', '2025-2029', '25bcs11666'
    ))

    # 2. Subjects for Semester 2
    subjects = [
        ('25CS201', 'Data Structures & Algorithms', 4.0, 2, 'Dr. Arvind Singhania', 'Theory', 75.0),
        ('25CS202', 'Object Oriented Programming with C++', 4.0, 2, 'Prof. Pooja Rawat', 'Theory', 75.0),
        ('25MA201', 'Discrete Mathematics & Graph Theory', 4.0, 2, 'Dr. S. K. Gupta', 'Theory', 75.0),
        ('25EC201', 'Digital Electronics & Microprocessors', 3.0, 2, 'Prof. K. Ramanujam', 'Theory', 75.0),
        ('25EV201', 'Environmental Science & Sustainability', 2.0, 2, 'Dr. Anjali Mehta', 'Theory', 75.0),
        ('25CSP21', 'Data Structures Laboratory', 1.5, 2, 'Dr. Arvind Singhania', 'Practical', 75.0),
        ('25CSP22', 'OOP with C++ Laboratory', 1.5, 2, 'Prof. Pooja Rawat', 'Practical', 75.0)
    ]
    for s in subjects:
        db.execute_update("""
            INSERT OR REPLACE INTO subjects (subject_code, subject_name, credits, semester, faculty_name, subject_type, min_attendance_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, s)

    # 3. Attendance for 25BCS11666
    # Note: 25EC201 has shortage (67.65%) for AI prediction demonstration
    attendance = [
        ('25BCS11666', '25CS201', 38, 34, 2, 0, 94.74),
        ('25BCS11666', '25CS202', 36, 30, 1, 0, 86.11),
        ('25BCS11666', '25MA201', 40, 31, 0, 0, 77.50),
        ('25BCS11666', '25EC201', 34, 22, 1, 0, 67.65),
        ('25BCS11666', '25EV201', 20, 18, 0, 0, 90.00),
        ('25BCS11666', '25CSP21', 14, 14, 0, 0, 100.00),
        ('25BCS11666', '25CSP22', 14, 13, 1, 0, 100.00)
    ]
    for a in attendance:
        db.execute_update("""
            INSERT OR REPLACE INTO attendance (student_id, subject_code, total_delivered, total_attended, duty_leave, medical_leave, percentage)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, a)

    # 4. Detailed Lecture Records
    records = [
        ('25BCS11666', '25CS201', '2026-11-04', '09:00 - 10:00', 'Present', 'AVL Tree Rotations and Balance Factors'),
        ('25BCS11666', '25CS202', '2026-11-04', '10:00 - 11:00', 'Present', 'Polymorphism & Virtual Destructors'),
        ('25BCS11666', '25EC201', '2026-11-05', '11:15 - 12:15', 'Absent',  'Sequential Circuits & Flip Flops'),
        ('25BCS11666', '25MA201', '2026-11-05', '13:00 - 14:00', 'Present', 'Eulerian & Hamiltonian Paths in Graphs'),
        ('25BCS11666', '25EC201', '2026-11-06', '09:00 - 10:00', 'Duty Leave', 'College Tech Fest Robotics Setup'),
        ('25BCS11666', '25CSP21', '2026-11-06', '14:00 - 16:00', 'Present', 'Lab Exam: Red-Black Tree Implementation')
    ]
    for r in records:
        db.execute_update("""
            INSERT INTO attendance_records (student_id, subject_code, lecture_date, time_slot, status, topic_covered)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, r)

    # 5. Marks for 25BCS11666
    marks = [
        ('25BCS11666', '25CS201', 2, 'Internal_MST1', 30.0, 28.5, 20.0, 'O',  '2026-09-15'),
        ('25BCS11666', '25CS201', 2, 'Internal_MST2', 30.0, 29.0, 20.0, 'O',  '2026-10-20'),
        ('25BCS11666', '25CS201', 2, 'Assignment',    20.0, 19.5, 10.0, 'O',  '2026-10-12'),
        ('25BCS11666', '25CS202', 2, 'Internal_MST1', 30.0, 26.0, 20.0, 'A+', '2026-09-16'),
        ('25BCS11666', '25CS202', 2, 'Internal_MST2', 30.0, 27.5, 20.0, 'A+', '2026-10-21'),
        ('25BCS11666', '25CS202', 2, 'Assignment',    20.0, 18.0, 10.0, 'A+', '2026-10-14'),
        ('25BCS11666', '25MA201', 2, 'Internal_MST1', 30.0, 24.0, 20.0, 'A',  '2026-09-17'),
        ('25BCS11666', '25MA201', 2, 'Internal_MST2', 30.0, 25.0, 20.0, 'A',  '2026-10-22'),
        ('25BCS11666', '25EC201', 2, 'Internal_MST1', 30.0, 17.0, 20.0, 'C',  '2026-09-18'),
        ('25BCS11666', '25EC201', 2, 'Internal_MST2', 30.0, 18.5, 20.0, 'B',  '2026-10-23'),
        ('25BCS11666', '25EC201', 2, 'Assignment',    20.0, 14.0, 10.0, 'B',  '2026-10-15'),
        ('25BCS11666', '25EV201', 2, 'Internal_MST1', 30.0, 27.0, 20.0, 'A+', '2026-09-19'),
        ('25BCS11666', '25EV201', 2, 'Assignment',    20.0, 19.0, 10.0, 'O',  '2026-10-16')
    ]
    for m in marks:
        db.execute_update("""
            INSERT INTO marks (student_id, subject_code, semester, component_type, max_marks, marks_obtained, weightage_pct, grade, recorded_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, m)

    # 6. Semester Results (Semester 1 Passed with 8.92 SGPA)
    db.execute_update("""
        INSERT OR REPLACE INTO semester_results (student_id, semester, total_credits, earned_credits, sgpa, cgpa, status, published_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, ('25BCS11666', 1, 20.0, 20.0, 8.92, 8.92, 'Passed', '2026-01-10'))

    # 7. Timetable for 25BCS11666
    timetable = [
        ('25BCS11666', 'Monday', '09:00:00', '10:00:00', '25CS201', 'LT-104', 'Dr. Arvind Singhania', 0),
        ('25BCS11666', 'Monday', '10:00:00', '11:00:00', '25CS202', 'LT-104', 'Prof. Pooja Rawat', 0),
        ('25BCS11666', 'Monday', '11:15:00', '12:15:00', '25MA201', 'LT-104', 'Dr. S. K. Gupta', 0),
        ('25BCS11666', 'Monday', '13:00:00', '15:00:00', '25CSP21', 'Lab-3',   'Dr. Arvind Singhania', 1),

        ('25BCS11666', 'Tuesday', '09:00:00', '10:00:00', '25EC201', 'LT-102', 'Prof. K. Ramanujam', 0),
        ('25BCS11666', 'Tuesday', '10:00:00', '11:00:00', '25CS201', 'LT-102', 'Dr. Arvind Singhania', 0),
        ('25BCS11666', 'Tuesday', '11:15:00', '12:15:00', '25EV201', 'LT-102', 'Dr. Anjali Mehta', 0),
        ('25BCS11666', 'Tuesday', '13:00:00', '15:00:00', '25CSP22', 'Lab-1',   'Prof. Pooja Rawat', 1),

        ('25BCS11666', 'Wednesday', '09:00:00', '10:00:00', '25MA201', 'LT-104', 'Dr. S. K. Gupta', 0),
        ('25BCS11666', 'Wednesday', '10:00:00', '11:00:00', '25CS202', 'LT-104', 'Prof. Pooja Rawat', 0),
        ('25BCS11666', 'Wednesday', '11:15:00', '12:15:00', '25EC201', 'LT-104', 'Prof. K. Ramanujam', 0),

        ('25BCS11666', 'Thursday', '09:00:00', '10:00:00', '25CS201', 'LT-104', 'Dr. Arvind Singhania', 0),
        ('25BCS11666', 'Thursday', '10:00:00', '11:00:00', '25EC201', 'LT-104', 'Prof. K. Ramanujam', 0),
        ('25BCS11666', 'Thursday', '11:15:00', '12:15:00', '25EV201', 'LT-104', 'Dr. Anjali Mehta', 0),

        ('25BCS11666', 'Friday', '09:00:00', '10:00:00', '25CS202', 'LT-104', 'Prof. Pooja Rawat', 0),
        ('25BCS11666', 'Friday', '10:00:00', '11:00:00', '25MA201', 'LT-104', 'Dr. S. K. Gupta', 0)
    ]
    for tt in timetable:
        db.execute_update("""
            INSERT INTO timetable (student_id, day_of_week, start_time, end_time, subject_code, room_no, faculty_name, is_lab)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, tt)

    # 8. Assignments
    assignments = [
        ('25BCS11666', '25CS201', 'Graph Traversal Algorithms Benchmark', 'Implement BFS and DFS with adjacency list and measure execution times on sparse vs dense graphs.', '2026-11-18 23:59:00', 'In Progress', 100.0, None),
        ('25BCS11666', '25EC201', '4-Bit Ripple Counter Design', 'Design and simulate a synchronous up/down counter using JK Flip Flops.', '2026-11-14 17:00:00', 'Pending', 50.0, None),
        ('25BCS11666', '25CS202', 'Banking Management System in C++', 'OOP principles implementation with abstract classes and exception handling.', '2026-10-28 23:59:00', 'Graded', 100.0, 96.0)
    ]
    for asg in assignments:
        db.execute_update("""
            INSERT INTO assignments (student_id, subject_code, title, description, due_date, status, max_marks, marks_awarded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, asg)

    # 9. Tasks
    tasks = [
        ('25BCS11666', 'Review Digital Electronics Karnaugh Maps (Ch 4)', 'Study', 'High', '2026-11-12', 0),
        ('25BCS11666', 'Solve 5 LeetCode Graph Problems (BFS/DFS)', 'Study', 'Medium', '2026-11-15', 0),
        ('25BCS11666', 'Prepare for Discrete Math Quiz 2', 'Exam', 'High', '2026-11-16', 0)
    ]
    for t in tasks:
        db.execute_update("""
            INSERT INTO tasks (student_id, title, category, priority, due_date, is_completed)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, t)

    # 10. Goals
    goals = [
        ('25BCS11666', 'Achieve Semester 2 Target CGPA', 'Target_CGPA', 9.00, 8.92, 'GPA', '2026-12-30', 'Active'),
        ('25BCS11666', 'Clear Digital Electronics Attendance Shortage', 'Min_Attendance', 75.00, 67.65, '%', '2026-11-30', 'Active'),
        ('25BCS11666', 'Maintain 90%+ in Data Structures & OOP', 'Min_Attendance', 90.00, 90.42, '%', '2026-12-15', 'Active')
    ]
    for g in goals:
        db.execute_update("""
            INSERT INTO goals (student_id, title, target_type, target_value, current_value, unit, deadline, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, g)

    # 11. Notifications
    notifs = [
        ('25BCS11666', '🚨 Attendance Shortage: Digital Electronics (25EC201)', 'Your attendance in 25EC201 is 67.65%, which is below the mandatory 75% limit. You need to attend the next 10 consecutive lectures.', 'Attendance', 0),
        ('25BCS11666', 'Assignment Approaching: 4-Bit Ripple Counter', 'Assignment is due on Nov 14, 2026.', 'Assignment', 0),
        ('25BCS11666', 'Semester 1 Result Verified', 'Your verified Semester 1 SGPA is 8.92 with 20 earned credits.', 'System', 1)
    ]
    for n in notifs:
        db.execute_update("""
            INSERT INTO notifications (student_id, title, message, category, is_read)
            VALUES (%s, %s, %s, %s, %s);
        """, n)

    # 12. Run AI Analytics Engine for 25BCS11666
    report = AIAnalyticsEngine.analyze_student('25BCS11666')
    print(f"[Seed] Successfully seeded record for 25BCS11666! AI Predicted CGPA: {report.predicted_cgpa}")

if __name__ == "__main__":
    seed_25bcs11666()
