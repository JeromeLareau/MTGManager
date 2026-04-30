from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal


class QuantityWidget(QWidget):
    changed = Signal(int)  # emits +1 or -1

    def __init__(self, value: int):
        super().__init__()

        self.label = QLabel(str(value))
        self.label.setAlignment(Qt.AlignCenter)

        btn_minus = QPushButton("−")
        btn_plus = QPushButton("+")

        btn_minus.setFixedWidth(24)
        btn_plus.setFixedWidth(24)
        self.label.setFixedWidth(24)

        layout = QHBoxLayout()
        layout.addWidget(btn_minus)
        layout.addWidget(self.label)
        layout.addWidget(btn_plus)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        self.setLayout(layout)

        btn_minus.clicked.connect(lambda: self.emit(-1))
        btn_plus.clicked.connect(lambda: self.emit(+1))

    def emit(self, delta: int):
        self.changed.emit(delta)

    def set_value(self, value: int):
        self.label.setText(str(value))