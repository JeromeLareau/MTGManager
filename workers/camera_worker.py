import cv2
from PySide6.QtCore import QThread, Signal
from scanner.card_detect import detect_card, warp_card

class CameraWorker(QThread):
    frame_ready = Signal(object)     # full frame for preview
    card_detected = Signal(object)   # warped card image

    def __init__(self, scan_controller):
        super().__init__()
        self.scan_controller = scan_controller
        self.running = True
        self.active = False
        self.cap = None

    def run(self):
        while self.running:
            if not self.active:
                self.msleep(50)
                continue
            
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    print("Could not open camera")
                    self.cap = None
                    self.msleep(500)
                    continue

            ret, frame = self.cap.read()
            if not ret:
                continue

            display = frame.copy()
            contour = detect_card(frame)

            if contour is not None:
                cv2.drawContours(display, [contour], -1, (0, 255, 0), 3)
                
                if self.scan_controller.can_submit():
                    card = warp_card(frame, contour)
                    self.scan_controller.mark_submitted()
                    self.card_detected.emit(card)

            # always emit the preview frame
            self.frame_ready.emit(display)

        if self.cap is not None:
            self.cap.release()

    def stop(self):
        self.running = False
        
    def start_camera(self):
        self.active = True

    def stop_camera(self):
        self.active = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
