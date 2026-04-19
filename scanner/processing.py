from scanner.ocr import retry_with_adaptive_threshold, retry_with_gray_filter, scan_card_name
from scanner.scryfall import get_card_by_fuzzy_name

def process_cards(card_queue, stop_event):
    while not stop_event.is_set():
        card_image = card_queue.get()
        if card_image is None:
            continue

        name = scan_card_name(card_image)
        print("OCR:", name)

        card = get_card_by_fuzzy_name(name)
        if card is None:
            print("Retrying with grayscale filter...")
            ocr_name = retry_with_gray_filter()
            card = get_card_by_fuzzy_name(ocr_name)
            
        if card is None:
            print("Retrying with adaptive threshold...")
            ocr_name = retry_with_adaptive_threshold()
            card = get_card_by_fuzzy_name(ocr_name)
        if card is None:
            print("❌ No card found on Scryfall")
        else:
            print("✅ FOUND:", card["name"])

        card_queue.task_done()