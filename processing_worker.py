from PySide6.QtCore import QObject, QThread, Signal, Slot
from scanner.ocr import (
    scan_card_name,
    retry_with_gray_filter,
    retry_with_adaptive_threshold,
)
from scanner.scryfall import ScryfallEndpoint, safe_scryfall_lookup

class ProcessingWorker(QObject):
    card_ready = Signal(dict)
    scan_failed = Signal()

    def __init__(self, scan_controller):
        super().__init__()
        self.scan_controller = scan_controller
        self.last_card_id = None

    @Slot(object)
    def process_card(self, card_image):
        try:
            name = scan_card_name(card_image)
            print("OCR:", name)

            card = safe_scryfall_lookup(
                endpoint=ScryfallEndpoint.FUZZY,
                name=name
            )

            if card is None:
                print("Retrying with grayscale filter...")
                ocr_name = retry_with_gray_filter()
                card = safe_scryfall_lookup(
                    endpoint=ScryfallEndpoint.FUZZY,
                    name=ocr_name
                )

            if card is None:
                print("Retrying with adaptive threshold...")
                ocr_name = retry_with_adaptive_threshold()
                card = safe_scryfall_lookup(
                    endpoint=ScryfallEndpoint.FUZZY,
                    name=ocr_name
                )

            if card is None:
                print("❌ No card found on Scryfall")
                self.scan_failed.emit()
                return

            if card["id"] == self.last_card_id:
                print("⚠️ Duplicate card detected, skipping")
                self.scan_failed.emit()
                return

            self.last_card_id = card["id"]
            print("✅ Card added to collection:", card["name"])
            self.card_ready.emit(card)
        finally:
            self.scan_controller.mark_done()

    def run(self):
        self.exec()