import requests

SCRYFALL_NAMED_URL = "https://api.scryfall.com/cards/named"

class ScryfallError(Exception):
    pass

def get_card_by_fuzzy_name(name: str) -> dict | None:
    if not name:
        return None

    response = requests.get(
        SCRYFALL_NAMED_URL,
        params={"fuzzy": name},
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        # No match found
        return None

    raise ScryfallError(
        f"Scryfall error {response.status_code}: {response.text}"
    )