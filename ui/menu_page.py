from PySide6.QtWidgets import (
    QLabel, QWidget, QPushButton,
    QVBoxLayout,
)
from PySide6.QtGui import Qt
from blinker import Signal

from ui.navigation_pages import NavigationPages

class MenuPage(QWidget):
    navigation_requested = Signal(NavigationPages)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTG Manager")

        title = QLabel("MTG Manager")
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #ca52fa;")
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.setAlignment(Qt.AlignCenter)
        title_layout.setContentsMargins(0, 0, 0, 40)

        btn_scan = QPushButton("Scan")
        btn_scan.setStyleSheet("font-size: 24px; font-weight: bold;")
        btn_scan.setFixedHeight(70)
        btn_scan.setFixedWidth(200)
        
        btn_collection = QPushButton("Collection")
        btn_collection.setStyleSheet("font-size: 24px; font-weight: bold;")
        btn_collection.setFixedHeight(70)
        btn_collection.setFixedWidth(200)
        
        btn_scan.clicked.connect(
            lambda: self.navigation_requested.send(NavigationPages.Scanner)
        )
        btn_collection.clicked.connect(
            lambda: self.navigation_requested.send(NavigationPages.Collection)
        )

        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addWidget(btn_scan, alignment=Qt.AlignCenter)
        main_layout.addWidget(btn_collection, alignment=Qt.AlignCenter)
        main_layout.setAlignment(Qt.AlignCenter)

        self.setLayout(main_layout)