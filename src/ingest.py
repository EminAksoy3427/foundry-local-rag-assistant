import json

from src.chunker import chunk_documents
from src.db import (
    count_documents,
    initialize_database,
    insert_documents,
    reset_database,
)
from src.document_loader import load_documents
from src.embedder import LocalEmbedder


def serialize_embedding(embedding):
    """
    Embedding listesini SQLite'ta saklanabilecek JSON string'e cevirir.

    float() donusumu, embedding degerlerinin standart Python float
    olmasini garanti eder.
    """
    normalized_embedding = [float(value) for value in embedding]
    return json.dumps(normalized_embedding)


def prepare_chunks_for_storage(embedded_chunks):
    """
    Embedding iceren chunk'lari SQLite'a kaydedilecek bicime getirir.

    Embedding listesi dogrudan SQLite TEXT alanina yazilamaz.
    Bu nedenle embedding JSON string'e donusturulur.
    """
    storage_records = []

    for chunk in embedded_chunks:
        storage_records.append(
            {
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "embedding": serialize_embedding(chunk["embedding"]),
            }
        )

    return storage_records


def ingest_documents(reset=True):
    """
    Gercek dokumanlari okuyup SQLite veritabanina aktarir.

    Pipeline:
    1. Dokumanlari yukle
    2. Chunk'lara bol
    3. Her chunk icin embedding uret
    4. Embedding'leri JSON string'e cevir
    5. Chunk'lari SQLite'a kaydet
    6. Kayit sayisini dogrula
    """
    print("Dokumanlar yukleniyor...")
    documents = load_documents()

    if not documents:
        raise ValueError("Ingestion icin okunabilir dokuman bulunamadi.")

    print(f"Yuklenen dokuman sayisi: {len(documents)}")

    print("\nDokumanlar chunk'lara bolunuyor...")
    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError("Dokumanlardan chunk uretilemedi.")

    print(f"Uretilen chunk sayisi: {len(chunks)}")

    embedder = LocalEmbedder()

    try:
        print("\nChunk embedding'leri uretiliyor...")
        embedder.load()
        embedded_chunks = embedder.embed_chunks(chunks)
    finally:
        embedder.unload()

    print("\nEmbedding'ler JSON formatina ceviriliyor...")
    storage_records = prepare_chunks_for_storage(embedded_chunks)

    if reset:
        print("Documents tablosu sifirlaniyor...")
        reset_database()
    else:
        initialize_database()

    print("Chunk'lar SQLite'a kaydediliyor...")
    inserted_count = insert_documents(storage_records)

    stored_count = count_documents()

    return {
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "inserted_count": inserted_count,
        "stored_count": stored_count,
    }