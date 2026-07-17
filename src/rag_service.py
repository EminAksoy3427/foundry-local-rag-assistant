from collections.abc import Callable

from src.context_builder import build_rag_prompt
from src.generator import LocalGenerator
from src.retrieval import (
    DEFAULT_MIN_SIMILARITY_SCORE,
    DEFAULT_RETRIEVAL_CANDIDATE_MULTIPLIER,
    rank_candidate_sources,
    retrieve_top_chunks,
    select_context_chunks_by_primary_source,
)


DEFAULT_TOP_K = 3

FALLBACK_ANSWER = (
    "Bu bilgi verilen dokumanlarda bulunmuyor."
)


def answer_question(
    question,
    top_k=DEFAULT_TOP_K,
    min_similarity_score=(
        DEFAULT_MIN_SIMILARITY_SCORE
    ),
    on_token: Callable[[str], None] | None = None,
):
    """
    Kullanici sorusunu uctan uca local RAG
    pipeline'inda isler.

    Akis:
    1. Genis bir retrieval aday havuzu getirir
    2. En yuksek semantik skorla baglam
       yeterliligini kontrol eder
    3. Adaylari kaynak duzeyinde hibrit olarak
       siralar
    4. En guclu kaynagin en iyi chunk'larini
       context olarak secer
    5. Yeterli baglam varsa local LLM cevabi
       uretir
    6. Yeterli baglam yoksa modeli yuklemeden
       guvenli fallback dondurur
    """
    cleaned_question = str(question).strip()

    if not cleaned_question:
        raise ValueError(
            "Kullanici sorusu bos olamaz."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k sifirdan buyuk olmalidir."
        )

    if not (
        -1.0
        <= min_similarity_score
        <= 1.0
    ):
        raise ValueError(
            "Minimum benzerlik skoru -1.0 ile "
            "1.0 arasinda olmalidir."
        )

    retrieval_candidate_k = max(
        top_k
        * DEFAULT_RETRIEVAL_CANDIDATE_MULTIPLIER,
        top_k,
    )

    print(
        "RAG servisi: ilgili chunk'lar "
        "getiriliyor..."
    )

    candidate_chunks = retrieve_top_chunks(
        query=cleaned_question,
        top_k=retrieval_candidate_k,
    )

    top_similarity_score = (
        float(
            candidate_chunks[0][
                "similarity_score"
            ]
        )
        if candidate_chunks
        else None
    )

    semantic_top_source = (
        candidate_chunks[0]["source"]
        if candidate_chunks
        else None
    )

    has_sufficient_context = (
        top_similarity_score is not None
        and top_similarity_score
        >= min_similarity_score
    )

    source_rankings = (
        rank_candidate_sources(
            question=cleaned_question,
            candidate_chunks=candidate_chunks,
        )
        if candidate_chunks
        else []
    )

    ranked_primary_source = (
        source_rankings[0]["source"]
        if source_rankings
        else None
    )

    if has_sufficient_context:
        relevant_chunks = (
            select_context_chunks_by_primary_source(
                question=cleaned_question,
                candidate_chunks=candidate_chunks,
                context_top_k=top_k,
                source_rankings=source_rankings,
            )
        )

        primary_source = ranked_primary_source
    else:
        relevant_chunks = []
        primary_source = None

    print(
        "\nRAG servisi: retrieval guvenligi "
        "kontrol ediliyor..."
    )

    print(
        "Minimum benzerlik esigi: "
        f"{min_similarity_score:.4f}"
    )

    if top_similarity_score is not None:
        print(
            "En yuksek benzerlik skoru: "
            f"{top_similarity_score:.4f}"
        )

    print(
        "Retrieval aday havuzu: "
        f"{len(candidate_chunks)}"
    )

    print(
        "Context icin kullanilan chunk sayisi: "
        f"{len(relevant_chunks)}"
    )

    print(f"Ana kaynak: {primary_source}")

    if (
        has_sufficient_context
        and source_rankings
    ):
        print("Kaynak secim skorlari:")

        for ranking in source_rankings:
            print(
                f"- {ranking['source']} "
                f"| semantic: "
                f"{ranking['semantic_score']:.4f} "
                f"| lexical: "
                f"{ranking['lexical_coverage']:.4f} "
                f"| combined: "
                f"{ranking['selection_score']:.4f}"
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
            "top_similarity_score": (
                top_similarity_score
            ),
            "min_similarity_score": (
                min_similarity_score
            ),
            "retrieval_candidate_k": (
                retrieval_candidate_k
            ),
            "semantic_top_source": (
                semantic_top_source
            ),
            "ranked_primary_source": (
                ranked_primary_source
            ),
            "primary_source": None,
            "source_rankings": source_rankings,
        }

    print(
        "\nRAG servisi: context ve prompt'lar "
        "olusturuluyor..."
    )

    rag_prompt = build_rag_prompt(
        question=cleaned_question,
        retrieved_chunks=relevant_chunks,
    )

    generator = LocalGenerator()
    model_alias = None

    try:
        print(
            "\nRAG servisi: yerel chat modeli "
            "yukleniyor..."
        )

        generator.load()
        model_alias = generator.model_alias

        print(
            "\nRAG servisi: cevap uretiliyor..."
        )

        answer = generator.generate(
            system_prompt=rag_prompt[
                "system_prompt"
            ],
            user_prompt=rag_prompt[
                "user_prompt"
            ],
            on_token=on_token,
        )
    finally:
        if on_token is not None:
            print()

        generator.unload()

    cleaned_answer = str(answer).strip()

    return {
        "question": cleaned_question,
        "answer": cleaned_answer,
        "status": "answered",
        "source_references": rag_prompt[
            "source_references"
        ],
        "retrieved_chunks": relevant_chunks,
        "candidate_chunks": candidate_chunks,
        "model_alias": model_alias,
        "top_similarity_score": (
            top_similarity_score
        ),
        "min_similarity_score": (
            min_similarity_score
        ),
        "retrieval_candidate_k": (
            retrieval_candidate_k
        ),
        "semantic_top_source": (
            semantic_top_source
        ),
        "ranked_primary_source": (
            ranked_primary_source
        ),
        "primary_source": primary_source,
        "source_rankings": source_rankings,
    }