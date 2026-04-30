import cv2

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtCore import QThread
from db.database import add_card_to_collection
from scanner.scryfall import ScryfallEndpoint, safe_scryfall_lookup
from ui.quantity_widget import QuantityWidget
from ui.toast import Toast
from workers.camera_worker import CameraWorker
from workers.processing_worker import ProcessingWorker
from workers.scanner_controller import ScanController

class ScanPage(QWidget):
    def __init__(self, download_manager):
        super().__init__()
        self.download_manager = download_manager
        self.download_manager.image_downloaded.connect(self.on_image_downloaded)
        
        self.setWindowTitle("MTG Manager")
        self.resize(1000, 700)
        self.current_card = None
        self.qty = 1
        self.prints = {}

        # Left side: camera preview
        self.camera_preview = QLabel("Camera")
        self.camera_preview.setMinimumSize(640, 480)
        self.camera_preview.setScaledContents(False)
        self.camera_preview.setAlignment(Qt.AlignCenter)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.camera_preview)

        # Right side: card info
        self.card_image = QLabel()
        self.card_image.setFixedSize(250, 350)
        self.card_image.setScaledContents(True)

        self.card_name = QLabel("No card")
        self.card_name.setAlignment(Qt.AlignCenter)
        self.card_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.card_type = QLabel("")
        self.card_type.setAlignment(Qt.AlignCenter)
        self.card_type.setStyleSheet("font-size: 14px;")
        self.card_set = QComboBox()
        self.card_set.currentIndexChanged.connect(self.set_current_print)
        self.foil_checkbox = QCheckBox("Foil")
        self.quantity_widget = QuantityWidget(self.qty)
        self.quantity_widget.changed.connect(self.update_quantity)
        
        self.add_button = QPushButton("Add to collection")
        self.add_button.clicked.connect(
            lambda: self.add_card()
        )

        self.add_button.setEnabled(False)
        
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(self.quantity_widget)
        quantity_layout.addWidget(self.foil_checkbox)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.card_image)
        right_layout.addWidget(self.card_name)
        right_layout.addWidget(self.card_type)
        right_layout.addWidget(self.card_set)
        right_layout.addStretch()
        right_layout.addLayout(quantity_layout)
        right_layout.addWidget(self.add_button)
        right_layout.setAlignment(Qt.AlignCenter)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)
        
        # Connect signals and start workers
        self.scan_controller = ScanController()
        self.camera = CameraWorker(self.scan_controller)
        self.processor = ProcessingWorker(self.scan_controller)
        self.processing_thread = QThread()
        
        self.camera.frame_ready.connect(self.update_image)
        self.camera.card_detected.connect(self.processor.process_card, Qt.QueuedConnection)
        self.processor.card_ready.connect(self.display_card)
        
        self.processor.moveToThread(self.processing_thread)
        self.processing_thread.start()
        self.camera.start()

    def update_image(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        qt_image = QImage(
            rgb.data, w, h, bytes_per_line, QImage.Format_RGB888
        )

        self.camera_preview.setPixmap(QPixmap.fromImage(qt_image))
        
    def display_card(self, card):
        self.card_name.setText(card['name'])
        self.card_type.setText(card['type_line'])
        self.current_card = card
        self.qty = 1
        self.quantity_widget.set_value(self.qty)
        self.foil_checkbox.setChecked(False)
        self.add_button.setEnabled(True)
        
        self.prints.clear()
        prints_uri = card.get("prints_search_uri")
        prints = safe_scryfall_lookup(ScryfallEndpoint.URI, prints_uri)
        for p in prints["data"]:
            if p["object"] != "card":
                continue
            self.prints[f"{p['set_name']} - {p['set']}"] = p
        self.card_set.clear()
        self.card_set.addItems(self.prints.keys())
        self.card_set.setCurrentText(f"{card['set_name']} - {card['set']}")
        
        self.download_manager.download(self.current_card['image_uris']['normal'])
            
    def update_quantity(self, delta):
        new_value = max(1, self.qty + delta)
        self.qty = new_value
        self.quantity_widget.set_value(new_value)
        
    def set_current_print(self, index):
        key = self.card_set.currentText()
        if key in self.prints:
            self.current_card = self.prints[key]
            self.download_manager.download(self.current_card['image_uris']['normal'])
    
    def on_image_downloaded(self, url, data):
        if data:
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.card_image.setPixmap(pixmap)
        
    def add_card(self):
        if not self.current_card:
            return
        
        card_id = self.current_card['id']
        foil = self.foil_checkbox.isChecked()
        add_card_to_collection(card_id, qty=self.qty, foil=foil)
        foil_text = "foil " if foil else ""
        Toast(self.window(), f"Added {self.qty}x {foil_text}{self.current_card['name']} to collection").show()

    def closeEvent(self, event):
        self.camera.stop()
        self.camera.wait()
        self.processor.stop()
        self.processor.wait()
        event.accept()
        
    def showEvent(self, event):
        super().showEvent(event)
        self.camera.start_camera()
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.camera.stop_camera()

