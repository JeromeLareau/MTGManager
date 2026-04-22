from scanner.ocr import retry_with_adaptive_threshold, retry_with_gray_filter, scan_card_name
from scanner.scryfall import ScryfallEndpoint, safe_scryfall_lookup

last_card_id = None

def process_cards(card_queue, stop_event):
    global last_card_id
    
    while not stop_event.is_set():
        card_image = card_queue.get()
        if card_image is None:
            continue

        name = scan_card_name(card_image)
        print("OCR:", name)

        card = safe_scryfall_lookup(endpoint=ScryfallEndpoint.FUZZY, name=name)
        if card is None:
            print("Retrying with grayscale filter...")
            ocr_name = retry_with_gray_filter()
            card = safe_scryfall_lookup(endpoint=ScryfallEndpoint.FUZZY, name=ocr_name)
            
        if card is None:
            print("Retrying with adaptive threshold...")
            ocr_name = retry_with_adaptive_threshold()
            card = safe_scryfall_lookup(endpoint=ScryfallEndpoint.FUZZY, name=ocr_name)
            
        if card is None:
            print("❌ No card found on Scryfall")
            
        else:            
            if card["id"] == last_card_id:
                print("⚠️ Duplicate card detected, skipping")
                card_queue.task_done()
                continue
            print("✅ Card added to collection:", card["name"])
            last_card_id = card["id"]

        card_queue.task_done()