import json
import math

from src.db import fetch_all_documents
from src.embedder import LocalEmbedder


def cosine_similarity(vector_a, vector_b):
    """
    Iki embedding vektoru arasindaki cosine similarity skorunu hesaplar.

    Sonuc genellikle -1 ile 1 arasindadir.
    Skor 1'e yaklastikca metinlerin anlamsal benzerligi artar.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding boyutlari birbiriyle uyusmuyor. "
            f"Birinci: {len(vector_a)}, ikinci: {len(vector_b)}"
        )

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a)
    )
    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def deserialize_embedding(embedding_text):
    """
    SQLite TEXT alaninda saklanan JSON embedding'i Python listesine cevirir.
    """
    if not embedding_text:
        raise ValueError("SQLite kaydinda embedding bulunamadi.")

    embedding = json.loads(embedding_text)

    if not isinstance(embedding, list):
        raise ValueError("Embedding JSON verisi bir liste degil.")

    return [float(value) for value in embedding]


def rank_documents(query_embedding, stored_documents):
    """
    Kullanici sorusunun embedding'ini tum SQLite kayitlariyla karsilastirir.

    Her kayda similarity_score ekler ve sonuclari en yuksek
    skordan en dusuk skora dogru siralar.
    """
    ranked_documents = []

    for document in stored_documents:
        stored_embedding = deserialize_embedding(document["embedding"])

        similarity_score = cosine_similarity(
            query_embedding,
            stored_embedding,
        )

        ranked_documents.append(
            {
                "id": document["id"],
                "source": document["source"],
                "chunk_index": document["chunk_index"],
                "chunk_text": document["chunk_text"],
                "similarity_score": similarity_score,
            }
        )

    ranked_documents.sort(
        key=lambda document: document["similarity_score"],
        reverse=True,
    )

    return ranked_documents


def retrieve_top_chunks(query, top_k=3):
    """
    Kullanici sorusu icin en alakali top-k chunk'i getirir.

    Adimlar:
    1. Sorunun embedding'ini uret
    2. SQLite kayitlarini oku
    3. Cosine similarity skorlarini hesapla
    4. Sonuclari sirala
    5. En yuksek skorlu top-k chunk'i dondur
    """
    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("Arama sorgusu bos olamaz.")

    if top_k <= 0:
        raise ValueError("top_k sifirdan buyuk olmalidir.")

    stored_documents = fetch_all_documents()

    if not stored_documents:
        raise ValueError(
            "SQLite veritabaninda aranacak dokuman bulunamadi. "
            "Once ingestion pipeline calistirilmali."
        )

    embedder = LocalEmbedder()

    try:
        print("Soru embedding'i uretiliyor...")
        embedder.load()
        query_embedding = embedder.embed_text(cleaned_query)
    finally:
        embedder.unload()

    ranked_documents = rank_documents(
        query_embedding=query_embedding,
        stored_documents=stored_documents,
    )

    return ranked_documents[:top_k]