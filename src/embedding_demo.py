import math

from foundry_local_sdk import Configuration, FoundryLocalManager


EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

def cosine_similarity(vector_a, vector_b):
    """
    Iki vektor arasindaki cosine similarity skorunu hesaplar.

    Skor 1'e yakinsa metinler anlamca daha benzerdir.
    """
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def get_embedding(client, text):
    """
    Verilen metni embedding vektorune cevirir.
    """
    response = client.generate_embedding(text)
    return response.data[0].embedding


def main():
    print("Embedding demo baslatiliyor...")

    FoundryLocalManager.initialize(
        Configuration(app_name="foundry-local-rag-assistant")
    )
    manager = FoundryLocalManager.instance

    print("Embedding modeli aliniyor...")
    model = manager.catalog.get_model(EMBEDDING_MODEL_ALIAS)

    print("Embedding modeli indiriliyor veya cache kontrol ediliyor...")
    model.download(
        lambda progress: print(
            f"\rDownloading embedding model: {progress:.0f}%",
            end="",
            flush=True,
        )
    )

    print("\nEmbedding modeli yukleniyor...")
    model.load()

    client = model.get_embedding_client()

    documents = [
        {
            "id": 1,
            "text": "RAG reduces hallucinations by grounding answers in retrieved documents.",
        },
        {
            "id": 2,
            "text": "SQLite stores data in a local file without needing a separate server.",
        },
        {
            "id": 3,
            "text": "Foundry Local runs AI models directly on the user's device.",
        },
        {
            "id": 4,
            "text": "Embeddings convert text into numerical vectors for similarity search.",
        },
    ]

    query = "How does RAG make answers more reliable?"

    print("\nDokuman embedding'leri uretiliyor...")
    document_embeddings = []

    for document in documents:
        embedding = get_embedding(client, document["text"])

        document_embeddings.append(
            {
                "id": document["id"],
                "text": document["text"],
                "embedding": embedding,
            }
        )

        print(f"Dokuman {document['id']} embedding boyutu: {len(embedding)}")

    print("\nSoru embedding'e cevriliyor...")
    query_embedding = get_embedding(client, query)

    print(f"Soru: {query}")
    print(f"Soru embedding boyutu: {len(query_embedding)}")

    print("\nBenzerlik skorlari hesaplanıyor...")

    results = []

    for document in document_embeddings:
        score = cosine_similarity(query_embedding, document["embedding"])

        results.append(
            {
                "id": document["id"],
                "text": document["text"],
                "score": score,
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)

    print("\nSonuclar:")
    for result in results:
        print(f"- Skor: {result['score']:.4f} | Dokuman {result['id']}: {result['text']}")

    best_match = results[0]

    print("\nEn alakali dokuman:")
    print(f"Dokuman {best_match['id']}: {best_match['text']}")
    print(f"Benzerlik skoru: {best_match['score']:.4f}")

    print("\nEmbedding modeli kapatiliyor...")
    model.unload()

    print("Embedding demo tamamlandi.")


if __name__ == "__main__":
    main()