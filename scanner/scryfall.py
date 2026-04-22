import enum
from time import time

import requests

SCRYFALL_NAMED_URL = "https://api.scryfall.com/cards/named"

class ScryfallError(Exception):
    pass

SCRYFALL_MIN_INTERVAL = 0.6
last_scryfall_call = 0

class ScryfallEndpoint(enum.Enum):
    FUZZY = "fuzzy"

def safe_scryfall_lookup(endpoint: ScryfallEndpoint, name):
    global last_scryfall_call
    now = time.time()

    wait = SCRYFALL_MIN_INTERVAL - (now - last_scryfall_call)
    if wait > 0:
        time.sleep(wait)

    match endpoint:
        case ScryfallEndpoint.FUZZY:
            card = get_card_by_fuzzy_name(name)
            last_scryfall_call = time.time()
            return card

    return None

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