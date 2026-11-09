"""
IntelliCampus: UIMS Sync Controller & Worker
Executes Playwright scraping on a background thread while delegating
CAPTCHA presentation and manual input safely to the PyQt6 main thread.
"""
import threading
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from services.uims_scraper import UIMSScraper
from controllers.auth_controller import AuthController

class UIMSSyncWorker(QThread):
    status_updated = pyqtSignal(str)
    captcha_requested = pyqtSignal(bytes)  # Emits raw CAPTCHA image bytes to UI
    sync_completed = pyqtSignal(dict)
    sync_failed = pyqtSignal(str)

    def __init__(self, username: str, password: str, demo_mode: bool = False, headless: bool = False):
        super().__init__()
        self.username = username
        self.password = password
        self.demo_mode = demo_mode
        self.headless = headless
        self._captcha_event = threading.Event()
        self._user_captcha_response: Optional[str] = None
        self._scraper = UIMSScraper(demo_mode=self.demo_mode, headless=self.headless)

    def provide_captcha_solution(self, solution: Optional[str]):
        """Called by UI thread when user enters CAPTCHA or cancels."""
        self._user_captcha_response = solution
        self._captcha_event.set()

    def _captcha_callback(self, captcha_bytes: bytes) -> Optional[str]:
        """
        Invoked by scraper when CAPTCHA is detected.
        Halts the background thread until the UI user enters manual solution.
        """
        self._captcha_event.clear()
        self._user_captcha_response = None
        self.captcha_requested.emit(captcha_bytes)
        # Wait indefinitely for user to enter CAPTCHA or cancel
        self._captcha_event.wait()
        return self._user_captcha_response

    def run(self):
        try:
            self.status_updated.emit("Starting UIMS Synchronizer...")
            result = self._scraper.authenticate_and_sync(
                username=self.username,
                password=self.password,
                captcha_resolver_callback=self._captcha_callback,
                status_callback=lambda msg: self.status_updated.emit(msg)
            )

            if result.get("success"):
                # Save credentials if successful
                student = AuthController.get_current_student()
                if student:
                    AuthController.save_credentials(student.student_id, self.username, self.password, remember=True)
                self.sync_completed.emit(result)
            else:
                self.sync_failed.emit(result.get("error", "Unknown sync error."))

        except Exception as e:
            self.sync_failed.emit(f"Sync failed unexpectedly: {str(e)}")
