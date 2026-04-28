from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt

class CollectionPage(QWidget):
    def __init__(self):
        super().__init__()

        # --- Search bar ---
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search collection…")

        # --- Card list ---
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        # Internal data (V1: simple list)
        self.cards = []  # list of dicts or strings

        # Signals
        self.search_bar.textChanged.connect(self.filter_list)

    # --- Public API ---

    def set_cards(self, cards):
        """
        cards: list of dicts, e.g.
        { "name": "Sol Ring", "set": "Commander Masters" }
        """
        self.cards = cards
        self.refresh_list()

    def add_card(self, card):
        self.cards.append(card)
        self.refresh_list()

    # --- UI logic ---

    def refresh_list(self):
        self.list_widget.clear()

        for card in self.cards:
            item = QListWidgetItem(card["name"])
            self.list_widget.addItem(item)

    def filter_list(self, text):
        text = text.lower()

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            visible = text in item.text().lower()
            item.setHidden(not visible)