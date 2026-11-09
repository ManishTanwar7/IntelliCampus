"""
IntelliCampus: Analytics Controller
Coordinates AI predictive insights and recommendations.
"""
from typing import Dict, Any, Optional
from models.analytics import AnalyticsReport
from services.ai_analytics_service import AIAnalyticsEngine

class AnalyticsController:

    @classmethod
    def get_or_generate_report(cls, student_id: str, force_refresh: bool = False) -> AnalyticsReport:
        if not force_refresh:
            existing = AnalyticsReport.get_latest(student_id)
            if existing:
                return existing
        return AIAnalyticsEngine.analyze_student(student_id)
