"""
IntelliCampus: Custom UI Cards & Metric Widgets
Collegia-style cards, progress bars, and status pills.
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MetricCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = "", accent_color: str = "#6366F1", parent=None):
        super().__init__(parent)
        self.setProperty("class", "MetricCard")
        self.setStyleSheet(f"""
            QFrame.MetricCard {{
                border-left: 4px solid {accent_color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        layout.addWidget(self.title_label)

        # Metric Value
        self.val_label = QLabel(value)
        self.val_label.setProperty("class", "MetricValue")
        layout.addWidget(self.val_label)

        # Subtitle / Delta
        if subtitle:
            self.sub_label = QLabel(subtitle)
            self.sub_label.setProperty("class", "MetricSubtitle")
            layout.addWidget(self.sub_label)

    def update_value(self, new_val: str, new_subtitle: str = ""):
        self.val_label.setText(new_val)
        if new_subtitle and hasattr(self, 'sub_label'):
            self.sub_label.setText(new_subtitle)


class AttendanceSubjectCard(QFrame):
    def __init__(self, subject_code: str, subject_name: str, attended: int, delivered: int, percentage: float, safe_skips: int, needed: int, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Header: Subject Code & Status Badge
        header = QHBoxLayout()
        code_lbl = QLabel(f"<b>{subject_code}</b>")
        code_lbl.setStyleSheet("font-size: 14px; color: #818CF8;")
        header.addWidget(code_lbl)

        header.addStretch()

        # Status Badge Pill
        status_lbl = QLabel()
        if percentage >= 80.0:
            status_lbl.setText(f"SAFE • {safe_skips} skips left")
            status_lbl.setStyleSheet("background-color: rgba(16, 185, 129, 0.2); color: #10B981; border-radius: 12px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        elif percentage >= 75.0:
            status_lbl.setText(f"BORDERLINE • {safe_skips} skips left")
            status_lbl.setStyleSheet("background-color: rgba(245, 158, 11, 0.2); color: #F59E0B; border-radius: 12px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        else:
            status_lbl.setText(f"SHORTAGE • Attend {needed} more")
            status_lbl.setStyleSheet("background-color: rgba(239, 68, 68, 0.2); color: #EF4444; border-radius: 12px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        header.addWidget(status_lbl)
        layout.addLayout(header)

        # Subject Title
        name_lbl = QLabel(subject_name)
        name_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #F8FAFC;")
        layout.addWidget(name_lbl)

        # Progress & Attendance Stats
        stats_layout = QHBoxLayout()
        stats_lbl = QLabel(f"{attended} attended / {delivered} delivered")
        stats_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        stats_layout.addWidget(stats_lbl)

        stats_layout.addStretch()

        pct_lbl = QLabel(f"<b>{percentage:.1f}%</b>")
        pct_lbl.setStyleSheet("font-size: 15px; font-weight: 700;")
        stats_layout.addWidget(pct_lbl)
        layout.addLayout(stats_layout)

        # Progress Bar
        bar = QProgressBar()
        bar.setMaximum(100)
        bar.setValue(min(100, int(percentage)))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        if percentage >= 80.0:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #10B981; border-radius: 4px; }")
        elif percentage >= 75.0:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #F59E0B; border-radius: 4px; }")
        else:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #EF4444; border-radius: 4px; }")
        layout.addWidget(bar)
