"""
IntelliCampus: Export Service
Generates styled PDF academic summary reports and multi-sheet Excel workbooks.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from config import EXPORTS_DIR
from models.student import Student
from models.attendance import SubjectAttendance
from models.marks import MarkItem, SemesterResult
from models.timetable import TimetableEntry
from models.assignment import Assignment
from models.analytics import AnalyticsReport
from services.ai_analytics_service import AIAnalyticsEngine

class ExportService:

    @classmethod
    def export_excel(cls, student_id: str, file_path: Optional[str] = None) -> str:
        """
        Exports comprehensive multi-sheet Excel workbook.
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = str(EXPORTS_DIR / f"IntelliCampus_{student_id}_{timestamp}.xlsx")

        student = Student.get_by_id(student_id) or Student.get_first_or_default()
        attendance = SubjectAttendance.get_for_student(student_id)
        marks = MarkItem.get_for_student(student_id)
        semesters = SemesterResult.get_for_student(student_id)
        timetable = TimetableEntry.get_for_student(student_id)
        assignments = Assignment.get_for_student(student_id)

        # 1. Summary DataFrame
        current_cgpa = semesters[-1].cgpa if semesters else 0.0
        summary_data = {
            "Field": ["Student Name", "Student UID / Roll", "Program", "Semester", "Email", "Section", "Batch", "Current CGPA", "Report Date"],
            "Value": [
                student.full_name if student else "N/A",
                student.student_id if student else "N/A",
                student.program if student else "N/A",
                student.semester if student else "N/A",
                student.email if student else "N/A",
                student.section if student else "N/A",
                student.batch if student else "N/A",
                current_cgpa,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        df_summary = pd.DataFrame(summary_data)

        # 2. Attendance DataFrame
        att_rows = []
        for a in attendance:
            att_rows.append({
                "Subject Code": a.subject_code,
                "Subject Name": a.subject_name,
                "Delivered": a.total_delivered,
                "Attended": a.total_attended,
                "Duty Leave": a.duty_leave,
                "Medical Leave": a.medical_leave,
                "Percentage (%)": a.calculated_percentage,
                "Status": "SAFE" if a.calculated_percentage >= 75.0 else "SHORTAGE",
                "Safe Skips (>=75%)": a.safe_skips(75.0),
                "Classes Needed (>=75%)": a.lectures_needed(75.0)
            })
        df_att = pd.DataFrame(att_rows)

        # 3. Marks DataFrame
        marks_rows = []
        for m in marks:
            marks_rows.append({
                "Subject Code": m.subject_code,
                "Subject Name": m.subject_name,
                "Semester": m.semester,
                "Assessment": m.component_type,
                "Max Marks": m.max_marks,
                "Marks Obtained": m.marks_obtained,
                "Percentage (%)": m.percentage,
                "Grade": m.grade or "-"
            })
        df_marks = pd.DataFrame(marks_rows)

        # 4. Semester Progression DataFrame
        sem_rows = []
        for s in semesters:
            sem_rows.append({
                "Semester": f"Semester {s.semester}",
                "Credits Registered": s.total_credits,
                "Credits Earned": s.earned_credits,
                "SGPA": s.sgpa,
                "Cumulative CGPA": s.cgpa,
                "Result Status": s.status,
                "Date Published": s.published_date or "-"
            })
        df_sem = pd.DataFrame(sem_rows)

        # 5. Timetable DataFrame
        tt_rows = []
        for t in timetable:
            tt_rows.append({
                "Day": t.day_of_week,
                "Time": t.formatted_time,
                "Subject Code": t.subject_code,
                "Subject Name": t.subject_name,
                "Room": t.room_no or "-",
                "Faculty": t.faculty_name or "-",
                "Type": "Practical/Lab" if t.is_lab else "Theory"
            })
        df_tt = pd.DataFrame(tt_rows)

        # 6. Assignments DataFrame
        asg_rows = []
        for a in assignments:
            asg_rows.append({
                "Subject": a.subject_name,
                "Assignment Title": a.title,
                "Due Date": a.due_date,
                "Status": a.status,
                "Max Marks": a.max_marks,
                "Marks Scored": a.marks_awarded if a.marks_awarded is not None else "Pending"
            })
        df_asg = pd.DataFrame(asg_rows)

        # Write multi-sheet Excel file with openpyxl
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Overview", index=False)
            df_att.to_excel(writer, sheet_name="Attendance Summary", index=False)
            df_marks.to_excel(writer, sheet_name="Assessments & Marks", index=False)
            df_sem.to_excel(writer, sheet_name="Semester Progression", index=False)
            df_tt.to_excel(writer, sheet_name="Weekly Schedule", index=False)
            df_asg.to_excel(writer, sheet_name="Assignments", index=False)

        return file_path

    @classmethod
    def export_pdf(cls, student_id: str, file_path: Optional[str] = None) -> str:
        """
        Generates a styled, multi-page PDF academic dossier.
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = str(EXPORTS_DIR / f"IntelliCampus_Academic_Report_{student_id}_{timestamp}.pdf")

        student = Student.get_by_id(student_id) or Student.get_first_or_default()
        attendance = SubjectAttendance.get_for_student(student_id)
        marks = MarkItem.get_for_student(student_id)
        semesters = SemesterResult.get_for_student(student_id)
        current_cgpa = semesters[-1].cgpa if semesters else 0.0

        # Run AI analytics for recommendations section
        report = AIAnalyticsEngine.analyze_student(student_id)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#4F46E5")   # Indigo
        accent_color = colors.HexColor("#06B6D4")    # Cyan
        text_dark = colors.HexColor("#1E293B")       # Slate
        danger_color = colors.HexColor("#EF4444")    # Red
        success_color = colors.HexColor("#10B981")   # Emerald

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=primary_color,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=14
        )
        section_heading = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=text_dark,
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=text_dark,
            leading=12
        )

        elements = []

        # Header Banner
        elements.append(Paragraph("IntelliCampus Academic Report", title_style))
        elements.append(Paragraph(f"Official Student Academic & Performance Dossier • Generated {datetime.now().strftime('%d %B %Y, %I:%M %p')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

        # Student Details Box
        student_data = [
            [
                Paragraph("<b>Student Name:</b>", body_style), Paragraph(student.full_name if student else "N/A", body_style),
                Paragraph("<b>UID / Roll No:</b>", body_style), Paragraph(student.student_id if student else "N/A", body_style)
            ],
            [
                Paragraph("<b>Program:</b>", body_style), Paragraph(student.program if student else "N/A", body_style),
                Paragraph("<b>Semester / Sec:</b>", body_style), Paragraph(f"Sem {student.semester} ({student.section or 'A'})" if student else "N/A", body_style)
            ],
            [
                Paragraph("<b>Current CGPA:</b>", body_style), Paragraph(f"<b>{current_cgpa:.2f}</b> / 10.00", body_style),
                Paragraph("<b>Predicted CGPA:</b>", body_style), Paragraph(f"<b>{report.predicted_cgpa:.2f}</b> (AI Forecast)", body_style)
            ]
        ]
        student_table = Table(student_data, colWidths=[1.3*inch, 2.3*inch, 1.3*inch, 2.3*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 14))

        # Attendance Summary Table
        elements.append(Paragraph("1. Subject-Wise Attendance Summary", section_heading))
        att_headers = ["Code", "Subject Name", "Delivered", "Attended", "Duty", "Total %", "Status", "Buffer/Req"]
        att_rows = [[Paragraph(f"<b>{h}</b>", body_style) for h in att_headers]]
        for a in attendance:
            pct = a.calculated_percentage
            status_text = "SAFE" if pct >= 75.0 else "SHORTAGE"
            action_text = f"+{a.safe_skips(75.0)} skips" if pct >= 75.0 else f"Req {a.lectures_needed(75.0)}"
            att_rows.append([
                Paragraph(a.subject_code, body_style),
                Paragraph(a.subject_name[:30], body_style),
                Paragraph(str(a.total_delivered), body_style),
                Paragraph(str(a.total_attended), body_style),
                Paragraph(str(a.duty_leave), body_style),
                Paragraph(f"<b>{pct:.1f}%</b>", body_style),
                Paragraph(status_text, body_style),
                Paragraph(action_text, body_style)
            ])

        att_table = Table(att_rows, colWidths=[0.8*inch, 2.4*inch, 0.7*inch, 0.7*inch, 0.5*inch, 0.8*inch, 0.9*inch, 0.9*inch])
        att_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDE9FE")),
            ('TEXTCOLOR', (0,0), (-1,0), primary_color),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        elements.append(att_table)
        elements.append(Spacer(1, 14))

        # Internal Marks & Assessments
        elements.append(Paragraph("2. Internal Assessment Highlights", section_heading))
        mark_headers = ["Code", "Subject", "Component", "Max", "Scored", "% Scored", "Grade"]
        mark_rows = [[Paragraph(f"<b>{h}</b>", body_style) for h in mark_headers]]
        for m in marks[:10]:  # Highlight top 10 recent
            mark_rows.append([
                Paragraph(m.subject_code, body_style),
                Paragraph(m.subject_name[:25], body_style),
                Paragraph(m.component_type.replace("_", " "), body_style),
                Paragraph(f"{m.max_marks:.0f}", body_style),
                Paragraph(f"{m.marks_obtained:.1f}", body_style),
                Paragraph(f"{m.percentage:.1f}%", body_style),
                Paragraph(m.grade or "-", body_style)
            ])

        mark_table = Table(mark_rows, colWidths=[0.9*inch, 2.5*inch, 1.4*inch, 0.6*inch, 0.7*inch, 0.8*inch, 0.6*inch])
        mark_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E0F2FE")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('ALIGN', (3,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        elements.append(mark_table)
        elements.append(Spacer(1, 14))

        # AI Predictive Analytics & Actionable Advice
        elements.append(Paragraph("3. AI Analytics & Intelligent Recommendations", section_heading))
        rec_box_data = []
        for rec in report.recommendations:
            rec_box_data.append([Paragraph(f"• {rec}", body_style)])

        if not rec_box_data:
            rec_box_data.append([Paragraph("No active alerts. Overall academic progress is excellent.", body_style)])

        rec_table = Table(rec_box_data, colWidths=[7.5*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FDE68A")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FEF3C7")),
            ('PADDING', (0,0), (-1,-1), 7),
        ]))
        elements.append(rec_table)

        doc.build(elements)
        return file_path
