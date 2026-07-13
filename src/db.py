from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "storage" / "rag.db"


def get_connection():
    """
    SQLite veritabanina baglanti olusturur.

    Veritabani dosyasi yoksa SQLite otomatik olarak olusturur.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """
    RAG projesi icin gerekli documents tablosunu olusturur.
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def reset_database():
    """
    Demo amacli olarak documents tablosunu sifirlar.

    Dikkat: Bu fonksiyon mevcut documents tablosunu siler.
    """
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS documents")
        conn.commit()

    initialize_database()


def insert_document(source, chunk_index, chunk_text, embedding=None):
    """
    Bir dokuman parcasini SQLite'a kaydeder.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO documents (source, chunk_index, chunk_text, embedding)
            VALUES (?, ?, ?, ?)
            """,
            (source, chunk_index, chunk_text, embedding),
        )
        conn.commit()

        return cursor.lastrowid


def fetch_all_documents():
    """
    SQLite icindeki tum dokuman parcalarini getirir.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(
            """
            SELECT id, source, chunk_index, chunk_text, embedding, created_at
            FROM documents
            ORDER BY id
            """
        )
        rows = cursor.fetchall()

        return [dict(row) for row in rows]
    finally:
        conn.close()


def count_documents():
    """
    documents tablosundaki toplam kayit sayisini dondurur.
    """
    with get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM documents")
        return cursor.fetchone()[0]
    
def insert_documents(documents):
    """
    Birden fazla dokuman chunk'ini tek transaction ile SQLite'a kaydeder.

    Her document sozlugu su alanlari icermelidir:
    - source
    - chunk_index
    - chunk_text
    - embedding
    """
    rows = [
        (
            document["source"],
            document["chunk_index"],
            document["chunk_text"],
            document.get("embedding"),
        )
        for document in documents
    ]

    if not rows:
        return 0

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO documents (
                source,
                chunk_index,
                chunk_text,
                embedding
            )
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()

    return len(rows)