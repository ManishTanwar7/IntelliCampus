"""
IntelliCampus: AI Analytics & Academic Forecast View
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt

from controllers.auth_controller import AuthController
from controllers.analytics_controller import AnalyticsController
from views.components.cards import MetricCard

class AnalyticsPage(QWidget):
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

        # Header Title with Refresh Button
        header = QHBoxLayout()
        title = QLabel("AI Academic Analytics & Predictive Forecaster")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)

        header.addStretch()

        self.recompute_btn = QPushButton("⚡ Recompute Predictions")
        self.recompute_btn.setProperty("class", "PrimaryButton")
        self.recompute_btn.clicked.connect(self._recompute)
        header.addWidget(self.recompute_btn)
        self.content_layout.addLayout(header)

        # 1. Top Predictive Metric Cards
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(14)
        self.card_cgpa = MetricCard("Predicted CGPA", "0.00", "Regression Model Confidence: 92%", "#6366F1")
        self.card_shortage = MetricCard("Shortage Risk", "0 Courses", "Projected to drop < 75%", "#EF4444")
        self.card_weak = MetricCard("Weakest Subject", "None", "Composite deficit score", "#F59E0B")
        self.card_buffer = MetricCard("Max Safe Skips", "0 Classes", "Available across courses", "#10B981")

        metrics_layout.addWidget(self.card_cgpa)
        metrics_layout.addWidget(self.card_shortage)
        metrics_layout.addWidget(self.card_weak)
        metrics_layout.addWidget(self.card_buffer)
        self.content_layout.addLayout(metrics_layout)

        # 2. Attendance Shortage Risk Forecaster Section
        risk_box = QFrame()
        risk_box.setProperty("class", "CardFrame")
        risk_l = QVBoxLayout(risk_box)
        risk_title = QLabel("🚨 Attendance Shortage Risk & Projected Trajectory")
        risk_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #EF4444;")
        risk_l.addWidget(risk_title)

        self.risk_container = QVBoxLayout()
        risk_l.addLayout(self.risk_container)
        self.content_layout.addWidget(risk_box)

        # 3. Weak Subject Deficit Detector Section
        weak_box = QFrame()
        weak_box.setProperty("class", "CardFrame")
        weak_l = QVBoxLayout(weak_box)
        weak_title = QLabel("🔍 Weak Subject Diagnostic & Assessment Deficits")
        weak_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #F59E0B;")
        weak_l.addWidget(weak_title)

        self.weak_container = QVBoxLayout()
        weak_l.addLayout(self.weak_container)
        self.content_layout.addWidget(weak_box)

        # 4. Actionable AI Recommendations
        rec_box = QFrame()
        rec_box.setProperty("class", "CardFrame")
        rec_l = QVBoxLayout(rec_box)
        rec_title = QLabel("💡 Personalized Academic Action Plan")
        rec_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #10B981;")
        rec_l.addWidget(rec_title)

        self.rec_container = QVBoxLayout()
        rec_l.addLayout(self.rec_container)
        self.content_layout.addWidget(rec_box)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.refresh_data()

    def refresh_data(self):
        student = AuthController.get_current_student()
        if not student:
            return

        report = AnalyticsController.get_or_generate_report(student.student_id)
        if not report:
            return

        # 1. Update Metrics
        self.card_cgpa.update_value(f"{report.predicted_cgpa:.2f}")
        shortage_count = len(report.shortage_risk_subjects)
        self.card_shortage.update_value(f"{shortage_count} Courses", "Critical action required" if shortage_count > 0 else "Safe")

        if report.weak_subjects:
            top_w = report.weak_subjects[0]
            self.card_weak.update_value(top_w["subject_code"], f"Risk: {top_w['risk_score']}/100")
        else:
            self.card_weak.update_value("None", "Consistent progress")

        max_skips = max(report.attendance_safe_skips.values()) if report.attendance_safe_skips else 0
        self.card_buffer.update_value(f"{max_skips} Skips", "Safe duty leave buffer")

        # 2. Populate Shortage Risks
        self._clear_layout(self.risk_container)
        if report.shortage_risk_subjects:
            for s in report.shortage_risk_subjects:
                row = QFrame()
                row.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 10px 14px;")
                row_l = QVBoxLayout(row)

                top = QHBoxLayout()
                t_lbl = QLabel(f"<b>{s['subject_code']} - {s['subject_name']}</b>")
                t_lbl.setStyleSheet("font-size: 13px; color: #F87171;")
                top.addWidget(t_lbl)
                top.addStretch()

                stat_badge = QLabel(f"{s['status']} • Current: {s['current_pct']}%")
                stat_badge.setStyleSheet("background-color: rgba(239, 68, 68, 0.2); color: #EF4444; border-radius: 4px; padding: 2px 8px; font-weight: bold;")
                top.addWidget(stat_badge)
                row_l.addLayout(top)

                desc = QLabel(
                    f"Consecutive classes to attend to reach 75%: <b>{s['lectures_needed']} lectures</b>.<br>"
                    f"Projected End-of-Semester Range: <b>{s['projected_worst']}%</b> (if 0 attended) to <b>{s['projected_best']}%</b> (if all attended)."
                )
                desc.setStyleSheet("color: #94A3B8; font-size: 12px; margin-top: 4px;")
                row_l.addWidget(desc)
                self.risk_container.addWidget(row)
        else:
            no_risk = QLabel("✅ No attendance shortage risks detected. All subjects safely above 75%.")
            no_risk.setStyleSheet("color: #10B981; font-weight: 600; padding: 10px;")
            self.risk_container.addWidget(no_risk)

        # 3. Populate Weak Subjects
        self._clear_layout(self.weak_container)
        if report.weak_subjects:
            for w in report.weak_subjects:
                row = QFrame()
                row.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 10px 14px;")
                row_l = QVBoxLayout(row)

                top = QHBoxLayout()
                t_lbl = QLabel(f"<b>{w['subject_code']} - {w['subject_name']}</b>")
                t_lbl.setStyleSheet("font-size: 13px; color: #FBBF24;")
                top.addWidget(t_lbl)
                top.addStretch()

                risk_lbl = QLabel(f"Deficit Score: {w['risk_score']}/100")
                risk_lbl.setStyleSheet("color: #F59E0B; font-weight: bold;")
                top.addWidget(risk_lbl)
                row_l.addLayout(top)

                reasons_text = " • ".join(w["reasons"])
                r_lbl = QLabel(f"Flags: {reasons_text} | Avg Marks: {w['avg_marks_pct']}% | Attendance: {w['attendance_pct']}%")
                r_lbl.setStyleSheet("color: #94A3B8; font-size: 12px; margin-top: 4px;")
                row_l.addWidget(r_lbl)
                self.weak_container.addWidget(row)
        else:
            no_weak = QLabel("✅ Performance is balanced across all courses.")
            no_weak.setStyleSheet("color: #10B981; font-weight: 600; padding: 10px;")
            self.weak_container.addWidget(no_weak)

        # 4. Populate Recommendations
        self._clear_layout(self.rec_container)
        for rec in report.recommendations:
            box = QLabel(rec)
            box.setWordWrap(True)
            box.setStyleSheet("background-color: #0F172A; border-left: 3px solid #10B981; border-radius: 4px; padding: 10px; font-size: 13px;")
            self.rec_container.addWidget(box)

    def _recompute(self):
        student = AuthController.get_current_student()
        if student:
            AnalyticsController.get_or_generate_report(student.student_id, force_refresh=True)
            self.refresh_data()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
