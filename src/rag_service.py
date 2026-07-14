from collections.abc import Callable

from src.context_builder import build_rag_prompt
from src.generator import LocalGenerator
from src.retrieval import (
    DEFAULT_MIN_SIMILARITY_SCORE,
    retrieve_top_chunks,
)


DEFAULT_TOP_K = 3
FALLBACK_ANSWER = "Bu bilgi verilen dokumanlarda bulunmuyor."


def answer_question(
    question,
    top_k=DEFAULT_TOP_K,
    min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
    on_token: Callable[[str], None] | None = None,
):
    """
    Kullanici sorusunu uctan uca local RAG pipeline'inda isler.

    Yeterli benzerlik skoruna sahip chunk bulunursa local LLM cevabi
    uretilir. Yeterli baglam yoksa chat modeli yuklenmeden guvenli
    fallback cevabi dondurulur.
    """
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Kullanici sorusu bos olamaz.")

    if top_k <= 0:
        raise ValueError("top_k sifirdan buyuk olmalidir.")

    if not -1.0 <= min_similarity_score <= 1.0:
        raise ValueError(
            "Minimum benzerlik skoru -1.0 ile 1.0 arasinda olmalidir."
        )

    print("RAG servisi: ilgili chunk'lar getiriliyor...")
    candidate_chunks = retrieve_top_chunks(
        query=cleaned_question,
        top_k=top_k,
    )

    top_similarity_score = (
        candidate_chunks[0]["similarity_score"]
        if candidate_chunks
        else None
    )

    has_sufficient_context = (
        top_similarity_score is not None
        and top_similarity_score >= min_similarity_score
)

    relevant_chunks = (
        candidate_chunks
        if has_sufficient_context
        else []
)

    print(
        "\nRAG servisi: retrieval guvenligi kontrol ediliyor..."
    )
    print(f"Minimum benzerlik esigi: {min_similarity_score:.4f}")

    if top_similarity_score is not None:
        print(f"En yuksek benzerlik skoru: {top_similarity_score:.4f}")

    print(
        "Context icin kullanilan chunk sayisi: "
        f"{len(relevant_chunks)}"
)

    if not has_sufficient_context:
        print(
            "Yeterli baglam bulunamadi. "
            "Yerel chat modeli yuklenmeyecek."
        )

        if on_token is not None:
            on_token(FALLBACK_ANSWER)
            print()

        return {
            "question": cleaned_question,
            "answer": FALLBACK_ANSWER,
            "status": "insufficient_context",
            "source_references": [],
            "retrieved_chunks": [],
            "candidate_chunks": candidate_chunks,
            "model_alias": None,
            "top_similarity_score": top_similarity_score,
            "min_similarity_score": min_similarity_score,
        }

    print("\nRAG servisi: context ve prompt'lar olusturuluyor...")
    rag_prompt = build_rag_prompt(
        question=cleaned_question,
        retrieved_chunks=relevant_chunks,
    )

    generator = LocalGenerator()

    try:
        print("\nRAG servisi: yerel chat modeli yukleniyor...")
        generator.load()

        print("\nRAG servisi: cevap uretiliyor...")
        answer = generator.generate(
            system_prompt=rag_prompt["system_prompt"],
            user_prompt=rag_prompt["user_prompt"],
            on_token=on_token,
        )
    finally:
        if on_token is not None:
            print()

        generator.unload()

    return {
        "question": cleaned_question,
        "answer": answer,
        "status": "answered",
        "source_references": rag_prompt["source_references"],
        "retrieved_chunks": relevant_chunks,
        "candidate_chunks": candidate_chunks,
        "model_alias": generator.model_alias,
        "top_similarity_score": top_similarity_score,
        "min_similarity_score": min_similarity_score,
    }