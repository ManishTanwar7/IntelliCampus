"""
IntelliCampus: Report Controller
Manages document generation, PDF, and Excel reporting.
"""
from typing import Optional
from services.export_service import ExportService

class ReportController:

    @classmethod
    def generate_pdf_report(cls, student_id: str, destination_path: Optional[str] = None) -> str:
        return ExportService.export_pdf(student_id, destination_path)

    @classmethod
    def generate_excel_report(cls, student_id: str, destination_path: Optional[str] = None) -> str:
        return ExportService.export_excel(student_id, destination_path)
