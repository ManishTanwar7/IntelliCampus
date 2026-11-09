"""
IntelliCampus: Student Productivity Suite
Assignment Tracker, Task Manager, Goal Tracker, and Study Planner.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QCheckBox, QProgressBar, QSpinBox
)
from PyQt6.QtCore import Qt

from controllers.auth_controller import AuthController
from controllers.productivity_controller import ProductivityController
from controllers.academic_controller import AcademicController

class ProductivityPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        header = QLabel("Student Productivity & Goal Suite")
        header.setStyleSheet("font-size: 18px; font-weight: 700;")
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._init_assignments_tab(), "📝 Assignment Tracker")
        self.tabs.addTab(self._init_tasks_tab(), "✅ Task Manager")
        self.tabs.addTab(self._init_goals_tab(), "🎯 Academic Goals")
        self.tabs.addTab(self._init_planner_tab(), "📅 Study Planner")

        main_layout.addWidget(self.tabs)
        self.refresh_data()

    # --- 1. Assignments Tab ---
    def _init_assignments_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Assignment Table
        self.asg_table = QTableWidget()
        self.asg_table.setColumnCount(6)
        self.asg_table.setHorizontalHeaderLabels(["Subject", "Title", "Due Date", "Max Marks", "Score", "Status"])
        self.asg_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.asg_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.asg_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.asg_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.asg_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.asg_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.asg_table)

        # Quick Add Assignment Bar
        add_card = QFrame()
        add_card.setProperty("class", "CardFrame")
        add_layout = QHBoxLayout(add_card)
        add_layout.setContentsMargins(10, 10, 10, 10)
        add_layout.setSpacing(10)

        self.asg_course_combo = QComboBox()
        self.asg_title_input = QLineEdit()
        self.asg_title_input.setPlaceholderText("Assignment Title...")
        self.asg_due_input = QLineEdit()
        self.asg_due_input.setPlaceholderText("Due Date (YYYY-MM-DD)")
        self.asg_due_input.setText("2026-11-25")

        asg_add_btn = QPushButton("+ Add Assignment")
        asg_add_btn.setProperty("class", "PrimaryButton")
        asg_add_btn.clicked.connect(self._handle_add_assignment)

        add_layout.addWidget(QLabel("Course:"))
        add_layout.addWidget(self.asg_course_combo)
        add_layout.addWidget(self.asg_title_input, 2)
        add_layout.addWidget(self.asg_due_input, 1)
        add_layout.addWidget(asg_add_btn)
        layout.addWidget(add_card)

        return widget

    # --- 2. Tasks Tab ---
    def _init_tasks_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Quick Add Task Bar
        task_add_card = QFrame()
        task_add_card.setProperty("class", "CardFrame")
        t_add_layout = QHBoxLayout(task_add_card)
        t_add_layout.setContentsMargins(10, 10, 10, 10)
        t_add_layout.setSpacing(10)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("What do you need to study or complete next?")
        self.task_cat_combo = QComboBox()
        self.task_cat_combo.addItems(["Study", "Assignment", "Exam", "Project", "General"])
        self.task_prio_combo = QComboBox()
        self.task_prio_combo.addItems(["High", "Medium", "Low"])

        t_btn = QPushButton("+ Add Task")
        t_btn.setProperty("class", "PrimaryButton")
        t_btn.clicked.connect(self._handle_add_task)

        t_add_layout.addWidget(self.task_input, 2)
        t_add_layout.addWidget(self.task_cat_combo)
        t_add_layout.addWidget(self.task_prio_combo)
        t_add_layout.addWidget(t_btn)
        layout.addWidget(task_add_card)

        # Task List Area
        self.task_scroll = QScrollArea()
        self.task_scroll.setWidgetResizable(True)
        self.task_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.task_container = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_container)
        self.task_list_layout.setContentsMargins(0, 0, 0, 0)
        self.task_list_layout.setSpacing(8)
        self.task_scroll.setWidget(self.task_container)
        layout.addWidget(self.task_scroll)

        return widget

    # --- 3. Goals Tab ---
    def _init_goals_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        self.goals_layout = QVBoxLayout(container)
        self.goals_layout.setContentsMargins(0, 0, 0, 0)
        self.goals_layout.setSpacing(12)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return widget

    # --- 4. Study Planner Tab ---
    def _init_planner_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(5)
        self.plan_table.setHorizontalHeaderLabels(["Scheduled Date", "Time", "Subject", "Duration", "Topic to Master"])
        self.plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.plan_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.plan_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.plan_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.plan_table)

        return widget

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        # Populate Course combo for assignments
        subjects = AcademicController.get_all_subjects()
        self.asg_course_combo.clear()
        for s in subjects:
            self.asg_course_combo.addItem(s.subject_code, userData=s.subject_code)

        # 1. Populate Assignments
        assignments = ProductivityController.get_assignments(student.student_id)
        self.asg_table.setRowCount(len(assignments))
        for row_idx, a in enumerate(assignments):
            self.asg_table.setItem(row_idx, 0, QTableWidgetItem(a.subject_code))
            self.asg_table.setItem(row_idx, 1, QTableWidgetItem(a.title))
            self.asg_table.setItem(row_idx, 2, QTableWidgetItem(a.due_date[:16]))
            self.asg_table.setItem(row_idx, 3, QTableWidgetItem(f"{a.max_marks:.0f}"))
            self.asg_table.setItem(row_idx, 4, QTableWidgetItem(f"{a.marks_awarded:.1f}" if a.marks_awarded is not None else "-"))

            status_item = QTableWidgetItem(a.status)
            if a.status == "Graded" or a.status == "Submitted":
                status_item.setForeground(Qt.GlobalColor.green)
            elif a.status == "In Progress":
                status_item.setForeground(Qt.GlobalColor.yellow)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.asg_table.setItem(row_idx, 5, status_item)

        # 2. Populate Tasks
        self._clear_layout(self.task_list_layout)
        tasks = ProductivityController.get_tasks(student.student_id)
        for t in tasks:
            row = QFrame()
            row.setProperty("class", "CardFrame")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(12, 10, 12, 10)

            chk = QCheckBox()
            chk.setChecked(t.is_completed)
            chk.toggled.connect(lambda state, tid=t.task_id: self._toggle_task(tid, state))
            r_layout.addWidget(chk)

            title_lbl = QLabel(t.title)
            if t.is_completed:
                title_lbl.setStyleSheet("color: #64748B; text-decoration: line-through; font-size: 13px;")
            else:
                title_lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
            r_layout.addWidget(title_lbl, 1)

            cat_lbl = QLabel(t.category)
            cat_lbl.setStyleSheet("background-color: #334155; color: #CBD5E1; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
            r_layout.addWidget(cat_lbl)

            prio_lbl = QLabel(t.priority)
            if t.priority == "High":
                prio_lbl.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 11px;")
            elif t.priority == "Medium":
                prio_lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11px;")
            else:
                prio_lbl.setStyleSheet("color: #10B981; font-size: 11px;")
            r_layout.addWidget(prio_lbl)

            self.task_list_layout.addWidget(row)

        # 3. Populate Goals
        self._clear_layout(self.goals_layout)
        goals = ProductivityController.get_goals(student.student_id)
        for g in goals:
            g_card = QFrame()
            g_card.setProperty("class", "CardFrame")
            g_layout = QVBoxLayout(g_card)
            g_layout.setContentsMargins(14, 12, 14, 12)

            top = QHBoxLayout()
            title_l = QLabel(f"<b>{g.title}</b>")
            top.addWidget(title_l)
            top.addStretch()
            val_l = QLabel(f"{g.current_value:.2f} / {g.target_value:.2f} {g.unit}")
            val_l.setStyleSheet("color: #818CF8; font-weight: bold;")
            top.addWidget(val_l)
            g_layout.addLayout(top)

            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(int(g.progress_percentage))
            bar.setFixedHeight(8)
            g_layout.addWidget(bar)
            self.goals_layout.addWidget(g_card)

        # 4. Populate Study Plans
        plans = ProductivityController.get_study_plans(student.student_id)
        self.plan_table.setRowCount(len(plans))
        for row_idx, p in enumerate(plans):
            self.plan_table.setItem(row_idx, 0, QTableWidgetItem(p.scheduled_date))
            self.plan_table.setItem(row_idx, 1, QTableWidgetItem(p.start_time or "18:00"))
            self.plan_table.setItem(row_idx, 2, QTableWidgetItem(f"{p.subject_code} - {p.subject_name}"))
            self.plan_table.setItem(row_idx, 3, QTableWidgetItem(f"{p.duration_minutes} mins"))
            self.plan_table.setItem(row_idx, 4, QTableWidgetItem(p.topic))

    def _handle_add_assignment(self):
        student = AuthController.get_current_student()
        if not student:
            return
        code = self.asg_course_combo.currentText()
        title = self.asg_title_input.text().strip()
        due = self.asg_due_input.text().strip()
        if title:
            ProductivityController.create_assignment(student.student_id, code, title, "", due, 100.0)
            self.asg_title_input.clear()
            self.refresh_data()

    def _handle_add_task(self):
        student = AuthController.get_current_student()
        if not student:
            return
        text = self.task_input.text().strip()
        if text:
            cat = self.task_cat_combo.currentText()
            prio = self.task_prio_combo.currentText()
            ProductivityController.add_task(student.student_id, text, cat, prio)
            self.task_input.clear()
            self.refresh_data()

    def _toggle_task(self, task_id: int, completed: bool):
        ProductivityController.toggle_task_completion(task_id, completed)
        self.refresh_data()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
