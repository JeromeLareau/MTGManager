from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt

from db.database import load_collection


class CollectionPage(QWidget):
    def __init__(self):
        super().__init__()

        # --- Search bar ---
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search collection…")

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "Set",
            "Normal",
            "Foil",
            "Price"
        ])

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.table)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Signals
        self.search_bar.textChanged.connect(self.filter_rows)

        # Load initial data
        self.reload()

    # ✅ Public API
    def reload(self):
        rows = load_collection()
        self.populate(rows)

    # --- Internal helpers ---

    def populate(self, rows):
        self.table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row["name"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row["set_name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row["qty_normal"])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(row["qty_foil"])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row["price_normal"])))

            # Align quantities
            self.table.item(row_idx, 2).setTextAlignment(Qt.AlignCenter)
            self.table.item(row_idx, 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(row_idx, 4).setTextAlignment(Qt.AlignCenter)

    def filter_rows(self, text):
        text = text.lower()

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().lower()
            set_name = self.table.item(row, 1).text().lower()

            visible = text in name or text in set_name
            self.table.setRowHidden(row, not visible)
            
    def showEvent(self, event):
        super().showEvent(event)
        self.reload()