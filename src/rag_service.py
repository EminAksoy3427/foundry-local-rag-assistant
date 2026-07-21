from collections.abc import Callable
from time import perf_counter

from src.context_builder import build_rag_prompt
from src.embedder import LocalEmbedder
from src.generator import LocalGenerator
from src.retrieval import (
    DEFAULT_MIN_SIMILARITY_SCORE,
    DEFAULT_RETRIEVAL_CANDIDATE_MULTIPLIER,
    rank_candidate_sources,
    retrieve_top_chunks_with_metrics,
    select_context_chunks_by_primary_source,
)


DEFAULT_TOP_K = 3

FALLBACK_ANSWER = (
    "Bu bilgi verilen dokumanlarda bulunmuyor."
)


def create_empty_generation_metrics():
    """
    Generation calismadiginda veya henuz
    baslamadiginda kullanilacak bos metrik
    sozlugunu olusturur.

    Cevaplanamaz sorularda bu alanlar sifir
    olarak kalir.
    """
    return {
        "time_to_first_token_seconds": 0.0,
        "generation_total_seconds": 0.0,
        "streaming_seconds": 0.0,
        "streaming_chunk_count": 0,
        "answer_character_count": 0,
    }


def create_empty_performance_metrics():
    """
    Tek bir RAG isteginde olculecek tum
    performans metriklerini olusturur.

    Retrieval, model yasam dongusu, generation
    ve toplam servis sureleri ayni sozlukte
    tutulur.
    """
    return {
        "database_read_seconds": 0.0,
        "embedding_model_load_seconds": 0.0,
        "query_embedding_seconds": 0.0,
        "embedding_model_unload_seconds": 0.0,
        "similarity_ranking_seconds": 0.0,
        "retrieval_total_seconds": 0.0,
        "source_ranking_seconds": 0.0,
        "context_selection_seconds": 0.0,
        "prompt_build_seconds": 0.0,
        "chat_model_load_seconds": 0.0,
        "time_to_first_token_seconds": 0.0,
        "generation_seconds": 0.0,
        "streaming_seconds": 0.0,
        "streaming_chunk_count": 0,
        "answer_character_count": 0,
        "chat_model_unload_seconds": 0.0,
        "service_total_seconds": 0.0,
    }


def print_performance_metrics(
    performance_metrics,
):
    """
    RAG isteginin performans metriklerini
    okunabilir bicimde terminale yazdirir.
    """
    print(
        "\nRAG SERVISI PERFORMANS METRIKLERI"
    )

    duration_metric_labels = {
        "database_read_seconds": (
            "SQLite okuma"
        ),
        "embedding_model_load_seconds": (
            "Embedding modeli yukleme"
        ),
        "query_embedding_seconds": (
            "Soru embedding'i uretme"
        ),
        "embedding_model_unload_seconds": (
            "Embedding modeli kapatma"
        ),
        "similarity_ranking_seconds": (
            "Similarity ve siralama"
        ),
        "retrieval_total_seconds": (
            "Toplam retrieval"
        ),
        "source_ranking_seconds": (
            "Hibrit kaynak siralama"
        ),
        "context_selection_seconds": (
            "Context secimi"
        ),
        "prompt_build_seconds": (
            "Prompt hazirlama"
        ),
        "chat_model_load_seconds": (
            "Chat modeli yukleme"
        ),
        "time_to_first_token_seconds": (
            "Ilk metin parcasina kadar gecen sure"
        ),
        "generation_seconds": (
            "Toplam cevap uretme"
        ),
        "streaming_seconds": (
            "Ilk parcadan sonra streaming"
        ),
        "chat_model_unload_seconds": (
            "Chat modeli kapatma"
        ),
        "service_total_seconds": (
            "Toplam RAG servis suresi"
        ),
    }

    for metric_name, label in (
        duration_metric_labels.items()
    ):
        value = float(
            performance_metrics.get(
                metric_name,
                0.0,
            )
        )

        print(
            f"- {label}: "
            f"{value:.4f} saniye"
        )

    streaming_chunk_count = int(
        performance_metrics.get(
            "streaming_chunk_count",
            0,
        )
    )

    answer_character_count = int(
        performance_metrics.get(
            "answer_character_count",
            0,
        )
    )

    print(
        "- Streaming parca sayisi: "
        f"{streaming_chunk_count}"
    )

    print(
        "- Cevap karakter sayisi: "
        f"{answer_character_count}"
    )


