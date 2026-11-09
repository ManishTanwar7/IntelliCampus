"""
IntelliCampus: Theme Manager & QSS Stylesheets
Provides modern Collegia-inspired dark and light stylesheets.
"""

DARK_THEME_QSS = """
/* Global Styling */
QWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
    selection-background-color: #6366F1;
    selection-color: #FFFFFF;
}

/* Sidebar */
#SidebarWidget {
    background-color: #0B1120;
    border-right: 1px solid #1E293B;
}

#SidebarTitle {
    font-size: 18px;
    font-weight: 700;
    color: #818CF8;
    padding: 12px 10px;
}

#SidebarSubtitle {
    font-size: 11px;
    color: #64748B;
    font-weight: 500;
    margin-top: -6px;
    margin-bottom: 12px;
}

/* Sidebar Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}

QPushButton.NavButton:checked, QPushButton.NavButton[active="true"] {
    background-color: #4F46E5;
    color: #FFFFFF;
}

/* Top Header Bar */
#TopHeaderWidget {
    background-color: #1E293B;
    border-bottom: 1px solid #334155;
    padding: 8px 16px;
}

#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #F8FAFC;
}

/* Cards & Containers */
QFrame.CardFrame {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
}

QFrame.MetricCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 14px;
}

QLabel.CardTitle {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel.MetricValue {
    font-size: 26px;
    font-weight: 800;
    color: #F8FAFC;
    margin-top: 4px;
}

QLabel.MetricSubtitle {
    font-size: 11px;
    color: #64748B;
}

/* Standard Buttons */
QPushButton.PrimaryButton {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.PrimaryButton:hover {
    background-color: #4338CA;
}

QPushButton.PrimaryButton:pressed {
    background-color: #3730A3;
}

QPushButton.SecondaryButton {
    background-color: #334155;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.SecondaryButton:hover {
    background-color: #475569;
}

QPushButton.DangerButton {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: #DC2626;
}

QPushButton.SuccessButton {
    background-color: #10B981;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.SuccessButton:hover {
    background-color: #059669;
}

/* Inputs & Form Controls */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateEdit {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #6366F1;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #6366F1;
    background-color: #131E35;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    color: #F8FAFC;
    selection-background-color: #312E81;
    selection-color: #FFFFFF;
}

QHeaderView::section {
    background-color: #0F172A;
    color: #94A3B8;
    font-weight: 700;
    border: none;
    border-bottom: 2px solid #334155;
    padding: 8px 10px;
    text-transform: uppercase;
    font-size: 11px;
}

/* Progress Bars */
QProgressBar {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    color: #F8FAFC;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #6366F1;
    border-radius: 5px;
}

/* Tab Widgets */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #1E293B;
    top: -1px;
}

QTabBar::tab {
    background-color: #0F172A;
    color: #94A3B8;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1E293B;
    color: #818CF8;
    border-bottom: 2px solid #6366F1;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #0F172A;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

LIGHT_THEME_QSS = """
/* Global Styling */
QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
}

/* Sidebar */
#SidebarWidget {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

#SidebarTitle {
    font-size: 18px;
    font-weight: 700;
    color: #4F46E5;
    padding: 12px 10px;
}

#SidebarSubtitle {
    font-size: 11px;
    color: #64748B;
    font-weight: 500;
    margin-top: -6px;
    margin-bottom: 12px;
}

/* Sidebar Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #64748B;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton.NavButton:checked, QPushButton.NavButton[active="true"] {
    background-color: #EEF2FF;
    color: #4F46E5;
}

/* Top Header Bar */
#TopHeaderWidget {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 8px 16px;
}

#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
}

/* Cards & Containers */
QFrame.CardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
}

QFrame.MetricCard {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px;
}

QLabel.CardTitle {
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel.MetricValue {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
    margin-top: 4px;
}

QLabel.MetricSubtitle {
    font-size: 11px;
    color: #94A3B8;
}

/* Standard Buttons */
QPushButton.PrimaryButton {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.PrimaryButton:hover {
    background-color: #4338CA;
}

QPushButton.SecondaryButton {
    background-color: #F1F5F9;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.SecondaryButton:hover {
    background-color: #E2E8F0;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    color: #0F172A;
    selection-background-color: #EEF2FF;
    selection-color: #4F46E5;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    font-weight: 700;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    padding: 8px 10px;
    text-transform: uppercase;
    font-size: 11px;
}

/* Progress Bars */
QProgressBar {
    background-color: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    text-align: center;
    color: #0F172A;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #4F46E5;
    border-radius: 5px;
}
"""

class ThemeManager:
    _current_theme = "dark"

    @classmethod
    def get_current_theme(cls) -> str:
        return cls._current_theme

    @classmethod
    def apply_theme(cls, app, theme_name: str = "dark"):
        cls._current_theme = theme_name
        if theme_name == "dark":
            app.setStyleSheet(DARK_THEME_QSS)
        else:
            app.setStyleSheet(LIGHT_THEME_QSS)
