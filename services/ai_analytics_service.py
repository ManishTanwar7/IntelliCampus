"""
IntelliCampus: AI Analytics & Academic Prediction Engine
Provides intelligent predictions for attendance shortages, future CGPA, weak subject identification,
and personalized study suggestions.
"""
import math
import numpy as np
from typing import Dict, List, Any, Optional
from models.attendance import SubjectAttendance
from models.marks import MarkItem, SemesterResult
from models.subject import Subject
from models.analytics import AnalyticsReport
from config import ACADEMIC_RULES

class AIAnalyticsEngine:

    @classmethod
    def analyze_student(cls, student_id: str) -> AnalyticsReport:
        """
        Executes full predictive pipeline for the student and persists report snapshot.
        """
        attendance_list = SubjectAttendance.get_for_student(student_id)
        marks_list = MarkItem.get_for_student(student_id)
        results_list = SemesterResult.get_for_student(student_id)
        subjects_list = Subject.get_all()

        # 1. Attendance Shortage & Safe Skips
        shortage_risk, safe_skips_map = cls._predict_attendance_risks(attendance_list)

        # 2. Weak Subject Detection
        weak_subjects = cls._detect_weak_subjects(attendance_list, marks_list)

        # 3. Expected CGPA Prediction
        predicted_cgpa = cls._predict_cgpa(results_list, marks_list)

        # 4. Generate Personalized Recommendations
        recommendations = cls._generate_recommendations(shortage_risk, weak_subjects, predicted_cgpa, attendance_list)

        report = AnalyticsReport(
            analytics_id=None,
            student_id=student_id,
            generated_at=None,
            predicted_cgpa=predicted_cgpa,
            weak_subjects=weak_subjects,
            shortage_risk_subjects=shortage_risk,
            attendance_safe_skips=safe_skips_map,
            recommendations=recommendations
        )
        report.save()
        return report

    @classmethod
    def _predict_attendance_risks(cls, attendance_list: List[SubjectAttendance]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Computes shortage risks and safe skips based on current and projected lectures.
        Standard semester lecture quota assumed as 60 lectures per theory course.
        """
        shortage_risk = []
        safe_skips_map = {}
        min_threshold = ACADEMIC_RULES["min_attendance_pct"]  # 75.0%

        for att in attendance_list:
            pct = att.calculated_percentage
            safe_skips = att.safe_skips(min_threshold)
            needed_classes = att.lectures_needed(min_threshold)
            safe_skips_map[att.subject_code] = safe_skips

            # Projection assuming 60 total semester lectures
            est_total_delivered = max(att.total_delivered, 60)
            remaining_lectures = max(0, est_total_delivered - att.total_delivered)
            
            # Best case: attends all remaining
            best_case_pct = round(((att.effective_attended + remaining_lectures) * 100.0) / est_total_delivered, 2)
            # Worst case: attends none
            worst_case_pct = round((att.effective_attended * 100.0) / est_total_delivered, 2)

            is_critical = pct < min_threshold
            is_warning = min_threshold <= pct < ACADEMIC_RULES["warning_attendance_pct"]

            if is_critical or is_warning:
                shortage_risk.append({
                    "subject_code": att.subject_code,
                    "subject_name": att.subject_name,
                    "current_pct": pct,
                    "status": "CRITICAL" if is_critical else "WARNING",
                    "lectures_needed": needed_classes,
                    "safe_skips": safe_skips,
                    "projected_best": best_case_pct,
                    "projected_worst": worst_case_pct,
                    "delivered": att.total_delivered,
                    "attended": att.effective_attended
                })

        # Sort shortage risks by severity: CRITICAL first, then lowest percentage
        shortage_risk.sort(key=lambda x: (0 if x["status"] == "CRITICAL" else 1, x["current_pct"]))
        return shortage_risk, safe_skips_map

    @classmethod
    def _detect_weak_subjects(cls, attendance_list: List[SubjectAttendance], marks_list: List[MarkItem]) -> List[Dict[str, Any]]:
        """
        Analyzes performance across internal assessments and attendance to detect weak subjects.
        """
        # Group marks by subject
        subject_marks: Dict[str, List[MarkItem]] = {}
        for m in marks_list:
            subject_marks.setdefault(m.subject_code, []).append(m)

        weak_list = []
        for att in attendance_list:
            code = att.subject_code
            items = subject_marks.get(code, [])
            
            # Calculate average percentage in assessments
            if items:
                percentages = [m.percentage for m in items]
                avg_marks_pct = round(sum(percentages) / len(percentages), 2)
            else:
                avg_marks_pct = 70.0  # default baseline if marks not yet posted

            # Compute Composite Risk Index (0 - 100, higher is riskier)
            # 60% weight on marks deficit, 40% weight on attendance deficit
            marks_deficit = max(0.0, 75.0 - avg_marks_pct)  # Target 75% marks
            att_deficit = max(0.0, 80.0 - att.calculated_percentage)
            
            risk_score = round((marks_deficit * 0.6) + (att_deficit * 0.4) * 2.0, 1)
            risk_score = min(100.0, max(0.0, risk_score))

            if risk_score > 15.0 or avg_marks_pct < 65.0 or att.calculated_percentage < 75.0:
                reasons = []
                if avg_marks_pct < 65.0:
                    reasons.append(f"Low assessment score avg ({avg_marks_pct}%)")
                if att.calculated_percentage < 75.0:
                    reasons.append(f"Attendance below threshold ({att.calculated_percentage}%)")
                elif att.calculated_percentage < 80.0:
                    reasons.append(f"Borderline attendance ({att.calculated_percentage}%)")

                weak_list.append({
                    "subject_code": code,
                    "subject_name": att.subject_name,
                    "avg_marks_pct": avg_marks_pct,
                    "attendance_pct": att.calculated_percentage,
                    "risk_score": risk_score,
                    "reasons": reasons
                })

        # Sort weak subjects by risk score descending
        weak_list.sort(key=lambda x: x["risk_score"], reverse=True)
        return weak_list

    @classmethod
    def _predict_cgpa(cls, results_list: List[SemesterResult], current_marks: List[MarkItem]) -> float:
        """
        Calculates predicted CGPA based on previous semester SGPA regression and current internal performance.
        """
        if not results_list:
            return 8.00

        # Historical SGPAs
        sgpas = [r.sgpa for r in results_list]
        credits_list = [r.earned_credits for r in results_list]
        total_prev_credits = sum(credits_list)
        total_prev_weighted = sum(sg * cr for sg, cr in zip(sgpas, credits_list))

        # Estimate current semester SGPA from internals
        if current_marks:
            curr_pcts = [m.percentage for m in current_marks]
            curr_avg_pct = sum(curr_pcts) / len(curr_pcts)
            # Estimate SGPA on 10.0 scale: rough mapping (pct / 10) + small curve
            curr_est_sgpa = min(10.0, max(4.0, (curr_avg_pct / 10.0) + 0.3))
        else:
            # Fallback to exponential moving average of past SGPAs
            curr_est_sgpa = np.average(sgpas, weights=np.linspace(1, 2, len(sgpas)))

        # Weighted cumulative combination
        current_sem_credits = 21.0
        predicted_cgpa = (total_prev_weighted + (curr_est_sgpa * current_sem_credits)) / (total_prev_credits + current_sem_credits)
        return round(float(predicted_cgpa), 2)

    @classmethod
    def _generate_recommendations(
        cls,
        shortage_risk: List[Dict[str, Any]],
        weak_subjects: List[Dict[str, Any]],
        predicted_cgpa: float,
        attendance_list: List[SubjectAttendance]
    ) -> List[str]:
        """Generates targeted, actionable advice for the student."""
        recommendations = []

        # Attendance recommendations
        critical_subjects = [s for s in shortage_risk if s["status"] == "CRITICAL"]
        if critical_subjects:
            for s in critical_subjects:
                recommendations.append(
                    f"🚨 Mandatory Action: Attend the next {s['lectures_needed']} consecutive lectures of "
                    f"'{s['subject_name']}' to restore attendance above 75% (currently {s['current_pct']}%)."
                )
        else:
            recommendations.append("✅ Great job! All subjects currently meet the minimum 75% attendance criterion.")

        # Academic recommendations for weakest subject
        if weak_subjects:
            top_weak = weak_subjects[0]
            recommendations.append(
                f"🎯 Focus Subject: '{top_weak['subject_name']}' has a composite risk score of {top_weak['risk_score']}/100. "
                f"Schedule 3 dedicated review sessions per week and practice past exam problems."
            )

        # CGPA guidance
        if predicted_cgpa >= ACADEMIC_RULES["target_cgpa"]:
            recommendations.append(
                f"⭐ On Track: Your expected CGPA is {predicted_cgpa}, exceeding the target of {ACADEMIC_RULES['target_cgpa']}. "
                f"Maintain your current internal momentum in final exams."
            )
        else:
            gap = round(ACADEMIC_RULES["target_cgpa"] - predicted_cgpa, 2)
            recommendations.append(
                f"📈 CGPA Optimization: Predicted CGPA is {predicted_cgpa} (gap of {gap} from target 8.50). "
                f"Securing 85%+ in end-semester exams will boost your cumulative score above 8.5."
            )

        # Buffer utilization advice
        safe_courses = [a for a in attendance_list if a.safe_skips(80.0) >= 3]
        if safe_courses:
            top_buffer = safe_courses[0]
            recommendations.append(
                f"💡 Safe Buffer: You have {top_buffer.safe_skips(75.0)} safe skips in '{top_buffer.subject_name}' "
                f"({top_buffer.calculated_percentage}%). You can safely use duty leaves or study leaves if necessary."
            )

        return recommendations
