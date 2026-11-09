"""
IntelliCampus: Dashboard Page (Collegia Inspired)
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from controllers.auth_controller import AuthController
from controllers.academic_controller import AcademicController
from controllers.productivity_controller import ProductivityController
from controllers.analytics_controller import AnalyticsController
from views.components.cards import MetricCard
from views.components.charts import PlotlyChartWidget

class DashboardPage(QWidget):
    navigate_requested = pyqtSignal(str)  # Allows quick navigation to other pages

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Scroll Area for responsive dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        # 1. Metric Cards Grid
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(14)
        
        self.card_attendance = MetricCard("Overall Attendance", "0.0%", "Loading...", "#10B981")
        self.card_cgpa = MetricCard("Current CGPA", "0.00", "Goal: 8.50+", "#6366F1")
        self.card_tasks = MetricCard("Pending Tasks", "0", "High Priority: 0", "#F59E0B")
        self.card_schedule = MetricCard("Today's Classes", "0", "Monday Schedule", "#06B6D4")

        self.metrics_grid.addWidget(self.card_attendance, 0, 0)
        self.metrics_grid.addWidget(self.card_cgpa, 0, 1)
        self.metrics_grid.addWidget(self.card_tasks, 0, 2)
        self.metrics_grid.addWidget(self.card_schedule, 0, 3)
        self.content_layout.addLayout(self.metrics_grid)

        # 2. Critical Alert Banner Container
        self.alert_frame = QFrame()
        self.alert_frame.setProperty("class", "CardFrame")
        self.alert_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #EF4444;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        self.alert_layout = QHBoxLayout(self.alert_frame)
        self.alert_label = QLabel()
        self.alert_label.setWordWrap(True)
        self.alert_label.setStyleSheet("color: #F87171; font-weight: 600;")
        self.alert_btn = QPushButton("View Shortage Details")
        self.alert_btn.setProperty("class", "DangerButton")
        self.alert_btn.clicked.connect(lambda: self.navigate_requested.emit("attendance"))
        self.alert_layout.addWidget(self.alert_label, 1)
        self.alert_layout.addWidget(self.alert_btn)
        self.alert_frame.setVisible(False)
        self.content_layout.addWidget(self.alert_frame)

        # 3. Two-Column Dashboard Layout
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(16)

        # Left Column: Attendance Plotly Chart & Today's Schedule
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        chart_card = QFrame()
        chart_card.setProperty("class", "CardFrame")
        chart_layout = QVBoxLayout(chart_card)
        chart_title = QLabel("Attendance Distribution (Course-Wise)")
        chart_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        chart_layout.addWidget(chart_title)

        self.chart_widget = PlotlyChartWidget()
        self.chart_widget.setFixedHeight(320)
        chart_layout.addWidget(self.chart_widget)
        left_col.addWidget(chart_card)

        # Today's Classes Card
        schedule_card = QFrame()
        schedule_card.setProperty("class", "CardFrame")
        self.schedule_layout = QVBoxLayout(schedule_card)
        sched_header = QHBoxLayout()
        sched_title = QLabel("Today's Timetable")
        sched_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        sched_header.addWidget(sched_title)
        sched_header.addStretch()
        view_all_tt = QPushButton("Full Week →")
        view_all_tt.setProperty("class", "SecondaryButton")
        view_all_tt.clicked.connect(lambda: self.navigate_requested.emit("timetable"))
        sched_header.addWidget(view_all_tt)
        self.schedule_layout.addLayout(sched_header)

        self.schedule_container = QVBoxLayout()
        self.schedule_layout.addLayout(self.schedule_container)
        left_col.addWidget(schedule_card)

        cols_layout.addLayout(left_col, 6)

        # Right Column: AI Suggestions & Upcoming Deadlines
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # AI Recommendations Card
        ai_card = QFrame()
        ai_card.setProperty("class", "CardFrame")
        ai_layout = QVBoxLayout(ai_card)
        ai_header = QHBoxLayout()
        ai_badge = QLabel("🤖 AI Academic Insights")
        ai_badge.setStyleSheet("font-size: 14px; font-weight: 700; color: #818CF8;")
        ai_header.addWidget(ai_badge)
        ai_header.addStretch()
        ai_more_btn = QPushButton("Analytics Details →")
        ai_more_btn.setProperty("class", "SecondaryButton")
        ai_more_btn.clicked.connect(lambda: self.navigate_requested.emit("analytics"))
        ai_header.addWidget(ai_more_btn)
        ai_layout.addLayout(ai_header)

        self.ai_recommendations_container = QVBoxLayout()
        ai_layout.addLayout(self.ai_recommendations_container)
        right_col.addWidget(ai_card)

        # Upcoming Deadlines Card
        deadlines_card = QFrame()
        deadlines_card.setProperty("class", "CardFrame")
        dl_layout = QVBoxLayout(deadlines_card)
        dl_header = QHBoxLayout()
        dl_title = QLabel("Upcoming Assignments & Deadlines")
        dl_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        dl_header.addWidget(dl_title)
        dl_header.addStretch()
        view_asg_btn = QPushButton("All Tasks →")
        view_asg_btn.setProperty("class", "SecondaryButton")
        view_asg_btn.clicked.connect(lambda: self.navigate_requested.emit("productivity"))
        dl_header.addWidget(view_asg_btn)
        dl_layout.addLayout(dl_header)

        self.deadlines_container = QVBoxLayout()
        dl_layout.addLayout(self.deadlines_container)
        right_col.addWidget(deadlines_card)

        cols_layout.addLayout(right_col, 5)
        self.content_layout.addLayout(cols_layout)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Load initial data
        self.refresh_data()

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        # 1. Update Metrics
        att_summary = AcademicController.get_attendance_overview(student.student_id)
        overall_pct = att_summary["overall_percentage"]
        shortages = att_summary["shortage_count"]

        self.card_attendance.update_value(
            f"{overall_pct:.1f}%",
            f"{shortages} shortage warning" if shortages > 0 else "All subjects safe (>=75%)"
        )

        results = AcademicController.get_semester_results(student.student_id)
        current_cgpa = results[-1].cgpa if results else 8.50
        self.card_cgpa.update_value(f"{current_cgpa:.2f}", f"Latest SGPA: {results[-1].sgpa:.2f}" if results else "Sem 5")

        tasks = ProductivityController.get_tasks(student.student_id, completed_filter=False)
        high_priority = sum(1 for t in tasks if t.priority == "High")
        self.card_tasks.update_value(str(len(tasks)), f"{high_priority} High Priority")

        # Today's day name (e.g. 'Monday', 'Tuesday')
        day_name = datetime.now().strftime("%A")
        if day_name in ["Saturday", "Sunday"]:
            day_name = "Monday"  # preview weekday
        today_classes = AcademicController.get_timetable(student.student_id, day=day_name)
        self.card_schedule.update_value(str(len(today_classes)), f"{day_name} Schedule")

        # 2. Critical Alert Banner
        critical_subjects = [s for s in att_summary["subjects"] if s.calculated_percentage < 75.0]
        if critical_subjects:
            first = critical_subjects[0]
            needed = first.lectures_needed(75.0)
            self.alert_label.setText(
                f"🚨 Critical Attendance Warning: '{first.subject_name}' is at {first.calculated_percentage}%. "
                f"You need {needed} consecutive classes to restore eligibility. Do not miss upcoming lectures!"
            )
            self.alert_frame.setVisible(True)
        else:
            self.alert_frame.setVisible(False)

        # 3. Render Plotly Bar Chart
        if att_summary["subjects"]:
            fig = PlotlyChartWidget.create_attendance_bar_chart(att_summary["subjects"], is_dark=True)
            self.chart_widget.load_figure(fig, is_dark=True)

        # 4. Populate Today's Schedule List
        self._clear_layout(self.schedule_container)
        if today_classes:
            for item in today_classes[:4]:
                row = QFrame()
                row.setStyleSheet("background-color: #0F172A; border-radius: 6px; padding: 6px 10px;")
                row_l = QHBoxLayout(row)
                row_l.setContentsMargins(8, 6, 8, 6)
                
                time_lbl = QLabel(item.formatted_time)
                time_lbl.setStyleSheet("color: #818CF8; font-weight: 600; font-size: 11px;")
                row_l.addWidget(time_lbl)

                info_lbl = QLabel(f"<b>{item.subject_code}</b>: {item.subject_name}")
                info_lbl.setStyleSheet("font-size: 12px;")
                row_l.addWidget(info_lbl, 1)

                room_lbl = QLabel(f"Room {item.room_no or 'TBA'}")
                room_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
                row_l.addWidget(room_lbl)
                self.schedule_container.addWidget(row)
        else:
            no_classes = QLabel("No classes scheduled for today.")
            no_classes.setStyleSheet("color: #94A3B8; font-style: italic;")
            self.schedule_container.addWidget(no_classes)

        # 5. Populate AI Insights
        self._clear_layout(self.ai_recommendations_container)
        report = AnalyticsController.get_or_generate_report(student.student_id)
        if report and report.recommendations:
            for rec in report.recommendations[:3]:
                box = QLabel(rec)
                box.setWordWrap(True)
                box.setStyleSheet("background-color: #0F172A; border-left: 3px solid #6366F1; border-radius: 4px; padding: 8px; font-size: 12px;")
                self.ai_recommendations_container.addWidget(box)

        # 6. Populate Deadlines
        self._clear_layout(self.deadlines_container)
        assignments = ProductivityController.get_assignments(student.student_id, status_filter="Pending")
        if assignments:
            for a in assignments[:3]:
                d_row = QFrame()
                d_row.setStyleSheet("background-color: #0F172A; border-radius: 6px; padding: 6px 10px;")
                d_layout = QHBoxLayout(d_row)
                d_layout.setContentsMargins(8, 6, 8, 6)

                t_lbl = QLabel(f"<b>{a.title}</b><br><span style='color: #94A3B8;'>{a.subject_name}</span>")
                d_layout.addWidget(t_lbl, 1)

                due_lbl = QLabel(f"Due: {a.due_date[:10]}")
                due_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11px;")
                d_layout.addWidget(due_lbl)
                self.deadlines_container.addWidget(d_row)
        else:
            no_asg = QLabel("No pending assignment deadlines.")
            no_asg.setStyleSheet("color: #10B981; font-weight: 600;")
            self.deadlines_container.addWidget(no_asg)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
