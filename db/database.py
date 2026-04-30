import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "collection.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
BULK_PATH = Path("data/bulk_data.json")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    ensure_collection_card_id_unique(conn)
    conn.commit()
    conn.close()    


def ensure_collection_card_id_unique(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA index_list('collection')")
    indexes = [row[1] for row in cursor.fetchall()]
    if "idx_collection_card_unique" in indexes:
        return

    try:
        cursor.execute("CREATE UNIQUE INDEX idx_collection_card_unique ON collection(card_id)")
    except sqlite3.OperationalError:
        cursor.execute("BEGIN")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS collection_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT NOT NULL UNIQUE,
                language TEXT DEFAULT 'en',
                qty_normal INTEGER DEFAULT 0,
                qty_foil INTEGER DEFAULT 0,
                FOREIGN KEY(card_id) REFERENCES cards(id)
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO collection_new (card_id, language, qty_normal, qty_foil)
            SELECT card_id, language, SUM(qty_normal), SUM(qty_foil)
            FROM collection
            GROUP BY card_id, language
            """
        )
        cursor.execute("DROP TABLE collection")
        cursor.execute("ALTER TABLE collection_new RENAME TO collection")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_collection_card_unique ON collection(card_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collection_card ON collection(card_id)")
        conn.commit()


def is_table_empty(cursor, table_name: str) -> bool:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count == 0
    
def import_bulk(initial_import=False):
    conn = get_connection()
    cursor = conn.cursor()

    if initial_import and not is_table_empty(cursor, "cards"):
        conn.close()
        return

    with open(BULK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor.execute("BEGIN")

    for card in data:
        if card.get("card_faces"):
            oracle_text = "\n---\n".join(face.get("oracle_text", "") for face in card["card_faces"])
        else:
            oracle_text = card.get("oracle_text")
        cursor.execute(
            """
            INSERT OR REPLACE INTO cards (
                id, name, set_code, set_name, collector_number, 
                lang, released_at, type_line, oracle_text, cmc, 
                colors, color_identity, rarity, image_normal, 
                layout, artist, full_art, price_normal, price_foil,
                scryfall_uri
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card["id"],
                card.get("name"),
                card.get("set"),
                card.get("set_name"),
                card.get("collector_number"),
                card.get("lang"),
                card.get("released_at"),
                card.get("type_line"),
                oracle_text,
                card.get("cmc"),
                ",".join(card.get("colors", [])),
                ",".join(card.get("color_identity")),
                card.get("rarity"),
                card.get("image_uris", {}).get("normal"),
                card.get("layout"),
                card.get("artist"),
                int(card.get("full_art", False)),
                card.get("prices", {}).get("usd"),
                card.get("prices", {}).get("usd_foil"),
                card.get("scryfall_uri"),
            ),
        )

    conn.commit()
    conn.close()

def add_card_to_collection(card_id, qty=1, foil=False):
    conn = get_connection()
    cursor = conn.cursor()
    
    qty_normal = qty if not foil else 0
    qty_foil = qty if foil else 0

    cursor.execute(
        """
        INSERT INTO collection (card_id, qty_normal, qty_foil)
        VALUES (?, ?, ?)
        ON CONFLICT(card_id)
        DO UPDATE SET qty_normal = qty_normal + excluded.qty_normal,
                      qty_foil = qty_foil + excluded.qty_foil
        """,
        (card_id, qty_normal, qty_foil),
    )

    conn.commit()
    conn.close()

def remove_card_from_collection(card_id, qty=1, foil=False):
    conn = get_connection()
    cursor = conn.cursor()
    
    qty_normal = qty if not foil else 0
    qty_foil = qty if foil else 0

    cursor.execute(
        """
        INSERT INTO collection (card_id, qty_normal, qty_foil)
        VALUES (?, ?, ?)
        ON CONFLICT(card_id)
        DO UPDATE SET qty_normal = qty_normal - excluded.qty_normal,
                      qty_foil = qty_foil - excluded.qty_foil
        """,
        (card_id, qty_normal, qty_foil),
    )

    conn.commit()
    conn.close()
    
def load_collection():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.name, c.set_name, col.qty_normal, col.qty_foil, c.price_normal
        FROM collection col
        JOIN cards c ON c.id = col.card_id
        ORDER BY c.name
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows

if __name__ == "__main__":
    init_db()
    import_bulk()
