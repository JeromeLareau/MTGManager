import sys
import cv2
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
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

        self.preview = QLabel("Starting camera...")
        self.preview.setScaledContents(True)
        
        self.card_label = QLabel("No card detected")

        layout = QVBoxLayout()
        layout.addWidget(self.preview)
        layout.addWidget(self.card_label)
        self.setLayout(layout)
        
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

        self.preview.setPixmap(QPixmap.fromImage(qt_image))
        
    
    def display_card(self, card):
        self.card_label.setText(
            f"{card['name']} — {card['set_name']}"
        )

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