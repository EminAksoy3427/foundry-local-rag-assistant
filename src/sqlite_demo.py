from db import (
    DB_PATH,
    count_documents,
    fetch_all_documents,
    insert_document,
    reset_database,
)


def main():
    print("SQLite demo baslatiliyor...")
    print(f"Veritabani yolu: {DB_PATH}")

    print("\nDemo icin documents tablosu sifirlaniyor...")
    reset_database()

    sample_chunks = [
        {
            "source": "rag_notes.txt",
            "chunk_index": 1,
            "chunk_text": "RAG retrieves relevant document chunks before generating an answer.",
        },
        {
            "source": "foundry_local_notes.txt",
            "chunk_index": 1,
            "chunk_text": "Foundry Local runs AI models directly on the user's device.",
        },
        {
            "source": "sqlite_notes.txt",
            "chunk_index": 1,
            "chunk_text": "SQLite stores application data in a single local database file.",
        },
    ]

    print("\nOrnek dokuman parcalari SQLite'a kaydediliyor...")

    for chunk in sample_chunks:
        new_id = insert_document(
            source=chunk["source"],
            chunk_index=chunk["chunk_index"],
            chunk_text=chunk["chunk_text"],
        )

        print(f"Kayit eklendi. ID: {new_id} | Source: {chunk['source']}")

    total_count = count_documents()
    print(f"\nToplam kayit sayisi: {total_count}")

    print("\nSQLite'tan kayitlar okunuyor...")

    documents = fetch_all_documents()

    for document in documents:
        print("-" * 60)
        print(f"ID: {document['id']}")
        print(f"Source: {document['source']}")
        print(f"Chunk Index: {document['chunk_index']}")
        print(f"Text: {document['chunk_text']}")
        print(f"Embedding: {document['embedding']}")
        print(f"Created At: {document['created_at']}")

    print("\nSQLite demo tamamlandi.")


if __name__ == "__main__":
    main()