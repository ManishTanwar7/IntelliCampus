"""
IntelliCampus: Main Application Entry Point
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config import APP_NAME
from services.database import DatabaseManager
from services.notification_service import NotificationService
from controllers.auth_controller import AuthController
from views.components.theme import ThemeManager
from views.main_window import MainWindow

def main():
    # Enable High DPI scaling
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # Initialize Database & verify schema/seed data
    print("[IntelliCampus] Initializing database engine...")
    db = DatabaseManager()

    # Run system health checks (check for low attendance alerts, assignment deadlines)
    student = AuthController.get_current_student()
    if student:
        print(f"[IntelliCampus] Active student loaded: {student.full_name} ({student.student_id})")
        NotificationService.run_system_health_checks(student.student_id)

    # Apply default dark theme
    ThemeManager.apply_theme(app, "dark")

    # Launch Main Window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
