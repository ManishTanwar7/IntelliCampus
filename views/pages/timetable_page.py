"""
IntelliCampus: Timetable Management View
Day-wise weekly schedule view, room allocations, faculty info, and lab tracking.
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

from controllers.auth_controller import AuthController
from controllers.academic_controller import AcademicController

class TimetablePage(QWidget):
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title and Today Quick Button
        header_layout = QHBoxLayout()
        title = QLabel("Weekly Academic Timetable")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.today_btn = QPushButton("Jump to Today")
        self.today_btn.setProperty("class", "PrimaryButton")
        self.today_btn.clicked.connect(self._select_today)
        header_layout.addWidget(self.today_btn)
        main_layout.addLayout(header_layout)

        # Tab Widget for Days
        self.tabs = QTabWidget()
        for day in self.DAYS:
            tab_page = self._create_day_tab(day)
            self.tabs.addTab(tab_page, day)

        main_layout.addWidget(self.tabs)
        self._select_today()

    def _create_day_tab(self, day: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        table = QTableWidget()
        table.setObjectName(f"table_{day}")
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Time Slot", "Course Code", "Subject Name", "Room / Lab", "Faculty Instructor", "Type"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(table)
        return widget

    def _select_today(self):
        today_name = datetime.now().strftime("%A")
        if today_name in self.DAYS:
            idx = self.DAYS.index(today_name)
            self.tabs.setCurrentIndex(idx)
        else:
            self.tabs.setCurrentIndex(0)

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        for idx, day in enumerate(self.DAYS):
            table = self.tabs.widget(idx).findChild(QTableWidget, f"table_{day}")
            if not table:
                continue

            entries = AcademicController.get_timetable(student.student_id, day=day)
            table.setRowCount(len(entries))

            for row_idx, e in enumerate(entries):
                table.setItem(row_idx, 0, QTableWidgetItem(e.formatted_time))
                table.setItem(row_idx, 1, QTableWidgetItem(e.subject_code))
                table.setItem(row_idx, 2, QTableWidgetItem(e.subject_name))
                table.setItem(row_idx, 3, QTableWidgetItem(e.room_no or "TBA"))
                table.setItem(row_idx, 4, QTableWidgetItem(e.faculty_name or "TBA"))

                type_item = QTableWidgetItem("Lab / Practical" if e.is_lab else "Theory")
                if e.is_lab:
                    type_item.setForeground(Qt.GlobalColor.cyan)
                table.setItem(row_idx, 5, type_item)
