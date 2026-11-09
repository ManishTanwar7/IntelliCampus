"""
IntelliCampus: Settings & UIMS Portal Configuration View
"""
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QLineEdit, QCheckBox, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from config import DB_CONFIG, UIMS_CONFIG, ACADEMIC_RULES
from controllers.auth_controller import AuthController
from controllers.uims_sync_controller import UIMSSyncWorker
from views.components.captcha_dialog import CaptchaDialog
from views.components.theme import ThemeManager

class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)
    sync_completed_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker: Optional[UIMSSyncWorker] = None
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

        header = QLabel("System Settings & Portal Configuration")
        header.setStyleSheet("font-size: 18px; font-weight: 700;")
        self.content_layout.addWidget(header)

        # 1. UIMS Credentials & Sync Card
        uims_card = QFrame()
        uims_card.setProperty("class", "CardFrame")
        uims_l = QVBoxLayout(uims_card)
        uims_l.setSpacing(12)

        uims_title = QLabel("🔐 UIMS Portal Credentials & Synchronizer")
        uims_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #818CF8;")
        uims_l.addWidget(uims_title)

        uims_desc = QLabel(
            "Configure user credentials for university synchronization. "
            "Passwords are encrypted locally using AES-Fernet encryption. "
            "Security Policy: The system NEVER bypasses CAPTCHA. If CAPTCHA appears, "
            "it will be displayed in an interactive dialog for manual entry."
        )
        uims_desc.setWordWrap(True)
        uims_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        uims_l.addWidget(uims_desc)

        cred_grid = QVBoxLayout()
        cred_grid.setSpacing(8)

        # UID
        h_uid = QHBoxLayout()
        h_uid.addWidget(QLabel("UIMS User ID:"), 1)
        self.uid_input = QLineEdit()
        self.uid_input.setPlaceholderText("e.g. 21BCS7492")
        h_uid.addWidget(self.uid_input, 2)
        cred_grid.addLayout(h_uid)

        # Password
        h_pwd = QHBoxLayout()
        h_pwd.addWidget(QLabel("Portal Password:"), 1)
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("••••••••••••")
        h_pwd.addWidget(self.pwd_input, 2)
        cred_grid.addLayout(h_pwd)

        # Options
        h_opts = QHBoxLayout()
        self.chk_remember = QCheckBox("Securely remember credentials (AES encrypted)")
        self.chk_remember.setChecked(True)
        h_opts.addWidget(self.chk_remember)

        self.chk_demo = QCheckBox("Simulation / Demo Mode (Test manual CAPTCHA offline)")
        self.chk_demo.setChecked(True)  # Default checked for instant out-of-the-box verification
        h_opts.addWidget(self.chk_demo)
        cred_grid.addLayout(h_opts)

        uims_l.addLayout(cred_grid)

        # Sync Buttons & Status
        sync_actions = QHBoxLayout()
        self.btn_sync = QPushButton("⚡ Start UIMS Sync with Manual CAPTCHA")
        self.btn_sync.setProperty("class", "PrimaryButton")
        self.btn_sync.clicked.connect(self._start_sync)
        sync_actions.addWidget(self.btn_sync)

        self.sync_status_lbl = QLabel("Ready for synchronization.")
        self.sync_status_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        sync_actions.addWidget(self.sync_status_lbl, 1)

        uims_l.addLayout(sync_actions)
        self.content_layout.addWidget(uims_card)

        # 2. Database Engine & Connection Card
        db_card = QFrame()
        db_card.setProperty("class", "CardFrame")
        db_l = QVBoxLayout(db_card)
        db_l.setSpacing(12)

        db_title = QLabel("🗄️ Database Architecture & Connection Settings")
        db_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #10B981;")
        db_l.addWidget(db_title)

        from services.database import DatabaseManager
        db_mgr = DatabaseManager()
        engine_status = "SQLite Local Mirror (Zero Configuration Mode)" if db_mgr._using_sqlite_fallback else f"MySQL 8.0 Server ({DB_CONFIG['mysql']['host']}:{DB_CONFIG['mysql']['port']})"

        db_info = QLabel(f"<b>Current Active Storage Engine:</b> {engine_status}")
        db_info.setStyleSheet("color: #F8FAFC; font-size: 13px;")
        db_l.addWidget(db_info)

        db_grid = QVBoxLayout()
        db_grid.setSpacing(6)

        h_host = QHBoxLayout()
        h_host.addWidget(QLabel("MySQL Host / IP:"), 1)
        self.mysql_host = QLineEdit(DB_CONFIG["mysql"]["host"])
        h_host.addWidget(self.mysql_host, 2)
        db_grid.addLayout(h_host)

        h_user = QHBoxLayout()
        h_user.addWidget(QLabel("MySQL User & DB:"), 1)
        self.mysql_user = QLineEdit(DB_CONFIG["mysql"]["user"])
        self.mysql_db = QLineEdit(DB_CONFIG["mysql"]["database"])
        h_user.addWidget(self.mysql_user, 1)
        h_user.addWidget(self.mysql_db, 1)
        db_grid.addLayout(h_user)

        db_l.addLayout(db_grid)
        self.content_layout.addWidget(db_card)

        # 3. Theme & Appearance
        theme_card = QFrame()
        theme_card.setProperty("class", "CardFrame")
        theme_l = QVBoxLayout(theme_card)
        theme_l.setSpacing(10)

        theme_title = QLabel("🎨 Theme & Visual Preferences")
        theme_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #F59E0B;")
        theme_l.addWidget(theme_title)

        h_theme = QHBoxLayout()
        h_theme.addWidget(QLabel("Application Theme:"), 1)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme (Collegia Indigo Slate)", "Light Theme (Clean White & Slate)"])
        self.theme_combo.currentIndexChanged.connect(self._handle_theme_change)
        h_theme.addWidget(self.theme_combo, 2)
        theme_l.addLayout(h_theme)

        self.content_layout.addWidget(theme_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        creds = AuthController.get_saved_credentials(student.student_id)
        if creds:
            self.uid_input.setText(creds.get("uims_user_id", ""))
            self.pwd_input.setText(creds.get("password", ""))
            self.sync_status_lbl.setText(f"Last synced: {creds.get('last_sync_at')}")
        else:
            self.uid_input.setText(student.student_id)
            self.pwd_input.setText("Password123*")

    def _start_sync(self):
        uid = self.uid_input.text().strip()
        pwd = self.pwd_input.text().strip()
        if not uid or not pwd:
            QMessageBox.warning(self, "Missing Credentials", "Please enter both UIMS User ID and Password.")
            return

        demo_mode = self.chk_demo.isChecked()
        self.btn_sync.setEnabled(False)
        self.sync_status_lbl.setText("Launching automation worker...")

        # Initialize background worker
        self.worker = UIMSSyncWorker(username=uid, password=pwd, demo_mode=demo_mode, headless=False)
        self.worker.status_updated.connect(self._on_sync_status)
        self.worker.captcha_requested.connect(self._on_captcha_requested)
        self.worker.sync_completed.connect(self._on_sync_completed)
        self.worker.sync_failed.connect(self._on_sync_failed)
        self.worker.start()

    def _on_sync_status(self, msg: str):
        self.sync_status_lbl.setText(msg)

    def _on_captcha_requested(self, image_bytes: bytes):
        """
        Presents the CAPTCHA modal dialog to the user on the main GUI thread.
        Never bypasses CAPTCHA: waits for user's manual entry.
        """
        self.sync_status_lbl.setText("Waiting for manual CAPTCHA entry...")
        user_solution = CaptchaDialog.get_captcha_input(image_bytes, self)
        # Pass manual entry back to the worker
        if self.worker:
            self.worker.provide_captcha_solution(user_solution)

    def _on_sync_completed(self, result: dict):
        self.btn_sync.setEnabled(True)
        self.sync_status_lbl.setText(f"✅ {result.get('message', 'Sync complete!')}")
        QMessageBox.information(self, "Sync Succeeded", result.get("message", "Academic records successfully refreshed."))
        self.sync_completed_signal.emit()

    def _on_sync_failed(self, err: str):
        self.btn_sync.setEnabled(True)
        self.sync_status_lbl.setText(f"❌ Sync Error: {err}")
        QMessageBox.critical(self, "Sync Failed", f"UIMS synchronization could not complete:\n\n{err}")

    def _handle_theme_change(self, idx: int):
        theme_name = "dark" if idx == 0 else "light"
        self.theme_changed.emit(theme_name)
