CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    set_code TEXT NOT NULL,
    set_name TEXT NOT NULL,
    collector_number TEXT,

    lang TEXT NOT NULL,
    released_at TEXT,

    type_line TEXT,
    oracle_text TEXT,
    cmc INTEGER,
    colors TEXT,
    color_identity TEXT,
    rarity TEXT,

    image_normal TEXT,
    layout TEXT,
    artist TEXT,
    full_art BOOLEAN,

    price_normal REAL,
    price_foil REAL,

    scryfall_uri TEXT
);

CREATE TABLE IF NOT EXISTS collection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT NOT NULL UNIQUE,
    language TEXT DEFAULT 'en',

    qty_normal INTEGER DEFAULT 0,
    qty_foil INTEGER DEFAULT 0,

    FOREIGN KEY(card_id) REFERENCES cards(id)
);

CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_set ON cards(set_code);
CREATE INDEX IF NOT EXISTS idx_collection_card ON collection(card_id);
