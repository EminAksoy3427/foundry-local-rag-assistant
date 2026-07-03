from document_loader import DOCUMENTS_DIR, load_documents, preview_text


def main():
    print("Document loader demo baslatiliyor...")
    print(f"Dokuman klasoru: {DOCUMENTS_DIR}")

    documents = load_documents()

    print(f"\nBulunan dokuman sayisi: {len(documents)}")

    if not documents:
        print("Hic dokuman bulunamadi.")
        return

    for index, document in enumerate(documents, start=1):
        text = document["text"]

        print("-" * 60)
        print(f"Dokuman No: {index}")
        print(f"Source: {document['source']}")
        print(f"Karakter Sayisi: {len(text)}")
        print(f"Kelime Sayisi: {len(text.split())}")
        print(f"On Izleme: {preview_text(text)}")

    print("\nDocument loader demo tamamlandi.")


if __name__ == "__main__":
    main()