"""
IntelliCampus: Reports & Export View
One-click PDF & Excel Academic Dossier generation.
"""
import os
import subprocess
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

from config import EXPORTS_DIR
from controllers.auth_controller import AuthController
from controllers.report_controller import ReportController

class ReportsPage(QWidget):
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

        header = QLabel("Academic Dossier & Summary Reports")
        header.setStyleSheet("font-size: 18px; font-weight: 700;")
        self.content_layout.addWidget(header)

        # Export Action Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # PDF Card
        pdf_card = QFrame()
        pdf_card.setProperty("class", "CardFrame")
        pdf_l = QVBoxLayout(pdf_card)
        pdf_l.setSpacing(10)

        pdf_title = QLabel("📄 Official PDF Academic Dossier")
        pdf_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #818CF8;")
        pdf_desc = QLabel(
            "Generates a formal, printable PDF document featuring student identity, "
            "subject-wise attendance breakdown, internal assessment marks, semester progression, "
            "and AI predictive recommendations."
        )
        pdf_desc.setWordWrap(True)
        pdf_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")

        self.btn_export_pdf = QPushButton("Generate & Download PDF")
        self.btn_export_pdf.setProperty("class", "PrimaryButton")
        self.btn_export_pdf.clicked.connect(self._handle_pdf_export)

        pdf_l.addWidget(pdf_title)
        pdf_l.addWidget(pdf_desc)
        pdf_l.addStretch()
        pdf_l.addWidget(self.btn_export_pdf)
        cards_layout.addWidget(pdf_card)

        # Excel Card
        xls_card = QFrame()
        xls_card.setProperty("class", "CardFrame")
        xls_l = QVBoxLayout(xls_card)
        xls_l.setSpacing(10)

        xls_title = QLabel("📊 Multi-Sheet Excel Workbook")
        xls_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #10B981;")
        xls_desc = QLabel(
            "Generates a multi-tab Microsoft Excel spreadsheet (.xlsx) with dedicated tabs "
            "for Student Overview, Attendance Data, Continuous Assessment Marks, Timetable, "
            "and Assignment Tracking."
        )
        xls_desc.setWordWrap(True)
        xls_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")

        self.btn_export_excel = QPushButton("Generate & Download Excel")
        self.btn_export_excel.setProperty("class", "SuccessButton")
        self.btn_export_excel.clicked.connect(self._handle_excel_export)

        xls_l.addWidget(xls_title)
        xls_l.addWidget(xls_desc)
        xls_l.addStretch()
        xls_l.addWidget(self.btn_export_excel)
        cards_layout.addWidget(xls_card)

        self.content_layout.addLayout(cards_layout)

        # Status Label
        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet("""
            background-color: #0F172A;
            border-left: 3px solid #6366F1;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 13px;
        """)
        self.status_lbl.setVisible(False)
        self.content_layout.addWidget(self.status_lbl)

        # Export Directory History
        hist_title = QLabel("Generated Report Files Archive")
        hist_title.setStyleSheet("font-size: 15px; font-weight: 700; margin-top: 10px;")
        self.content_layout.addWidget(hist_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["File Name", "Type", "Size", "Action"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.setFixedHeight(220)
        self.content_layout.addWidget(self.history_table)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        # Scan EXPORTS_DIR for files
        files = list(EXPORTS_DIR.glob("*.*"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        self.history_table.setRowCount(len(files))
        for idx, f in enumerate(files):
            self.history_table.setItem(idx, 0, QTableWidgetItem(f.name))
            self.history_table.setItem(idx, 1, QTableWidgetItem(f.suffix.upper().replace(".", "")))
            size_kb = round(f.stat().st_size / 1024, 1)
            self.history_table.setItem(idx, 2, QTableWidgetItem(f"{size_kb} KB"))

            open_btn = QPushButton("Open File")
            open_btn.setProperty("class", "SecondaryButton")
            open_btn.clicked.connect(lambda _, path=str(f): self._open_file(path))
            self.history_table.setCellWidget(idx, 3, open_btn)

    def _handle_pdf_export(self):
        student = AuthController.get_current_student()
        if not student:
            return
        self.btn_export_pdf.setEnabled(False)
        self.status_lbl.setText("Generating PDF Academic Dossier with ReportLab...")
        self.status_lbl.setVisible(True)

        try:
            pdf_path = ReportController.generate_pdf_report(student.student_id)
            self.status_lbl.setText(f"✅ PDF successfully generated at: {pdf_path}")
            self.refresh_data()
            self._open_file(pdf_path)
        except Exception as e:
            self.status_lbl.setText(f"❌ PDF export error: {e}")
        finally:
            self.btn_export_pdf.setEnabled(True)

    def _handle_excel_export(self):
        student = AuthController.get_current_student()
        if not student:
            return
        self.btn_export_excel.setEnabled(False)
        self.status_lbl.setText("Generating multi-sheet Excel Workbook with Pandas & OpenPyXL...")
        self.status_lbl.setVisible(True)

        try:
            excel_path = ReportController.generate_excel_report(student.student_id)
            self.status_lbl.setText(f"✅ Excel workbook successfully generated at: {excel_path}")
            self.refresh_data()
            self._open_file(excel_path)
        except Exception as e:
            self.status_lbl.setText(f"❌ Excel export error: {e}")
        finally:
            self.btn_export_excel.setEnabled(True)

    def _open_file(self, file_path: str):
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            print(f"[ReportsPage] Could not open file: {e}")
