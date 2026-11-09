"""
IntelliCampus: Main Application Window
Collegia-inspired modern desktop UI featuring responsive sidebar navigation,
dynamic top bar with notification center, and stacked module pages.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from config import APP_NAME, APP_SUBTITLE, APP_VERSION
from controllers.auth_controller import AuthController
from services.notification_service import NotificationService
from views.components.theme import ThemeManager

# Pages
from views.pages.dashboard_page import DashboardPage
from views.pages.attendance_page import AttendancePage
from views.pages.marks_page import MarksPage
from views.pages.timetable_page import TimetablePage
from views.pages.productivity_page import ProductivityPage
from views.pages.analytics_page import AnalyticsPage
from views.pages.reports_page import ReportsPage
from views.pages.settings_page import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_SUBTITLE} (v{APP_VERSION})")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 680)

        self._nav_buttons = {}
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar Navigation
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # 2. Right Content Area (Top Header + Stacked Pages)
        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Header Bar
        header = self._create_top_header()
        right_layout.addWidget(header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self._init_pages()
        right_layout.addWidget(self.stack)

        main_layout.addWidget(right_area, 1)

        # Select Dashboard by default
        self._switch_page("dashboard")

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("SidebarWidget")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(6)

        # Brand Title
        brand_row = QHBoxLayout()
        icon_box = QLabel("⚡")
        icon_box.setStyleSheet("background-color: #4F46E5; color: white; border-radius: 8px; padding: 4px 8px; font-size: 16px;")
        brand_row.addWidget(icon_box)

        brand_text = QVBoxLayout()
        title = QLabel(APP_NAME)
        title.setObjectName("SidebarTitle")
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setObjectName("SidebarSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        layout.addLayout(brand_row)

        layout.addSpacing(10)

        # Navigation Buttons
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("attendance", "📅  Attendance"),
            ("marks", "📝  Marks & Results"),
            ("timetable", "⏰  Timetable"),
            ("productivity", "⚡  Productivity & Goals"),
            ("analytics", "🤖  AI Analytics"),
            ("reports", "📑  Reports & Exports"),
            ("settings", "⚙️  Settings & Portal")
        ]

        for page_key, label in nav_items:
            btn = QPushButton(label)
            btn.setProperty("class", "NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=page_key: self._switch_page(k))
            self._nav_buttons[page_key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Student Mini Profile Footer
        student = AuthController.get_current_student()
        profile_card = QFrame()
        profile_card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        p_layout = QHBoxLayout(profile_card)
        p_layout.setContentsMargins(8, 8, 8, 8)
        p_layout.setSpacing(10)

        # Avatar Initial Circle
        initials = "AS"
        if student and student.full_name:
            parts = student.full_name.split()
            initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else ""))
        self.avatar_lbl = QLabel(initials)
        self.avatar_lbl.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #06B6D4);
            color: white;
            font-weight: bold;
            font-size: 12px;
            border-radius: 16px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
            qproperty-alignment: AlignCenter;
        """)
        p_layout.addWidget(self.avatar_lbl)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.name_lbl = QLabel(student.full_name if student else "Student User")
        self.name_lbl.setStyleSheet("font-weight: 700; font-size: 12px; color: #F8FAFC;")
        self.uid_lbl = QLabel(f"{student.student_id if student else ''} • Sem {student.semester if student else 2}")
        self.uid_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        info_layout.addWidget(self.name_lbl)
        info_layout.addWidget(self.uid_lbl)
        p_layout.addLayout(info_layout)

        layout.addWidget(profile_card)
        return sidebar

    def _create_top_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("TopHeaderWidget")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self.page_title_lbl = QLabel("Dashboard Overview")
        self.page_title_lbl.setObjectName("HeaderTitle")
        layout.addWidget(self.page_title_lbl)

        layout.addStretch()

        # Student Search Bar
        from PyQt6.QtWidgets import QLineEdit
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search UID (e.g. 25bcs11666)...")
        self.search_box.setFixedWidth(230)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                color: #F8FAFC;
            }
            QLineEdit:focus {
                border: 1px solid #6366F1;
            }
        """)
        self.search_box.returnPressed.connect(self._handle_student_search)
        layout.addWidget(self.search_box)

        self.btn_search = QPushButton("Find")
        self.btn_search.setProperty("class", "SecondaryButton")
        self.btn_search.setFixedWidth(60)
        self.btn_search.clicked.connect(self._handle_student_search)
        layout.addWidget(self.btn_search)

        # Quick Sync UIMS Button
        self.btn_quick_sync = QPushButton("⚡ Sync UIMS")
        self.btn_quick_sync.setProperty("class", "PrimaryButton")
        self.btn_quick_sync.clicked.connect(lambda: self._switch_page("settings"))
        layout.addWidget(self.btn_quick_sync)

        # Notification Bell
        student = AuthController.get_current_student()
        unread_count = NotificationService.get_unread_count(student.student_id) if student else 0
        self.btn_notif = QPushButton(f"🔔 Alerts ({unread_count})")
        self.btn_notif.setProperty("class", "SecondaryButton")
        self.btn_notif.clicked.connect(self._show_notifications_modal)
        layout.addWidget(self.btn_notif)

        # Theme Toggle Button
        self.btn_theme = QPushButton("☀️ Light")
        self.btn_theme.setProperty("class", "SecondaryButton")
        self.btn_theme.clicked.connect(self._toggle_theme)
        layout.addWidget(self.btn_theme)

        return header

    def _init_pages(self):
        self.pages = {
            "dashboard": DashboardPage(),
            "attendance": AttendancePage(),
            "marks": MarksPage(),
            "timetable": TimetablePage(),
            "productivity": ProductivityPage(),
            "analytics": AnalyticsPage(),
            "reports": ReportsPage(),
            "settings": SettingsPage()
        }

        # Wire inter-page navigation signals
        self.pages["dashboard"].navigate_requested.connect(self._switch_page)
        self.pages["settings"].theme_changed.connect(self._apply_theme)
        self.pages["settings"].sync_completed_signal.connect(self._refresh_all_pages)

        for key, page_widget in self.pages.items():
            self.stack.addWidget(page_widget)

    def _switch_page(self, page_key: str):
        if page_key in self.pages:
            idx = list(self.pages.keys()).index(page_key)
            self.stack.setCurrentIndex(idx)

            # Update checked state on nav buttons
            for k, btn in self._nav_buttons.items():
                btn.setChecked(k == page_key)

            # Update page title
            titles = {
                "dashboard": "Dashboard Overview",
                "attendance": "Course-Wise Attendance & Safe Skips",
                "marks": "Assessment Marks & CGPA Progress",
                "timetable": "Weekly Academic Timetable",
                "productivity": "Productivity, Tasks & Goal Tracker",
                "analytics": "AI Academic Analytics & Predictor",
                "reports": "Academic Dossier & Summary Reports",
                "settings": "System Settings & Portal Connection"
            }
            self.page_title_lbl.setText(titles.get(page_key, "IntelliCampus"))

            # Refresh data on active page
            active_page = self.pages[page_key]
            if hasattr(active_page, "refresh_data"):
                active_page.refresh_data()

    def _refresh_all_pages(self):
        for page in self.pages.values():
            if hasattr(page, "refresh_data"):
                page.refresh_data()

    def _toggle_theme(self):
        curr = ThemeManager.get_current_theme()
        new_theme = "light" if curr == "dark" else "dark"
        self._apply_theme(new_theme)

    def _apply_theme(self, theme_name: str):
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, theme_name)
        if theme_name == "dark":
            self.btn_theme.setText("☀️ Light")
        else:
            self.btn_theme.setText("🌙 Dark")

    def _show_notifications_modal(self):
        student = AuthController.get_current_student()
        if not student:
            return

        notifs = NotificationService.get_notifications(student.student_id, limit=10)
        dialog = QDialog(self)
        dialog.setWindowTitle("Active Academic Alerts & Notifications")
        dialog.setFixedSize(480, 400)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(18, 18, 18, 18)
        d_layout.setSpacing(10)

        d_title = QLabel("System & Academic Notifications")
        d_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        d_layout.addWidget(d_title)

        if notifs:
            for n in notifs:
                box = QFrame()
                box.setStyleSheet("background-color: #1E293B; border-radius: 6px; padding: 8px 10px;")
                b_layout = QVBoxLayout(box)
                b_layout.setContentsMargins(6, 6, 6, 6)
                
                t_lbl = QLabel(f"<b>{n['title']}</b>")
                b_layout.addWidget(t_lbl)

                m_lbl = QLabel(n['message'])
                m_lbl.setWordWrap(True)
                m_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
                b_layout.addWidget(m_lbl)
                d_layout.addWidget(box)
        else:
            no_lbl = QLabel("No active unread notifications.")
            no_lbl.setStyleSheet("color: #10B981; font-weight: 600;")
            d_layout.addWidget(no_lbl)

        d_layout.addStretch()
        close_btn = QPushButton("Mark All as Read & Close")
        close_btn.setProperty("class", "PrimaryButton")
        close_btn.clicked.connect(lambda: [NotificationService.mark_all_as_read(student.student_id), dialog.accept(), self.btn_notif.setText("🔔 Alerts (0)")])
        d_layout.addWidget(close_btn)

        dialog.exec()

    def _handle_student_search(self):
        query = self.search_box.text().strip()
        if not query:
            return

        from models.student import Student
        found = Student.search(query)
        if found:
            AuthController.set_current_student(found)
            self._update_profile_ui(found)
            self._refresh_all_pages()
            self.search_box.clear()
            QMessageBox.information(
                self, "Student Found",
                f"Loaded record for: {found.full_name} ({found.student_id})\nProgram: {found.program}\nSemester: {found.semester}"
            )
        else:
            QMessageBox.warning(
                self, "Not Found",
                f"No student record found matching '{query}'.\nTip: You can search '25bcs11666', '21bcs7492', or student names."
            )

    def _update_profile_ui(self, student):
        if not student:
            return
        parts = student.full_name.split()
        initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else ""))
        self.avatar_lbl.setText(initials)
        self.name_lbl.setText(student.full_name)
        self.uid_lbl.setText(f"{student.student_id} • Sem {student.semester}")
        unread_count = NotificationService.get_unread_count(student.student_id)
        self.btn_notif.setText(f"🔔 Alerts ({unread_count})")
