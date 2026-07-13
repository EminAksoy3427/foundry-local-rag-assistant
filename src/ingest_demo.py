import json

from src.db import fetch_all_documents
from src.ingest import ingest_documents


def preview_text(text, max_length=100):
    """
    Uzun chunk metnini terminalde kisa gostermek icin kullanilir.
    """
    single_line_text = " ".join(text.split())

    if len(single_line_text) <= max_length:
        return single_line_text

    return single_line_text[:max_length] + "..."


def main():
    print("SQLite ingestion demo baslatiliyor...\n")

    summary = ingest_documents(reset=True)

    print("\nSQLite kayitlari okunuyor...")
    stored_documents = fetch_all_documents()

    expected_count = summary["chunk_count"]
    actual_count = len(stored_documents)

    if actual_count != expected_count:
        raise RuntimeError(
            "SQLite kayit sayisi beklenen chunk sayisiyla uyusmuyor. "
            f"Beklenen: {expected_count}, bulunan: {actual_count}"
        )

    print("\nIngestion basariyla tamamlandi.")
    print(f"Yuklenen dokuman sayisi: {summary['document_count']}")
    print(f"Uretilen chunk sayisi: {summary['chunk_count']}")
    print(f"SQLite'a eklenen kayit sayisi: {summary['inserted_count']}")
    print(f"SQLite'tan okunan kayit sayisi: {actual_count}")

    if stored_documents:
        first_document = stored_documents[0]
        restored_embedding = json.loads(first_document["embedding"])

        print("\nIlk SQLite kaydi:")
        print(f"ID: {first_document['id']}")
        print(f"Kaynak: {first_document['source']}")
        print(f"Chunk index: {first_document['chunk_index']}")
        print(f"Embedding boyutu: {len(restored_embedding)}")
        print(
            "Chunk on izlemesi: "
            f"{preview_text(first_document['chunk_text'])}"
        )


if __name__ == "__main__":
    main()