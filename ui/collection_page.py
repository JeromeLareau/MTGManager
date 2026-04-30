from PySide6.QtWidgets import (
    QHeaderView,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt

from db.database import get_connection, load_collection, update_quantity
from ui.quantity_widget import QuantityWidget


class CollectionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border-radius: 6px;
                background-color: #1e1e1e;
            }

            QTableWidget {
                background-color: #121212;
                gridline-color: #2a2a2a;
            }

            QHeaderView::section {
                background-color: #1e1e1e;
                padding: 6px;
                border: none;
            }
            """)

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
        
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Set
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Normal
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Foil
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Price


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
            card_id = row["id"]
            
            # Name and Set
            self.table.setItem(row_idx, 0, QTableWidgetItem(row["name"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row["set_name"]))
            
            # Normal quantity widget
            
            normal_item = QTableWidgetItem()
            normal_item.setData(Qt.DisplayRole, row["qty_normal"])
            normal_item.setData(Qt.UserRole, row["qty_normal"])
            normal_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, normal_item)

            normal_widget = QuantityWidget(row["qty_normal"])
            normal_widget.changed.connect(
                lambda delta, cid=card_id, w=normal_widget:
                    self.change_qty(cid, "qty_normal", delta, w)
            )
            self.table.setCellWidget(row_idx, 2, normal_widget)
            
            # Foil quantity widget
            foil_item = QTableWidgetItem()
            foil_item.setData(Qt.DisplayRole, row["qty_foil"])
            foil_item.setData(Qt.UserRole, row["qty_foil"])
            foil_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, foil_item)
            
            foil_widget = QuantityWidget(row["qty_foil"])
            foil_widget.changed.connect(
                lambda delta, cid=card_id, w=foil_widget:
                    self.change_qty(cid, "qty_foil", delta, w)
            )
            self.table.setCellWidget(row_idx, 3, foil_widget)

            # Price
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row["price_normal"])))
            self.table.item(row_idx, 4).setTextAlignment(Qt.AlignCenter)
            
    def change_qty(self, card_id, field, delta, widget):
        update_quantity(card_id, field, delta)

        # Update UI number instantly (no reload needed)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            f"SELECT {field} FROM collection WHERE card_id = ?",
            (card_id,)
        )
        new_value = cur.fetchone()[0]
        conn.close()

        widget.set_value(new_value)
        
        row = self.table.indexAt(widget.pos()).row()
        item = self.table.item(row, 2 if field == "qty_normal" else 3)
        if item is not None:
            item.setData(Qt.UserRole, new_value)
            item.setText(str(new_value))

        self.table.sortItems(
            self.table.horizontalHeader().sortIndicatorSection(),
            self.table.horizontalHeader().sortIndicatorOrder()
        )


    def filter_rows(self, text):
        text = text.lower()

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().lower()
            set_name = self.table.item(row, 1).text().lower()

            visible = text in name or text in set_name
            self.table.setRowHidden(row, not visible)