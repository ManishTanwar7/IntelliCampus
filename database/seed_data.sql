-- =======================================================================
-- IntelliCampus: Realistic Seed Data
-- =======================================================================

USE intellicampus_db;

-- 1. Insert Student
INSERT INTO students (student_id, full_name, email, phone, program, semester, section, batch, uims_username)
VALUES 
('21BCS7492', 'Aarav Sharma', 'aarav.sharma@cuchd.in', '+91 98765 43210', 'B.E. Computer Science & Engineering', 5, 'CSE-04', '2023-2027', '21bcs7492')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- 2. Insert Subjects for Semester 5
INSERT INTO subjects (subject_code, subject_name, credits, semester, faculty_name, subject_type, min_attendance_pct)
VALUES
('21CS501', 'Design & Analysis of Algorithms', 4.0, 5, 'Dr. Rajesh Verma', 'Theory', 75.00),
('21CS502', 'Database Management Systems', 4.0, 5, 'Prof. Sunita Menon', 'Theory', 75.00),
('21CS503', 'Operating Systems & System Prog.', 4.0, 5, 'Dr. Amitav Ghosh', 'Theory', 75.00),
('21CS504', 'Machine Learning & AI Foundations', 3.0, 5, 'Dr. Neha Kulkarni', 'Theory', 75.00),
('21CS505', 'Computer Networks & Security', 3.0, 5, 'Prof. Vikram Chauhan', 'Theory', 75.00),
('21CSP51', 'DBMS Laboratory & Mini Project', 1.5, 5, 'Prof. Sunita Menon', 'Practical', 75.00),
('21CSP52', 'Algorithms & Coding Lab', 1.5, 5, 'Dr. Rajesh Verma', 'Practical', 75.00)
ON DUPLICATE KEY UPDATE subject_name=VALUES(subject_name);

-- 3. Insert Attendance Summary
-- Notice 21CS504 has attendance below 75% to trigger AI shortage warning!
INSERT INTO attendance (student_id, subject_code, total_delivered, total_attended, duty_leave, medical_leave)
VALUES
('21BCS7492', '21CS501', 42, 36, 2, 0), -- (36+2)/42 = 90.48%
('21BCS7492', '21CS502', 38, 32, 1, 0), -- (32+1)/38 = 86.84%
('21BCS7492', '21CS503', 40, 31, 0, 0), -- 31/40 = 77.50%
('21BCS7492', '21CS504', 35, 23, 1, 0), -- (23+1)/35 = 68.57% (SHORTAGE ALERT!)
('21BCS7492', '21CS505', 36, 29, 2, 0), -- (29+2)/36 = 86.11%
('21BCS7492', '21CSP51', 14, 13, 0, 0), -- 13/14 = 92.86%
('21BCS7492', '21CSP52', 14, 12, 1, 0)  -- (12+1)/14 = 92.86%
ON DUPLICATE KEY UPDATE total_delivered=VALUES(total_delivered);

-- 4. Insert Detailed Attendance Records (Past few days)
INSERT INTO attendance_records (student_id, subject_code, lecture_date, time_slot, status, topic_covered)
VALUES
('21BCS7492', '21CS501', '2026-11-02', '09:00 - 10:00', 'Present', 'Dynamic Programming - Bellman Ford'),
('21BCS7492', '21CS502', '2026-11-02', '10:00 - 11:00', 'Present', 'Query Optimization & B+ Trees'),
('21BCS7492', '21CS503', '2026-11-03', '11:15 - 12:15', 'Absent',  'Virtual Memory & Demand Paging'),
('21BCS7492', '21CS504', '2026-11-03', '13:00 - 14:00', 'Absent',  'Support Vector Machines (SVM)'),
('21BCS7492', '21CS505', '2026-11-04', '09:00 - 10:00', 'Present', 'TCP Flow & Congestion Control'),
('21BCS7492', '21CSP51', '2026-11-04', '14:00 - 16:00', 'Present', 'PL/SQL Triggers & Stored Procedures'),
('21BCS7492', '21CS504', '2026-11-05', '10:00 - 11:00', 'Duty Leave', 'Robotics Hackathon Participation'),
('21BCS7492', '21CS501', '2026-11-06', '09:00 - 10:00', 'Present', 'Greedy Techniques & Matroids'),
('21BCS7492', '21CS502', '2026-11-06', '11:15 - 12:15', 'Present', 'Concurrency Control & 2PL');

