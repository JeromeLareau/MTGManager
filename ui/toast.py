from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class Toast(QWidget):
    def __init__(self, parent, message: str, duration=2000):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        label = QLabel(message)
        label.setStyleSheet("""
            QLabel {
                background-color: #2e7d32;
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
            }
        """)
        label.setFont(QFont("Segoe UI", 10))
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.adjustSize()
        self.move_to_top_right()

        QTimer.singleShot(duration, self.close)

    def move_to_top_right(self):
        parent_rect = self.parent().geometry()
        toast_rect = self.geometry()

        x = parent_rect.right() - toast_rect.width() - 20
        y = parent_rect.top() + 20

        self.move(x, y)