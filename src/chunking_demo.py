from chunker import chunk_documents
from document_loader import load_documents, preview_text


def main():
    print("Chunking demo baslatiliyor...")

    documents = load_documents()
    print(f"Yuklenen dokuman sayisi: {len(documents)}")

    chunks = chunk_documents(documents)
    print(f"Uretilen chunk sayisi: {len(chunks)}")

    print("\nChunk listesi:")

    for chunk in chunks:
        print("-" * 60)
        print(f"Source: {chunk['source']}")
        print(f"Chunk Index: {chunk['chunk_index']}")
        print(f"Karakter Sayisi: {len(chunk['chunk_text'])}")
        print(f"Kelime Sayisi: {len(chunk['chunk_text'].split())}")
        print(f"On Izleme: {preview_text(chunk['chunk_text'])}")

    print("\nChunking demo tamamlandi.")


if __name__ == "__main__":
    main()