-- 5. Insert Marks (Internal MSTs & Assignments)
INSERT INTO marks (student_id, subject_code, semester, component_type, max_marks, marks_obtained, weightage_pct, grade, recorded_date)
VALUES
-- Algorithms
('21BCS7492', '21CS501', 5, 'Internal_MST1', 30.0, 27.5, 20.0, 'A+', '2026-09-20'),
('21BCS7492', '21CS501', 5, 'Internal_MST2', 30.0, 28.0, 20.0, 'A+', '2026-10-25'),
('21BCS7492', '21CS501', 5, 'Assignment',    20.0, 19.0, 10.0, 'O',  '2026-10-15'),
-- DBMS
('21BCS7492', '21CS502', 5, 'Internal_MST1', 30.0, 25.0, 20.0, 'A',  '2026-09-21'),
('21BCS7492', '21CS502', 5, 'Internal_MST2', 30.0, 26.5, 20.0, 'A+', '2026-10-26'),
('21BCS7492', '21CS502', 5, 'Assignment',    20.0, 18.0, 10.0, 'A+', '2026-10-16'),
-- Operating Systems
('21BCS7492', '21CS503', 5, 'Internal_MST1', 30.0, 23.0, 20.0, 'B+', '2026-09-22'),
('21BCS7492', '21CS503', 5, 'Internal_MST2', 30.0, 24.0, 20.0, 'A',  '2026-10-27'),
('21BCS7492', '21CS503', 5, 'Assignment',    20.0, 17.0, 10.0, 'A',  '2026-10-17'),
-- Machine Learning (Weak internal score!)
('21BCS7492', '21CS504', 5, 'Internal_MST1', 30.0, 16.5, 20.0, 'C',  '2026-09-23'),
('21BCS7492', '21CS504', 5, 'Internal_MST2', 30.0, 18.0, 20.0, 'B',  '2026-10-28'),
('21BCS7492', '21CS504', 5, 'Assignment',    20.0, 14.0, 10.0, 'B',  '2026-10-18'),
-- Networks
('21BCS7492', '21CS505', 5, 'Internal_MST1', 30.0, 26.0, 20.0, 'A+', '2026-09-24'),
('21BCS7492', '21CS505', 5, 'Internal_MST2', 30.0, 25.5, 20.0, 'A',  '2026-10-29'),
('21BCS7492', '21CS505', 5, 'Assignment',    20.0, 19.5, 10.0, 'O',  '2026-10-19');

-- 6. Insert Semester Results History (Sem 1 to Sem 4 for CGPA calculations)
INSERT INTO semester_results (student_id, semester, total_credits, earned_credits, sgpa, cgpa, status, published_date)
VALUES
('21BCS7492', 1, 21.0, 21.0, 8.45, 8.45, 'Passed', '2024-01-15'),
('21BCS7492', 2, 22.5, 22.5, 8.70, 8.58, 'Passed', '2024-06-20'),
('21BCS7492', 3, 23.0, 23.0, 8.30, 8.48, 'Passed', '2025-01-18'),
('21BCS7492', 4, 22.0, 22.0, 8.85, 8.57, 'Passed', '2025-06-25')
ON DUPLICATE KEY UPDATE sgpa=VALUES(sgpa);

-- 7. Insert Weekly Timetable
INSERT INTO timetable (student_id, day_of_week, start_time, end_time, subject_code, room_no, faculty_name, is_lab)
VALUES
('21BCS7492', 'Monday', '09:00:00', '10:00:00', '21CS501', 'C-302', 'Dr. Rajesh Verma', FALSE),
('21BCS7492', 'Monday', '10:00:00', '11:00:00', '21CS502', 'C-302', 'Prof. Sunita Menon', FALSE),
('21BCS7492', 'Monday', '11:15:00', '12:15:00', '21CS503', 'C-302', 'Dr. Amitav Ghosh', FALSE),
('21BCS7492', 'Monday', '13:00:00', '15:00:00', '21CSP51', 'Lab-5', 'Prof. Sunita Menon', TRUE),

('21BCS7492', 'Tuesday', '09:00:00', '10:00:00', '21CS504', 'C-304', 'Dr. Neha Kulkarni', FALSE),
('21BCS7492', 'Tuesday', '10:00:00', '11:00:00', '21CS505', 'C-304', 'Prof. Vikram Chauhan', FALSE),
('21BCS7492', 'Tuesday', '11:15:00', '12:15:00', '21CS501', 'C-304', 'Dr. Rajesh Verma', FALSE),
('21BCS7492', 'Tuesday', '13:00:00', '15:00:00', '21CSP52', 'Lab-2', 'Dr. Rajesh Verma', TRUE),

