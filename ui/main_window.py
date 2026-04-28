from PySide6.QtWidgets import (
    QHBoxLayout, QWidget, QPushButton,
    QVBoxLayout, QStackedWidget, QMenu
)
from PySide6.QtCore import Qt

from ui.collection_page import CollectionPage
from ui.menu_page import MenuPage
from ui.navigation_pages import NavigationPages
from ui.scan_page import ScanPage

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Hamburger menu
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setFixedSize(40, 40)

        self.menu = QMenu(self)

        action_menu = self.menu.addAction("Menu")
        action_scan = self.menu.addAction("Scan")
        action_collection = self.menu.addAction("Collection")

        action_menu.triggered.connect(
            lambda: self.navigate_to(NavigationPages.Menu)
        )
        action_scan.triggered.connect(
            lambda: self.navigate_to(NavigationPages.Scanner)
        )
        action_collection.triggered.connect(
            lambda: self.navigate_to(NavigationPages.Collection)
        )
        self.btn_menu.clicked.connect(self.show_menu)
        self.btn_menu.hide()

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.btn_menu, alignment=Qt.AlignLeft)
        top_bar.addStretch()

        # Pages
        self.stack = QStackedWidget()
        self.page_menu = MenuPage()
        self.page_scan = ScanPage()
        self.page_collection = CollectionPage()

        self.stack.addWidget(self.page_menu)
        self.stack.addWidget(self.page_scan)
        self.stack.addWidget(self.page_collection)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.page_menu.navigation_requested.connect(self.navigate_to)

    def show_menu(self):
        self.menu.exec(self.btn_menu.mapToGlobal(
            self.btn_menu.rect().bottomLeft()
        ))
        
    def navigate_to(self, page: NavigationPages):
        if page == NavigationPages.Menu:
            self.btn_menu.hide()
        else:
            self.btn_menu.show()

        match page:
            case NavigationPages.Menu:
                self.stack.setCurrentIndex(0)
            case NavigationPages.Scanner:
                self.stack.setCurrentIndex(1)
            case NavigationPages.Collection:
                self.page_collection.set_cards([
                    {"name": "Sol Ring", "set": "Commander Masters"},
                    {"name": "Fabled Passage", "set": "Zendikar Rising"},
                    {"name": "Solemn Simulacrum", "set": "Commander 2019"},
                ])
                self.stack.setCurrentIndex(2)
    
