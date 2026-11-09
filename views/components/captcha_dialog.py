"""
IntelliCampus: Manual CAPTCHA Entry Dialog
CRITICAL SAFETY COMPLIANCE:
The platform never bypasses CAPTCHA. This dialog presents the portal's
security verification image to the user and halts automation until
manual user input is provided.
"""
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtCore import Qt

class CaptchaDialog(QDialog):
    def __init__(self, captcha_image_bytes: bytes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("UIMS Security Verification - CAPTCHA Required")
        self.setFixedSize(440, 320)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self._user_input: Optional[str] = None
        self._init_ui(captcha_image_bytes)

    def _init_ui(self, image_bytes: bytes):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title
        title_label = QLabel("Portal Security Challenge")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Compliance Notice
        notice_label = QLabel(
            "UIMS portal requires verification. IntelliCampus strictly complies with "
            "security policies and never bypasses CAPTCHA. Please enter the characters shown below:"
        )
        notice_label.setWordWrap(True)
        notice_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(notice_label)

        # CAPTCHA Image Container Card
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #0B1120;
                border: 2px dashed #4F46E5;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        img_layout = QHBoxLayout(image_frame)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.captcha_label = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        # Scale to crisp view if needed
        self.captcha_label.setPixmap(pixmap.scaled(220, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        img_layout.addWidget(self.captcha_label)
        layout.addWidget(image_frame)

        # Input Field
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Type CAPTCHA characters exactly as seen...")
        self.input_edit.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 3px;
                padding: 8px 12px;
                text-align: center;
            }
        """)
        self.input_edit.returnPressed.connect(self._on_submit)
        layout.addWidget(self.input_edit)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.cancel_btn = QPushButton("Cancel Sync")
        self.cancel_btn.setProperty("class", "SecondaryButton")
        self.cancel_btn.clicked.connect(self._on_cancel)

        self.submit_btn = QPushButton("Submit & Verify")
        self.submit_btn.setProperty("class", "PrimaryButton")
        self.submit_btn.clicked.connect(self._on_submit)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.submit_btn)
        layout.addLayout(btn_layout)

        # Focus input immediately
        self.input_edit.setFocus()

    def _on_submit(self):
        text = self.input_edit.text().strip()
        if text:
            self._user_input = text
            self.accept()
        else:
            self.input_edit.setStyleSheet(self.input_edit.styleSheet() + "border: 1px solid #EF4444;")

    def _on_cancel(self):
        self._user_input = None
        self.reject()

    def get_input(self) -> Optional[str]:
        return self._user_input

    @classmethod
    def get_captcha_input(cls, image_bytes: bytes, parent=None) -> Optional[str]:
        """Convenience modal launcher that returns entered text or None."""
        dialog = cls(image_bytes, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_input()
        return None