('21BCS7492', 'Wednesday', '09:00:00', '10:00:00', '21CS503', 'C-302', 'Dr. Amitav Ghosh', FALSE),
('21BCS7492', 'Wednesday', '10:00:00', '11:00:00', '21CS502', 'C-302', 'Prof. Sunita Menon', FALSE),
('21BCS7492', 'Wednesday', '11:15:00', '12:15:00', '21CS505', 'C-302', 'Prof. Vikram Chauhan', FALSE),
('21BCS7492', 'Wednesday', '13:00:00', '14:00:00', '21CS504', 'C-302', 'Dr. Neha Kulkarni', FALSE),

('21BCS7492', 'Thursday', '09:00:00', '10:00:00', '21CS501', 'C-302', 'Dr. Rajesh Verma', FALSE),
('21BCS7492', 'Thursday', '10:00:00', '11:00:00', '21CS504', 'C-302', 'Dr. Neha Kulkarni', FALSE),
('21BCS7492', 'Thursday', '11:15:00', '12:15:00', '21CS503', 'C-302', 'Dr. Amitav Ghosh', FALSE),

('21BCS7492', 'Friday', '09:00:00', '10:00:00', '21CS505', 'C-302', 'Prof. Vikram Chauhan', FALSE),
('21BCS7492', 'Friday', '10:00:00', '11:00:00', '21CS502', 'C-302', 'Prof. Sunita Menon', FALSE),
('21BCS7492', 'Friday', '11:15:00', '12:15:00', '21CS501', 'C-302', 'Dr. Rajesh Verma', FALSE);

-- 8. Insert Assignments
INSERT INTO assignments (student_id, subject_code, title, description, due_date, status, max_marks, marks_awarded)
VALUES
('21BCS7492', '21CS504', 'Hyperparameter Tuning in SVM', 'Implement GridSearch and RandomSearch on the MNIST dataset and analyze accuracy curves.', '2026-11-12 23:59:00', 'Pending', 100.0, NULL),
('21BCS7492', '21CS502', 'E-Commerce Schema Normalization', 'Provide 3NF and BCNF decompositions for the given relational order catalog.', '2026-11-15 17:00:00', 'In Progress', 50.0, NULL),
('21BCS7492', '21CS501', 'Divide & Conquer Convex Hull', 'Algorithm formulation and test benchmark with randomized 2D coordinate clusters.', '2026-11-20 23:59:00', 'Pending', 50.0, NULL),
('21BCS7492', '21CS503', 'Custom Shell with Pipes & Redirection', 'Build a POSIX C shell supporting stdin/stdout redirection and concurrent pipelines.', '2026-10-30 23:59:00', 'Graded', 100.0, 94.0);

-- 9. Insert Tasks
INSERT INTO tasks (student_id, title, category, priority, due_date, is_completed)
VALUES
('21BCS7492', 'Read SVM Kernels & Slack Variables in Bishop Book', 'Study', 'High', '2026-11-10', FALSE),
('21BCS7492', 'Prepare 10 Practice Problems for Dynamic Programming', 'Study', 'Medium', '2026-11-11', FALSE),
('21BCS7492', 'Submit ML Assignment 3 on Portal', 'Assignment', 'High', '2026-11-12', FALSE),
('21BCS7492', 'Review OS Chapter 8 (Deadlock Prevention & Banker Algorithm)', 'Exam', 'Medium', '2026-11-14', FALSE),
('21BCS7492', 'Attend IEEE Student Branch Tech Talk on Generative AI', 'General', 'Low', '2026-11-16', TRUE);

-- 10. Insert Goals
INSERT INTO goals (student_id, title, target_type, target_value, current_value, unit, deadline, status)
VALUES
('21BCS7492', 'Achieve Overall Semester 5 CGPA Target', 'Target_CGPA', 8.80, 8.57, 'GPA', '2026-12-30', 'Active'),
('21BCS7492', 'Restore Machine Learning Attendance above Threshold', 'Min_Attendance', 75.00, 68.57, '%', '2026-11-30', 'Active'),
('21BCS7492', 'Maintain 90%+ in Algorithms & DBMS', 'Min_Attendance', 90.00, 88.66, '%', '2026-12-15', 'Active'),
('21BCS7492', 'Complete 120 Weekly Study Hours across Semester', 'Study_Hours', 120.00, 84.50, 'Hours', '2026-12-20', 'Active');

