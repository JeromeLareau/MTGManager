import sys
import cv2

from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtCore import QThread
from camera_worker import CameraWorker
from processing_worker import ProcessingWorker
from scanner_controller import ScanController

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTG Manager")
        self.resize(1000, 700)

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
        self.card_type = QLabel("")
        self.card_set = QLabel("")
        self.add_button = QPushButton("Add to collection")

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.card_image)
        right_layout.addWidget(self.card_name)
        right_layout.addWidget(self.card_type)
        right_layout.addWidget(self.card_set)
        right_layout.addStretch()
        right_layout.addWidget(self.add_button)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)
        
        # Connect signals and start workers
        self.scan_controller = ScanController()
        self.camera = CameraWorker(self.scan_controller)
        self.processing_thread = QThread()
        self.processor = ProcessingWorker(self.scan_controller)
        
        self.camera.frame_ready.connect(self.update_image)
        self.camera.card_detected.connect(self.processor.process_card, Qt.QueuedConnection)
        self.processor.card_ready.connect(self.display_card)
        
        self.processor.moveToThread(self.processing_thread)
        self.processing_thread.start()

        # self.processor.start()
        self.camera.start()

    def update_image(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        qt_image = QImage(
            rgb.data, w, h, bytes_per_line, QImage.Format_RGB888
        )

        self.camera_preview.setPixmap(QPixmap.fromImage(qt_image))
        
    def display_card(self, card, image_data):
        self.card_name.setText(card['name'])
        self.card_type.setText(card['type_line'])
        self.card_set.setText(card['set_name'])
        
        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.card_image.setPixmap(pixmap)


    def closeEvent(self, event):
        self.camera.stop()
        self.camera.wait()
        self.processor.stop()
        self.processor.wait()
        event.accept()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())