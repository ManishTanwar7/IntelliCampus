"""
IntelliCampus: Marks, SGPA & Result Analysis View
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

from controllers.auth_controller import AuthController
from controllers.academic_controller import AcademicController
from controllers.analytics_controller import AnalyticsController
from views.components.cards import MetricCard
from views.components.charts import PlotlyChartWidget

class MarksPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        # 1. Metric Cards Header
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(14)

        self.card_cgpa = MetricCard("Cumulative CGPA", "0.00", "Official Scale: 10.00", "#6366F1")
        self.card_sgpa = MetricCard("Latest SGPA", "0.00", "Previous Semester", "#06B6D4")
        self.card_credits = MetricCard("Credits Earned", "0.0", "Total Degree Credits", "#10B981")
        self.card_forecast = MetricCard("AI Predicted CGPA", "0.00", "End-of-Semester Forecast", "#F59E0B")

        metrics_layout.addWidget(self.card_cgpa)
        metrics_layout.addWidget(self.card_sgpa)
        metrics_layout.addWidget(self.card_credits)
        metrics_layout.addWidget(self.card_forecast)
        self.content_layout.addLayout(metrics_layout)

        # 2. Interactive SGPA / CGPA Progression Plotly Chart
        chart_card = QFrame()
        chart_card.setProperty("class", "CardFrame")
        chart_layout = QVBoxLayout(chart_card)
        chart_title = QLabel("Semester-by-Semester SGPA / CGPA Trajectory")
        chart_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        chart_layout.addWidget(chart_title)

        self.chart_widget = PlotlyChartWidget()
        self.chart_widget.setFixedHeight(340)
        chart_layout.addWidget(self.chart_widget)
        self.content_layout.addWidget(chart_card)

        # 3. Two columns: Semester Progression Table & Internal Assessment Marks
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(16)

        # Left Column: Semester Results Table
        sem_card = QFrame()
        sem_card.setProperty("class", "CardFrame")
        sem_layout = QVBoxLayout(sem_card)
        sem_title = QLabel("Semester Results History")
        sem_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        sem_layout.addWidget(sem_title)

        self.sem_table = QTableWidget()
        self.sem_table.setColumnCount(5)
        self.sem_table.setHorizontalHeaderLabels(["Semester", "Credits", "SGPA", "CGPA", "Status"])
        self.sem_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sem_table.setFixedHeight(260)
        sem_layout.addWidget(self.sem_table)
        tables_layout.addWidget(sem_card, 4)

        # Right Column: Current Semester Internal Assessments
        marks_card = QFrame()
        marks_card.setProperty("class", "CardFrame")
        marks_layout = QVBoxLayout(marks_card)
        marks_title = QLabel("Current Semester Internal Assessments (MST & Continuous)")
        marks_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        marks_layout.addWidget(marks_title)

        self.marks_table = QTableWidget()
        self.marks_table.setColumnCount(5)
        self.marks_table.setHorizontalHeaderLabels(["Course", "Assessment", "Score", "Max", "Grade"])
        self.marks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.marks_table.setFixedHeight(260)
        marks_layout.addWidget(self.marks_table)
        tables_layout.addWidget(marks_card, 6)

        self.content_layout.addLayout(tables_layout)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        results = AcademicController.get_semester_results(student.student_id)
        report = AnalyticsController.get_or_generate_report(student.student_id)
        marks = AcademicController.get_marks_by_semester(student.student_id)

        # Update metrics
        current_cgpa = results[-1].cgpa if results else 8.50
        latest_sgpa = results[-1].sgpa if results else 8.40
        earned_credits = sum(r.earned_credits for r in results) if results else 88.5
        predicted_cgpa = report.predicted_cgpa if report else current_cgpa

        self.card_cgpa.update_value(f"{current_cgpa:.2f}")
        self.card_sgpa.update_value(f"{latest_sgpa:.2f}", f"Semester {results[-1].semester}" if results else "")
        self.card_credits.update_value(f"{earned_credits:.1f}")
        self.card_forecast.update_value(f"{predicted_cgpa:.2f}", "Forecasted with AI")

        # Load Plotly Trend Chart
        if results:
            fig = PlotlyChartWidget.create_cgpa_trend_chart(results, predicted_cgpa, is_dark=True)
            self.chart_widget.load_figure(fig, is_dark=True)

        # Populate Semester Results
        self.sem_table.setRowCount(len(results))
        for row_idx, r in enumerate(results):
            self.sem_table.setItem(row_idx, 0, QTableWidgetItem(f"Semester {r.semester}"))
            self.sem_table.setItem(row_idx, 1, QTableWidgetItem(f"{r.earned_credits:.1f}"))
            self.sem_table.setItem(row_idx, 2, QTableWidgetItem(f"{r.sgpa:.2f}"))
            self.sem_table.setItem(row_idx, 3, QTableWidgetItem(f"{r.cgpa:.2f}"))
            status_item = QTableWidgetItem(r.status)
            status_item.setForeground(Qt.GlobalColor.green)
            self.sem_table.setItem(row_idx, 4, status_item)

        # Populate Internal Assessments
        self.marks_table.setRowCount(len(marks))
        for row_idx, m in enumerate(marks):
            self.marks_table.setItem(row_idx, 0, QTableWidgetItem(m.subject_code))
            self.marks_table.setItem(row_idx, 1, QTableWidgetItem(m.component_type.replace("_", " ")))
            self.marks_table.setItem(row_idx, 2, QTableWidgetItem(f"{m.marks_obtained:.1f}"))
            self.marks_table.setItem(row_idx, 3, QTableWidgetItem(f"{m.max_marks:.0f}"))
            grade_item = QTableWidgetItem(m.grade or "-")
            if m.percentage >= 80:
                grade_item.setForeground(Qt.GlobalColor.green)
            elif m.percentage < 60:
                grade_item.setForeground(Qt.GlobalColor.red)
            self.marks_table.setItem(row_idx, 4, grade_item)
