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

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera")

        while self.running:
            ret, frame = cap.read()
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

        cap.release()

    def stop(self):
        self.running = False