def answer_question(
    question,
    top_k=DEFAULT_TOP_K,
    min_similarity_score=(
        DEFAULT_MIN_SIMILARITY_SCORE
    ),
    on_token: Callable[[str], None] | None = None,
    embedder=None,
    generator=None,
    manage_embedder_lifecycle=None,
    manage_generator_lifecycle=None,
):
    """
    Kullanici sorusunu uctan uca local RAG
    pipeline'inda isler.

    Varsayilan kullanim stateless'tir:

    - Embedding modeli yuklenir
    - Retrieval yapilir
    - Embedding modeli kapatilir
    - Yeterli context varsa chat modeli yuklenir
    - Streaming cevap uretilir
    - Chat modeli kapatilir

    Disaridan embedder ve generator verilirse
    model nesneleri birden fazla soruda yeniden
    kullanilabilir.

    Generation asamasinda su metrikler olculur:

    - Ilk metin parcasina kadar gecen sure
    - Toplam generation suresi
    - Ilk parcadan sonraki streaming suresi
    - Streaming parca sayisi
    - Cevap karakter sayisi
    """
    cleaned_question = str(
        question
    ).strip()

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

    service_start = perf_counter()

    performance_metrics = (
        create_empty_performance_metrics()
    )

    generation_metrics = (
        create_empty_generation_metrics()
    )

    owns_embedder = embedder is None
    owns_generator = generator is None

    active_embedder = (
        LocalEmbedder()
        if owns_embedder
        else embedder
    )

    active_generator = (
        LocalGenerator()
        if owns_generator
        else generator
    )

    if manage_embedder_lifecycle is None:
        manage_embedder_lifecycle = (
            owns_embedder
        )

    if manage_generator_lifecycle is None:
        manage_generator_lifecycle = (
            owns_generator
        )

    retrieval_candidate_k = max(
        (
            top_k
            * DEFAULT_RETRIEVAL_CANDIDATE_MULTIPLIER
        ),
        top_k,
    )

    print(
        "RAG servisi: ilgili chunk'lar "
        "getiriliyor..."
    )

    retrieval_result = (
        retrieve_top_chunks_with_metrics(
            query=cleaned_question,
            top_k=retrieval_candidate_k,
            embedder=active_embedder,
            manage_embedder_lifecycle=(
                manage_embedder_lifecycle
            ),
        )
    )

    candidate_chunks = retrieval_result[
        "chunks"
    ]

    retrieval_timings = retrieval_result[
        "timings"
    ]

    for metric_name, metric_value in (
        retrieval_timings.items()
    ):
        performance_metrics[metric_name] = (
            float(metric_value)
        )

    embedding_model_reused = retrieval_result[
        "embedding_model_reused"
    ]

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

    source_rankings = []
    relevant_chunks = []
    ranked_primary_source = None
    primary_source = None

    if has_sufficient_context:
        source_ranking_start = (
            perf_counter()
        )

        source_rankings = (
            rank_candidate_sources(
                question=cleaned_question,
                candidate_chunks=(
                    candidate_chunks
                ),
            )
        )

        performance_metrics[
            "source_ranking_seconds"
        ] = (
            perf_counter()
            - source_ranking_start
        )

        ranked_primary_source = (
            source_rankings[0]["source"]
            if source_rankings
            else None
        )

        context_selection_start = (
            perf_counter()
        )

        relevant_chunks = (
            select_context_chunks_by_primary_source(
                question=cleaned_question,
                candidate_chunks=(
                    candidate_chunks
                ),
                context_top_k=top_k,
                source_rankings=(
                    source_rankings
                ),
            )
        )

        performance_metrics[
            "context_selection_seconds"
        ] = (
            perf_counter()
            - context_selection_start
        )

        primary_source = (
            ranked_primary_source
        )

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

    print(
        f"Ana kaynak: {primary_source}"
    )

    print(
        "Embedding modeli yeniden kullanildi: "
        f"{embedding_model_reused}"
    )

    if source_rankings:
        print(
            "Kaynak secim skorlari:"
        )

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
            "Yerel chat modeli kullanilmayacak."
        )

        if on_token is not None:
            on_token(
                FALLBACK_ANSWER
            )
            print()

        performance_metrics[
            "service_total_seconds"
        ] = (
            perf_counter()
            - service_start
        )

        print_performance_metrics(
            performance_metrics
        )

        return {
            "question": cleaned_question,
            "answer": FALLBACK_ANSWER,
            "status": "insufficient_context",
            "source_references": [],
            "retrieved_chunks": [],
            "candidate_chunks": (
                candidate_chunks
            ),
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
            "ranked_primary_source": None,
            "primary_source": None,
            "source_rankings": [],
            "performance_metrics": (
                performance_metrics
            ),
            "generation_metrics": (
                generation_metrics
            ),
            "embedding_model_reused": (
                embedding_model_reused
            ),
            "chat_model_used": False,
            "chat_model_reused": False,
            "embedder_lifecycle_managed": (
                manage_embedder_lifecycle
            ),
            "generator_lifecycle_managed": (
                manage_generator_lifecycle
            ),
        }

    print(
        "\nRAG servisi: context ve prompt'lar "
        "olusturuluyor..."
    )

    prompt_build_start = perf_counter()

    rag_prompt = build_rag_prompt(
        question=cleaned_question,
        retrieved_chunks=relevant_chunks,
    )

    performance_metrics[
        "prompt_build_seconds"
    ] = (
        perf_counter()
        - prompt_build_start
    )

    chat_model_reused = (
        active_generator.is_loaded
    )

    model_alias = (
        active_generator.model_alias
    )

    answer = ""

    try:
        if active_generator.is_loaded:
            print(
                "\nRAG servisi: yuklu chat modeli "
                "yeniden kullaniliyor..."
            )

        else:
            print(
                "\nRAG servisi: yerel chat modeli "
                "yukleniyor..."
            )

            chat_model_load_start = (
                perf_counter()
            )

            active_generator.load()

            performance_metrics[
                "chat_model_load_seconds"
            ] = (
                perf_counter()
                - chat_model_load_start
            )

        print(
            "\nRAG servisi: cevap uretiliyor..."
        )

        generation_result = (
            active_generator.generate_with_metrics(
                system_prompt=rag_prompt[
                    "system_prompt"
                ],
                user_prompt=rag_prompt[
                    "user_prompt"
                ],
                on_token=on_token,
            )
        )

        answer = generation_result[
            "answer"
        ]

        generation_metrics = (
            generation_result[
                "metrics"
            ]
        )

        performance_metrics[
            "time_to_first_token_seconds"
        ] = float(
            generation_metrics[
                "time_to_first_token_seconds"
            ]
        )

        performance_metrics[
            "generation_seconds"
        ] = float(
            generation_metrics[
                "generation_total_seconds"
            ]
        )

        performance_metrics[
            "streaming_seconds"
        ] = float(
            generation_metrics[
                "streaming_seconds"
            ]
        )

        performance_metrics[
            "streaming_chunk_count"
        ] = int(
            generation_metrics[
                "streaming_chunk_count"
            ]
        )

        performance_metrics[
            "answer_character_count"
        ] = int(
            generation_metrics[
                "answer_character_count"
            ]
        )

    finally:
        if on_token is not None:
            print()

        if manage_generator_lifecycle:
            chat_model_unload_start = (
                perf_counter()
            )

            active_generator.unload()

            performance_metrics[
                "chat_model_unload_seconds"
            ] = (
                perf_counter()
                - chat_model_unload_start
            )

    cleaned_answer = str(
        answer
    ).strip()

    performance_metrics[
        "service_total_seconds"
    ] = (
        perf_counter()
        - service_start
    )

    print(
        "Chat modeli yeniden kullanildi: "
        f"{chat_model_reused}"
    )

    print_performance_metrics(
        performance_metrics
    )

    return {
        "question": cleaned_question,
        "answer": cleaned_answer,
        "status": "answered",
        "source_references": rag_prompt[
            "source_references"
        ],
        "retrieved_chunks": (
            relevant_chunks
        ),
        "candidate_chunks": (
            candidate_chunks
        ),
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
        "primary_source": (
            primary_source
        ),
        "source_rankings": (
            source_rankings
        ),
        "performance_metrics": (
            performance_metrics
        ),
        "generation_metrics": (
            generation_metrics
        ),
        "embedding_model_reused": (
            embedding_model_reused
        ),
        "chat_model_used": True,
        "chat_model_reused": (
            chat_model_reused
        ),
        "embedder_lifecycle_managed": (
            manage_embedder_lifecycle
        ),
        "generator_lifecycle_managed": (
            manage_generator_lifecycle
        ),
    }