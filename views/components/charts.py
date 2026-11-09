"""
IntelliCampus: Plotly Interactive Chart Components
Embeds interactive Plotly visualizations in PyQt6 using QWebEngineView.
"""
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QUrl

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except Exception:
    WEBENGINE_AVAILABLE = False

import plotly.graph_objects as go
import plotly.express as px

class PlotlyChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.layout.addWidget(self.web_view)
        else:
            self.web_view = None
            self.fallback_label = QLabel("Interactive Chart (WebEngine initializing...)")
            self.fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.fallback_label)

    def load_figure(self, fig: go.Figure, is_dark: bool = True):
        """Renders Plotly figure with dark or light theme."""
        bg_color = "#1E293B" if is_dark else "#FFFFFF"
        text_color = "#F8FAFC" if is_dark else "#0F172A"
        grid_color = "#334155" if is_dark else "#E2E8F0"

        fig.update_layout(
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color, family="Segoe UI, sans-serif"),
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis=dict(gridcolor=grid_color),
            yaxis=dict(gridcolor=grid_color)
        )

        html_content = fig.to_html(include_plotlyjs="cdn", full_html=True)
        # Add basic responsive style
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background-color: {bg_color}; overflow: hidden; }}
                .js-plotly-plot {{ height: 100vh !important; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        if self.web_view:
            self.web_view.setHtml(styled_html)
        elif hasattr(self, 'fallback_label'):
            self.fallback_label.setText("Chart loaded successfully")

    # --- Chart Builders ---
    @staticmethod
    def create_attendance_bar_chart(attendance_list: list, is_dark: bool = True) -> go.Figure:
        codes = [a.subject_code for a in attendance_list]
        names = [a.subject_name for a in attendance_list]
        percentages = [a.calculated_percentage for a in attendance_list]
        
        # Colors: Green for >=80, Yellow for 75-80, Red for <75
        bar_colors = []
        for p in percentages:
            if p >= 80.0:
                bar_colors.append("#10B981")  # Emerald
            elif p >= 75.0:
                bar_colors.append("#F59E0B")  # Amber
            else:
                bar_colors.append("#EF4444")  # Rose

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=codes,
            y=percentages,
            text=[f"{p:.1f}%" for p in percentages],
            textposition='auto',
            hovertext=[f"{n}<br>Delivered: {a.total_delivered}<br>Attended: {a.effective_attended}" for n, a in zip(names, attendance_list)],
            hoverinfo="text",
            marker=dict(color=bar_colors, cornerradius=6)
        ))

        # Add 75% threshold line
        fig.add_hline(
            y=75.0,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text="Mandatory 75% Limit",
            annotation_position="bottom right"
        )

        fig.update_layout(
            title="Subject-Wise Attendance Percentage",
            yaxis=dict(title="Attendance (%)", range=[0, 105]),
            xaxis=dict(title="Course Code")
        )
        return fig

    @staticmethod
    def create_cgpa_trend_chart(semester_results: list, predicted_cgpa: Optional[float] = None, is_dark: bool = True) -> go.Figure:
        semesters = [f"Sem {r.semester}" for r in semester_results]
        sgpas = [r.sgpa for r in semester_results]
        cgpas = [r.cgpa for r in semester_results]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=semesters,
            y=sgpas,
            mode='lines+markers',
            name='Semester SGPA',
            line=dict(color='#06B6D4', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=semesters,
            y=cgpas,
            mode='lines+markers',
            name='Cumulative CGPA',
            line=dict(color='#6366F1', width=3),
            marker=dict(size=9)
        ))

        # Add projected future point if provided
        if predicted_cgpa is not None and semester_results:
            next_sem = f"Sem {len(semester_results) + 1} (Forecast)"
            fig.add_trace(go.Scatter(
                x=[semesters[-1], next_sem],
                y=[cgpas[-1], predicted_cgpa],
                mode='lines+markers',
                name='AI Predicted CGPA',
                line=dict(color='#F59E0B', width=2, dash='dot'),
                marker=dict(size=9, symbol='star')
            ))

        fig.update_layout(
            title="Academic CGPA & SGPA Progression",
            yaxis=dict(title="Grade Point (Scale of 10.0)", range=[5.0, 10.0]),
            xaxis=dict(title="Semester"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    @staticmethod
    def create_marks_distribution_chart(marks_list: list, is_dark: bool = True) -> go.Figure:
        subjects = list(set(m.subject_code for m in marks_list))
        # Compute avg percentage per subject
        subj_data = {}
        for m in marks_list:
            subj_data.setdefault(m.subject_code, []).append(m.percentage)

        avg_scores = [round(sum(subj_data[c])/len(subj_data[c]), 1) for c in subjects]

        fig = go.Figure(data=[go.Bar(
            x=subjects,
            y=avg_scores,
            text=[f"{s}%" for s in avg_scores],
            textposition='auto',
            marker=dict(color='#8B5CF6')
        )])

        fig.update_layout(
            title="Internal Assessment Performance by Course",
            yaxis=dict(title="Score (%)", range=[0, 100]),
            xaxis=dict(title="Course")
        )
        return fig