-- 11. Insert Study Plans
INSERT INTO study_plans (student_id, subject_code, scheduled_date, start_time, duration_minutes, topic, notes, is_completed)
VALUES
('21BCS7492', '21CS504', '2026-11-09', '18:00:00', 90, 'SVM Kernels and Loss Function Derivations', 'Focus on Lagrange multipliers and dual problem.', FALSE),
('21BCS7492', '21CS501', '2026-11-10', '19:30:00', 60, 'Knapsack and Subset Sum DP formulation', 'Solve 3 LeetCode Mediums.', FALSE),
('21BCS7492', '21CS502', '2026-11-11', '17:00:00', 75, 'B+ Tree Splitting & Merge Algorithm', 'Diagram tree rebalancing cases.', FALSE);

-- 12. Insert Notifications
INSERT INTO notifications (student_id, title, message, category, is_read)
VALUES
('21BCS7492', 'Attendance Warning: Machine Learning', 'Your attendance in 21CS504 is 68.57%, which is below the mandatory 75% limit. You need to attend the next 9 consecutive lectures without missing any.', 'Attendance', FALSE),
('21BCS7492', 'Assignment Due Soon: SVM Tuning', 'Assignment "Hyperparameter Tuning in SVM" is due on Nov 12, 2026.', 'Assignment', FALSE),
('21BCS7492', 'Mid-Semester Exam Results Released', 'Internal MST2 marks for Algorithms, DBMS, and OS have been posted.', 'Exam', TRUE);


-- =======================================================================
-- Seed Student 25BCS11666 (Manish Tanwar - Semester 2)
-- =======================================================================

INSERT INTO students (student_id, full_name, email, phone, program, semester, section, batch, uims_username)
VALUES 
('25BCS11666', 'Manish Tanwar', 'mstanwar567@gmail.com', '+91 98123 45678', 'B.E. Computer Science & Engineering', 2, 'CSE-12', '2025-2029', '25bcs11666')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO subjects (subject_code, subject_name, credits, semester, faculty_name, subject_type, min_attendance_pct)
VALUES
('25CS201', 'Data Structures & Algorithms', 4.0, 2, 'Dr. Arvind Singhania', 'Theory', 75.00),
('25CS202', 'Object Oriented Programming with C++', 4.0, 2, 'Prof. Pooja Rawat', 'Theory', 75.00),
('25MA201', 'Discrete Mathematics & Graph Theory', 4.0, 2, 'Dr. S. K. Gupta', 'Theory', 75.00),
('25EC201', 'Digital Electronics & Microprocessors', 3.0, 2, 'Prof. K. Ramanujam', 'Theory', 75.00),
('25EV201', 'Environmental Science & Sustainability', 2.0, 2, 'Dr. Anjali Mehta', 'Theory', 75.00),
('25CSP21', 'Data Structures Laboratory', 1.5, 2, 'Dr. Arvind Singhania', 'Practical', 75.00),
('25CSP22', 'OOP with C++ Laboratory', 1.5, 2, 'Prof. Pooja Rawat', 'Practical', 75.00)
ON DUPLICATE KEY UPDATE subject_name=VALUES(subject_name);

INSERT INTO attendance (student_id, subject_code, total_delivered, total_attended, duty_leave, medical_leave)
VALUES
('25BCS11666', '25CS201', 38, 34, 2, 0), -- 36/38 = 94.74%
('25BCS11666', '25CS202', 36, 30, 1, 0), -- 31/36 = 86.11%
('25BCS11666', '25MA201', 40, 31, 0, 0), -- 31/40 = 77.50%
('25BCS11666', '25EC201', 34, 22, 1, 0), -- 23/34 = 67.65% (SHORTAGE)
('25BCS11666', '25EV201', 20, 18, 0, 0), -- 18/20 = 90.00%
('25BCS11666', '25CSP21', 14, 14, 0, 0), -- 14/14 = 100.00%
('25BCS11666', '25CSP22', 14, 13, 1, 0)  -- 14/14 = 100.00%
ON DUPLICATE KEY UPDATE total_delivered=VALUES(total_delivered);

INSERT INTO semester_results (student_id, semester, total_credits, earned_credits, sgpa, cgpa, status, published_date)
VALUES
('25BCS11666', 1, 20.0, 20.0, 8.92, 8.92, 'Passed', '2026-01-10')
ON DUPLICATE KEY UPDATE sgpa=VALUES(sgpa);
