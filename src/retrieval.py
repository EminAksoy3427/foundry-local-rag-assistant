import json
import math
import re

from src.db import fetch_all_documents
from src.embedder import LocalEmbedder


DEFAULT_MIN_SIMILARITY_SCORE = 0.60
DEFAULT_RETRIEVAL_CANDIDATE_MULTIPLIER = 3

SOURCE_LEXICAL_WEIGHT = 0.05
LEXICAL_PREFIX_LENGTH = 5

LEXICAL_STOP_WORDS = {
    "bir",
    "bu",
    "ve",
    "ile",
    "icin",
    "neden",
    "nasil",
    "nedir",
    "ne",
    "hangi",
    "mi",
    "mu",
    "midir",
    "sistem",
    "sistemi",
    "sisteminde",
}

TURKISH_CHARACTER_MAP = str.maketrans(
    {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
        "Ç": "c",
        "Ğ": "g",
        "İ": "i",
        "I": "i",
        "Ö": "o",
        "Ş": "s",
        "Ü": "u",
    }
)


def cosine_similarity(vector_a, vector_b):
    """
    Iki embedding vektoru arasindaki cosine similarity
    skorunu hesaplar.

    Sonuc genellikle -1 ile 1 arasindadir.
    Skor 1'e yaklastikca metinlerin anlamsal
    benzerligi artar.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding boyutlari birbiriyle uyusmuyor. "
            f"Birinci: {len(vector_a)}, "
            f"ikinci: {len(vector_b)}"
        )

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def deserialize_embedding(embedding_text):
    """
    SQLite TEXT alaninda saklanan JSON embedding'i
    Python listesine cevirir.
    """
    if not embedding_text:
        raise ValueError(
            "SQLite kaydinda embedding bulunamadi."
        )

    embedding = json.loads(embedding_text)

    if not isinstance(embedding, list):
        raise ValueError(
            "Embedding JSON verisi bir liste degil."
        )

    return [
        float(value)
        for value in embedding
    ]


def rank_documents(
    query_embedding,
    stored_documents,
):
    """
    Kullanici sorusunun embedding'ini tum SQLite
    kayitlariyla karsilastirir.

    Her kayda similarity_score ekler ve sonuclari
    en yuksek skordan en dusuk skora dogru siralar.
    """
    ranked_documents = []

    for document in stored_documents:
        stored_embedding = deserialize_embedding(
            document["embedding"]
        )

        similarity_score = cosine_similarity(
            query_embedding,
            stored_embedding,
        )

        ranked_documents.append(
            {
                "id": document["id"],
                "source": document["source"],
                "chunk_index": document[
                    "chunk_index"
                ],
                "chunk_text": document["chunk_text"],
                "similarity_score": similarity_score,
            }
        )

    ranked_documents.sort(
        key=lambda document: document[
            "similarity_score"
        ],
        reverse=True,
    )

    return ranked_documents


def retrieve_top_chunks(
    query,
    top_k=3,
):
    """
    Kullanici sorusu icin en alakali top-k chunk'i
    getirir.

    Adimlar:
    1. Sorunun embedding'ini uret
    2. SQLite kayitlarini oku
    3. Cosine similarity skorlarini hesapla
    4. Sonuclari sirala
    5. En yuksek skorlu top-k chunk'i dondur
    """
    cleaned_query = str(query).strip()

    if not cleaned_query:
        raise ValueError(
            "Arama sorgusu bos olamaz."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k sifirdan buyuk olmalidir."
        )

    stored_documents = fetch_all_documents()

    if not stored_documents:
        raise ValueError(
            "SQLite veritabaninda aranacak dokuman "
            "bulunamadi. Once ingestion pipeline "
            "calistirilmali."
        )

    embedder = LocalEmbedder()

    try:
        print("Soru embedding'i uretiliyor...")
        embedder.load()

        query_embedding = embedder.embed_text(
            cleaned_query
        )
    finally:
        embedder.unload()

    ranked_documents = rank_documents(
        query_embedding=query_embedding,
        stored_documents=stored_documents,
    )

    return ranked_documents[:top_k]


def normalize_for_lexical_match(text):
    """
    Metni basit kelime eslestirmesi icin
    normalize eder.
    """
    normalized = str(text).translate(
        TURKISH_CHARACTER_MAP
    )

    normalized = normalized.lower()

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    ).strip()


def tokenize_for_lexical_match(text):
    """
    Normalize edilmis metni anlamli ve benzersiz
    kelimelere ayirir.
    """
    tokens = []
    seen_tokens = set()

    normalized_text = normalize_for_lexical_match(
        text
    )

    for token in normalized_text.split():
        if len(token) < 3:
            continue

        if token in LEXICAL_STOP_WORDS:
            continue

        if token in seen_tokens:
            continue

        tokens.append(token)
        seen_tokens.add(token)

    return tokens


def lexical_tokens_match(
    left_token,
    right_token,
):
    """
    Tam kelime veya ortak kok benzeri on ek
    eslesmesini kontrol eder.

    Ornek:
    - bilgi / bilgilerini
    - saklar / saklamak
    """
    if left_token == right_token:
        return True

    if (
        len(left_token) < LEXICAL_PREFIX_LENGTH
        or len(right_token)
        < LEXICAL_PREFIX_LENGTH
    ):
        return False

    return (
        left_token[:LEXICAL_PREFIX_LENGTH]
        == right_token[:LEXICAL_PREFIX_LENGTH]
    )


def calculate_source_query_coverage(
    question,
    source_chunks,
):
    """
    Sorudaki anlamli kelimelerin ne kadarinin
    bir kaynagin aday chunk'larinda karsilandigini
    hesaplar.
    """
    question_tokens = tokenize_for_lexical_match(
        question
    )

    if not question_tokens:
        return 0.0

    if not source_chunks:
        return 0.0

    combined_source_text = " ".join(
        (
            f"{chunk['source']} "
            f"{chunk['chunk_text']}"
        )
        for chunk in source_chunks
    )

    source_tokens = tokenize_for_lexical_match(
        combined_source_text
    )

    matched_question_tokens = 0

    for question_token in question_tokens:
        token_matched = any(
            lexical_tokens_match(
                question_token,
                source_token,
            )
            for source_token in source_tokens
        )

        if token_matched:
            matched_question_tokens += 1

    return (
        matched_question_tokens
        / len(question_tokens)
    )


def rank_candidate_sources(
    question,
    candidate_chunks,
    lexical_weight=SOURCE_LEXICAL_WEIGHT,
):
    """
    Retrieval adaylarini kaynaklara gore gruplar
    ve kaynak duzeyinde siralar.

    Kaynak secim skoru:

        en yuksek semantik skor
        +
        lexical agirlik * soru kapsama orani

    Bu yontem, semantik skorlari birbirine cok
    yakin olan kaynaklarda sorudaki belirgin
    kavramlari daha iyi karsilayan dokumani
    one cikarir.
    """
    if not 0.0 <= lexical_weight <= 1.0:
        raise ValueError(
            "lexical_weight 0.0 ile 1.0 "
            "arasinda olmalidir."
        )

    if not candidate_chunks:
        return []

    grouped_chunks = {}

    for chunk in candidate_chunks:
        source = chunk["source"]

        grouped_chunks.setdefault(
            source,
            [],
        ).append(chunk)

    source_rankings = []

    for source, source_chunks in (
        grouped_chunks.items()
    ):
        semantic_score = max(
            float(chunk["similarity_score"])
            for chunk in source_chunks
        )

        lexical_coverage = (
            calculate_source_query_coverage(
                question=question,
                source_chunks=source_chunks,
            )
        )

        selection_score = (
            semantic_score
            + lexical_weight * lexical_coverage
        )

        source_rankings.append(
            {
                "source": source,
                "semantic_score": semantic_score,
                "lexical_coverage": (
                    lexical_coverage
                ),
                "selection_score": selection_score,
                "candidate_chunk_count": len(
                    source_chunks
                ),
            }
        )

    source_rankings.sort(
        key=lambda item: (
            -item["selection_score"],
            -item["semantic_score"],
            item["source"],
        )
    )

    return source_rankings


def select_context_chunks_by_primary_source(
    question,
    candidate_chunks,
    context_top_k=3,
    source_rankings=None,
):
    """
    Hibrit kaynak siralamasinda ilk gelen kaynaga
    ait en guclu chunk'lari context olarak secer.

    source_rankings daha once hesaplandiysa tekrar
    hesaplama yapmamak icin parametre olarak
    verilebilir.
    """
    if context_top_k <= 0:
        raise ValueError(
            "context_top_k sifirdan buyuk "
            "olmalidir."
        )

    if not candidate_chunks:
        return []

    if source_rankings is None:
        source_rankings = rank_candidate_sources(
            question=question,
            candidate_chunks=candidate_chunks,
        )

    if not source_rankings:
        return []

    primary_source = source_rankings[0][
        "source"
    ]

    primary_source_chunks = [
        chunk
        for chunk in candidate_chunks
        if chunk["source"] == primary_source
    ]

    primary_source_chunks.sort(
        key=lambda chunk: chunk[
            "similarity_score"
        ],
        reverse=True,
    )

    return primary_source_chunks[
        :context_top_k
    ]