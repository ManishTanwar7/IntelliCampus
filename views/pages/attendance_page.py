"""
IntelliCampus: Attendance Module View
Detailed subject-wise tracking, safe-skips/lectures-needed metrics,
interactive "What-If" calculator, and lecture logs.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGridLayout
)
from PyQt6.QtCore import Qt

from controllers.auth_controller import AuthController
from controllers.academic_controller import AcademicController
from views.components.cards import AttendanceSubjectCard, MetricCard

class AttendancePage(QWidget):
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

        # 1. Header Overview Cards
        overview_layout = QHBoxLayout()
        overview_layout.setSpacing(14)
        self.card_overall = MetricCard("Aggregate Attendance", "0.0%", "Minimum required: 75.0%", "#10B981")
        self.card_attended = MetricCard("Total Attended", "0", "Includes Duty & Medical", "#6366F1")
        self.card_delivered = MetricCard("Total Delivered", "0", "Across all active courses", "#06B6D4")
        self.card_shortage = MetricCard("Shortage Risk", "0 Subjects", "Danger threshold (<75%)", "#EF4444")

        overview_layout.addWidget(self.card_overall)
        overview_layout.addWidget(self.card_attended)
        overview_layout.addWidget(self.card_delivered)
        overview_layout.addWidget(self.card_shortage)
        self.content_layout.addLayout(overview_layout)

        # 2. Interactive "What-If" Simulation Calculator
        calc_card = QFrame()
        calc_card.setProperty("class", "CardFrame")
        calc_layout = QVBoxLayout(calc_card)
        calc_layout.setSpacing(10)

        calc_title = QLabel("⚡ Interactive Attendance Simulator ('What-If' Calculator)")
        calc_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #818CF8;")
        calc_layout.addWidget(calc_title)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        controls_layout.addWidget(QLabel("Select Course:"))
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self._run_simulation)
        controls_layout.addWidget(self.course_combo, 2)

        controls_layout.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Attend next lectures consecutively", "Miss / Skip next lectures"])
        self.action_combo.currentIndexChanged.connect(self._run_simulation)
        controls_layout.addWidget(self.action_combo, 2)

        controls_layout.addWidget(QLabel("Lectures:"))
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 40)
        self.spin_count.setValue(5)
        self.spin_count.valueChanged.connect(self._run_simulation)
        controls_layout.addWidget(self.spin_count, 1)

        calc_layout.addLayout(controls_layout)

        self.sim_result_lbl = QLabel("Select parameters above to preview simulated attendance outcome.")
        self.sim_result_lbl.setStyleSheet("""
            background-color: #0F172A;
            border-left: 3px solid #10B981;
            padding: 10px 14px;
            border-radius: 6px;
            font-weight: 600;
            color: #F8FAFC;
        """)
        calc_layout.addWidget(self.sim_result_lbl)
        self.content_layout.addWidget(calc_card)

        # 3. Subject Cards Grid
        grid_title = QLabel("Course-Wise Attendance Breakdown")
        grid_title.setStyleSheet("font-size: 15px; font-weight: 700; margin-top: 6px;")
        self.content_layout.addWidget(grid_title)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(14)
        self.content_layout.addLayout(self.cards_grid)

        # 4. Lecture History Logs Table
        log_title = QLabel("Recent Attendance Logs & Verification Records")
        log_title.setStyleSheet("font-size: 15px; font-weight: 700; margin-top: 10px;")
        self.content_layout.addWidget(log_title)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Date", "Time Slot", "Course Code", "Status", "Topic Covered"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.log_table.setFixedHeight(240)
        self.content_layout.addWidget(self.log_table)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        overview = AcademicController.get_attendance_overview(student.student_id)
        subjects = overview["subjects"]

        # Update metric cards
        self.card_overall.update_value(f"{overview['overall_percentage']:.1f}%")
        self.card_attended.update_value(str(overview["total_attended"]))
        self.card_delivered.update_value(str(overview["total_delivered"]))
        self.card_shortage.update_value(
            f"{overview['shortage_count']} Courses",
            "Attention required" if overview['shortage_count'] > 0 else "All >= 75%"
        )

        # Populate combo box
        self.course_combo.blockSignals(True)
        self.course_combo.clear()
        for s in subjects:
            self.course_combo.addItem(f"{s.subject_code} - {s.subject_name}", userData=s)
        self.course_combo.blockSignals(False)

        # Render Subject Cards in 2-column grid
        self._clear_layout(self.cards_grid)
        for idx, s in enumerate(subjects):
            row = idx // 2
            col = idx % 2
            card = AttendanceSubjectCard(
                subject_code=s.subject_code,
                subject_name=s.subject_name,
                attended=s.effective_attended,
                delivered=s.total_delivered,
                percentage=s.calculated_percentage,
                safe_skips=s.safe_skips(75.0),
                needed=s.lectures_needed(75.0)
            )
            self.cards_grid.addWidget(card, row, col)

        # Populate Lecture Logs
        logs = AcademicController.get_attendance_logs(student.student_id, limit=30)
        self.log_table.setRowCount(len(logs))
        for row_idx, log in enumerate(logs):
            self.log_table.setItem(row_idx, 0, QTableWidgetItem(log.lecture_date))
            self.log_table.setItem(row_idx, 1, QTableWidgetItem(log.time_slot))
            self.log_table.setItem(row_idx, 2, QTableWidgetItem(log.subject_code))

            status_item = QTableWidgetItem(log.status)
            if log.status == "Present":
                status_item.setForeground(Qt.GlobalColor.green)
            elif log.status == "Absent":
                status_item.setForeground(Qt.GlobalColor.red)
            else:
                status_item.setForeground(Qt.GlobalColor.yellow)

            self.log_table.setItem(row_idx, 3, status_item)
            self.log_table.setItem(row_idx, 4, QTableWidgetItem(log.topic_covered or "-"))

        self._run_simulation()

    def _run_simulation(self):
        s_obj = self.course_combo.currentData()
        if not s_obj:
            return

        is_attending = (self.action_combo.currentIndex() == 0)
        count = self.spin_count.value()

        curr_att = s_obj.effective_attended
        curr_del = s_obj.total_delivered
        curr_pct = s_obj.calculated_percentage

        if is_attending:
            new_att = curr_att + count
            new_del = curr_del + count
            new_pct = round((new_att * 100.0) / new_del, 2)
            delta = round(new_pct - curr_pct, 2)
            sign = f"+{delta}" if delta >= 0 else str(delta)
            status_text = "PASSED (Safe)" if new_pct >= 75.0 else f"SHORTAGE (Needs {s_obj.lectures_needed(75.0) - count} more)"

            self.sim_result_lbl.setText(
                f"📈 Simulation: Attending next {count} lectures will raise attendance from "
                f"{curr_pct:.2f}% to {new_pct:.2f}% ({sign}%). Status: {status_text}."
            )
        else:
            new_att = curr_att
            new_del = curr_del + count
            new_pct = round((new_att * 100.0) / new_del, 2)
            delta = round(new_pct - curr_pct, 2)
            status_text = "SAFE" if new_pct >= 75.0 else "SHORTAGE RISK TRIGGERED"

            self.sim_result_lbl.setText(
                f"📉 Simulation: Missing next {count} lectures will drop attendance from "
                f"{curr_pct:.2f}% to {new_pct:.2f}% ({delta}%). Status: {status_text}."
            )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
