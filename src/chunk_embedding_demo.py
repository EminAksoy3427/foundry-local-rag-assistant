from chunker import chunk_documents
from document_loader import load_documents, preview_text
from embedder import LocalEmbedder


def main():
    print("Chunk embedding demo baslatiliyor...")

    print("\nDokumanlar yukleniyor...")
    documents = load_documents()
    print(f"Yuklenen dokuman sayisi: {len(documents)}")

    print("\nDokumanlar chunk'lara bolunuyor...")
    chunks = chunk_documents(documents)
    print(f"Uretilen chunk sayisi: {len(chunks)}")

    if not chunks:
        print("Embedding uretilecek chunk bulunamadi.")
        return

    embedder = LocalEmbedder()

    try:
        embedder.load()

        print("\nChunk embedding'leri uretiliyor...")
        embedded_chunks = embedder.embed_chunks(chunks)

        print("\nEmbedding uretimi tamamlandi.")
        print(f"Embedding uretilen chunk sayisi: {len(embedded_chunks)}")

        first_chunk = embedded_chunks[0]

        print("\nIlk embedded chunk ornegi:")
        print(f"Source: {first_chunk['source']}")
        print(f"Chunk Index: {first_chunk['chunk_index']}")
        print(f"Chunk Text Preview: {preview_text(first_chunk['chunk_text'])}")
        print(f"Embedding Boyutu: {len(first_chunk['embedding'])}")
        print(f"Embedding Ilk 5 Deger: {first_chunk['embedding'][:5]}")

        print("\nTum chunk embedding ozetleri:")

        for chunk in embedded_chunks:
            print("-" * 60)
            print(f"Source: {chunk['source']}")
            print(f"Chunk Index: {chunk['chunk_index']}")
            print(f"Text Preview: {preview_text(chunk['chunk_text'])}")
            print(f"Embedding Dimension: {len(chunk['embedding'])}")

    finally:
        embedder.unload()

    print("\nChunk embedding demo tamamlandi.")


if __name__ == "__main__":
    main()