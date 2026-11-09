"""
IntelliCampus: Comprehensive Test Suite
Validates Database, Models, AI Analytics Engine, Security, and Reporting.
"""
import unittest
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.database import DatabaseManager
from services.security_service import SecurityService
from services.ai_analytics_service import AIAnalyticsEngine
from services.export_service import ExportService
from services.uims_scraper import UIMSScraper
from models.student import Student
from models.attendance import SubjectAttendance
from models.marks import MarkItem, SemesterResult
from controllers.academic_controller import AcademicController

class TestIntelliCampus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize Database Manager
        cls.db = DatabaseManager()

    def test_01_database_and_student_seed(self):
        """Verifies database initialization and seeded student."""
        student = Student.get_first_or_default()
        self.assertIsNotNone(student, "Student should be seeded")
        self.assertEqual(student.student_id, "21BCS7492")
        self.assertEqual(student.full_name, "Aarav Sharma")
        print(f"[PASS] Test 1 Passed: Seed student {student.full_name} loaded.")

    def test_02_attendance_calculations(self):
        """Validates attendance percentages, safe skips, and recovery streaks."""
        student = Student.get_first_or_default()
        overview = AcademicController.get_attendance_overview(student.student_id)
        self.assertGreater(overview["overall_percentage"], 0.0)
        self.assertGreaterEqual(len(overview["subjects"]), 5)

        # Check shortage course (21CS504)
        ml_course = next((s for s in overview["subjects"] if s.subject_code == "21CS504"), None)
        self.assertIsNotNone(ml_course)
        self.assertLess(ml_course.calculated_percentage, 75.0, "21CS504 should be below 75% for AI test")
        needed = ml_course.lectures_needed(75.0)
        self.assertGreater(needed, 0, "Recovery streak must be > 0 when below 75%")
        print(f"[PASS] Test 2 Passed: 21CS504 attendance {ml_course.calculated_percentage}% requires {needed} consecutive lectures.")

        # Check high-attendance course (21CS501)
        algo_course = next((s for s in overview["subjects"] if s.subject_code == "21CS501"), None)
        self.assertIsNotNone(algo_course)
        self.assertGreaterEqual(algo_course.calculated_percentage, 75.0)
        skips = algo_course.safe_skips(75.0)
        self.assertGreater(skips, 0, "Safe skips must be > 0 when well above 75%")
        print(f"[PASS] Test 2b Passed: 21CS501 attendance {algo_course.calculated_percentage}% allows {skips} safe skips.")

    def test_03_credential_encryption(self):
        """Validates AES-Fernet encryption, salt generation, and decryption."""
        plain = "MySecretPortalPass#2026"
        encrypted, salt = SecurityService.encrypt_password(plain)
        self.assertNotEqual(plain, encrypted)
        decrypted = SecurityService.decrypt_password(encrypted, salt)
        self.assertEqual(plain, decrypted)
        print("[PASS] Test 3 Passed: AES-Fernet password encryption and decryption matched perfectly.")

    def test_04_ai_analytics_engine(self):
        """Validates AI predictions for shortage, CGPA forecast, and weak subjects."""
        student = Student.get_first_or_default()
        report = AIAnalyticsEngine.analyze_student(student.student_id)
        self.assertIsNotNone(report)
        self.assertGreater(report.predicted_cgpa, 7.0)
        self.assertLessEqual(report.predicted_cgpa, 10.0)

        # Ensure weak subject detected
        self.assertGreater(len(report.weak_subjects), 0)
        self.assertEqual(report.weak_subjects[0]["subject_code"], "21CS504")

        # Ensure shortage course identified
        self.assertGreater(len(report.shortage_risk_subjects), 0)
        self.assertEqual(report.shortage_risk_subjects[0]["subject_code"], "21CS504")

        # Ensure recommendations generated
        self.assertGreater(len(report.recommendations), 2)
        print(f"[PASS] Test 4 Passed: AI Predicted CGPA = {report.predicted_cgpa}, Weak Subject = {report.weak_subjects[0]['subject_code']}")

    def test_05_pdf_and_excel_exports(self):
        """Validates PDF and Excel generation without errors."""
        student = Student.get_first_or_default()
        pdf_path = ExportService.export_pdf(student.student_id)
        self.assertTrue(os.path.exists(pdf_path), "PDF file should exist")
        self.assertGreater(os.path.getsize(pdf_path), 1000, "PDF should have content")

        excel_path = ExportService.export_excel(student.student_id)
        self.assertTrue(os.path.exists(excel_path), "Excel file should exist")
        self.assertGreater(os.path.getsize(excel_path), 1000, "Excel should have content")
        print(f"[PASS] Test 5 Passed: Successfully generated PDF ({os.path.getsize(pdf_path)} bytes) and Excel ({os.path.getsize(excel_path)} bytes).")

    def test_06_captcha_manual_resolver_compliance(self):
        """
        Validates safety compliance: system never bypasses CAPTCHA,
        invokes the resolver callback with image bytes, and consumes the manual entry.
        """
        scraper = UIMSScraper(demo_mode=True)
        captcha_received = []

        def mock_ui_captcha_resolver(img_bytes: bytes) -> str:
            self.assertGreater(len(img_bytes), 100, "Must receive valid CAPTCHA image bytes")
            captcha_received.append(True)
            return "TESTC"

        # Test with wrong captcha first
        res_fail = scraper.authenticate_and_sync("21BCS7492", "pwd", mock_ui_captcha_resolver)
        self.assertFalse(res_fail["success"])
        self.assertTrue(captcha_received[0], "CAPTCHA modal must have been presented to user")
        print("[PASS] Test 6 Passed: CAPTCHA safety verified - challenge presented to user and manual entry required.")

if __name__ == "__main__":
    unittest.main()
