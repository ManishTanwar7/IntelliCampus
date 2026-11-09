"""
Analytics Model
"""
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from services.database import DatabaseManager

@dataclass
class AnalyticsReport:
    analytics_id: Optional[int]
    student_id: str
    generated_at: Optional[str]
    predicted_cgpa: float
    weak_subjects: List[Dict[str, Any]]
    shortage_risk_subjects: List[Dict[str, Any]]
    attendance_safe_skips: Dict[str, int]
    recommendations: List[str]

    @classmethod
    def get_latest(cls, student_id: str) -> Optional['AnalyticsReport']:
        db = DatabaseManager()
        query = "SELECT * FROM ai_analytics WHERE student_id = %s ORDER BY generated_at DESC LIMIT 1;"
        row = db.fetch_one(query, (student_id,))
        if row:
            return cls(
                analytics_id=row.get("analytics_id"),
                student_id=row["student_id"],
                generated_at=str(row.get("generated_at")),
                predicted_cgpa=float(row.get("predicted_cgpa", 0.0)),
                weak_subjects=json.loads(row.get("weak_subjects_json") or "[]"),
                shortage_risk_subjects=json.loads(row.get("shortage_risk_subjects_json") or "[]"),
                attendance_safe_skips=json.loads(row.get("attendance_safe_skips_json") or "{}"),
                recommendations=json.loads(row.get("recommendations_json") or "[]")
            )
        return None

    def save(self) -> bool:
        db = DatabaseManager()
        query = """
            INSERT INTO ai_analytics (
                student_id, predicted_cgpa, weak_subjects_json,
                shortage_risk_subjects_json, attendance_safe_skips_json, recommendations_json
            ) VALUES (%s, %s, %s, %s, %s, %s);
        """
        self.analytics_id = db.execute_update(query, (
            self.student_id,
            self.predicted_cgpa,
            json.dumps(self.weak_subjects),
            json.dumps(self.shortage_risk_subjects),
            json.dumps(self.attendance_safe_skips),
            json.dumps(self.recommendations)
        ))
        return True
