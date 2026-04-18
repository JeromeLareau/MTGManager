from scanner.ocr import retry_with_adaptive_threshold, retry_with_gray_filter, scan_card_name
from scanner.scryfall import get_card_by_fuzzy_name

if __name__ == "__main__":
    image_path = "card.jpg"  # <-- put an MTG card image here

    ocr_name = scan_card_name(image_path)
    print("OCR RESULT:", ocr_name)

    card = get_card_by_fuzzy_name(ocr_name)
    if card is None:
        print("Retrying with grayscale filter...")
        ocr_name = retry_with_gray_filter()
        card = get_card_by_fuzzy_name(ocr_name)
        
    if card is None:
        print("Retrying with adaptive threshold...")
        ocr_name = retry_with_adaptive_threshold()
        card = get_card_by_fuzzy_name(ocr_name)

    if card is None:
        print("No card found on Scryfall")
    else:
        print("✅ MATCH FOUND")
        print("Name:", card["name"])
        print("Mana cost:", card.get("mana_cost"))
        print("Type:", card.get("type_line"))
        print("Set:", card["set_name"])
        print("Rarity:", card["rarity"])