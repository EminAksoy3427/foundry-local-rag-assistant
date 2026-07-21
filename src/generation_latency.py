import json
import unicodedata
from contextlib import redirect_stdout
from datetime import datetime, timezone
from time import perf_counter
from io import StringIO
from pathlib import Path
from statistics import mean, median

from src.embedder import LocalEmbedder
from src.generator import (
    CHAT_MODEL_ALIAS,
    DEFAULT_TEMPERATURE,
    LocalGenerator,
)
from src.rag_service import answer_question


BASE_DIR = Path(__file__).resolve().parents[1]

GENERATION_LATENCY_REPORT_PATH = (
    BASE_DIR
    / "reports"
    / "generation_latency_report.json"
)

MAX_TOKEN_CONFIGURATIONS = [
    120,
    160,
    220,
]

DEFAULT_REPEATS = 2

WARMUP_QUESTION = (
    "SQLite RAG sisteminde hangi bilgileri saklar?"
)

GENERATION_LATENCY_CASES = [
    {
        "id": "latency_rag",
        "question": (
            "RAG cevaplari nasil daha guvenilir "
            "hale getirir?"
        ),
        "expected_source": "rag_notes.txt",
        "required_concept_groups": [
            [
                "dokuman",
                "belge",
            ],
            [
                "baglam",
                "context",
                "destek",
                "dayan",
            ],
        ],
    },
    {
        "id": "latency_foundry_local",
        "question": (
            "Foundry Local ne ise yarar?"
        ),
        "expected_source": (
            "foundry_local_notes.txt"
        ),
        "required_concept_groups": [
            [
                "model",
                "yapay zeka",
            ],
            [
                "cihaz",
                "yerel",
                "local",
            ],
        ],
    },
    {
        "id": "latency_sqlite",
        "question": (
            "SQLite neden yerel bir RAG "
            "uygulamasi icin uygundur?"
        ),
        "expected_source": "sqlite_notes.txt",
        "required_concept_groups": [
            [
                "sqlite",
            ],
            [
                "yerel",
                "local",
            ],
            [
                "dosya",
                "sunucu",
                "serverless",
                "hafif",
            ],
        ],
    },
    {
        "id": "latency_project",
        "question": (
            "Bu projenin temel amaci nedir?"
        ),
        "expected_source": (
            "project_overview.txt"
        ),
        "required_concept_groups": [
            [
                "yerel",
                "local",
            ],
            [
                "dokuman",
                "belge",
            ],
            [
                "asistan",
                "soru-cevap",
                "soru",
                "cevap",
            ],
        ],
    },
]


def normalize_text(value):
    """
    Metni kucuk harfe ve ASCII benzeri bir
    bicime donusturur.

    Kalite kontrolundeki Turkce karakter
    farkliliklarinin eslesmeyi bozmamasini
    saglar.
    """
    text = str(value).casefold()

    translation_table = str.maketrans(
        {
            "ı": "i",
            "ç": "c",
            "ğ": "g",
            "ö": "o",
            "ş": "s",
            "ü": "u",
        }
    )

    text = text.translate(
        translation_table
    )

    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )


def evaluate_concept_groups(
    answer,
    concept_groups,
):
    """
    Her kavram grubundan en az bir kelimenin
    cevapta bulunup bulunmadigini kontrol eder.
    """
    normalized_answer = normalize_text(
        answer
    )

    group_results = []

    for concept_group in concept_groups:
        matched_terms = []

        for term in concept_group:
            normalized_term = normalize_text(
                term
            )

            if normalized_term in normalized_answer:
                matched_terms.append(
                    term
                )

        group_results.append(
            {
                "terms": concept_group,
                "matched_terms": (
                    matched_terms
                ),
                "passed": bool(
                    matched_terms
                ),
            }
        )

    return {
        "passed": all(
            group["passed"]
            for group in group_results
        ),
        "groups": group_results,
    }


def answer_ends_cleanly(answer):
    """
    Cevabin bariz bicimde yarida kesilmis
    gorunup gorunmedigine dair basit bir
    sezgisel kontrol yapar.

    Bu kesin token-limit tespiti degildir.
    """
    cleaned_answer = str(
        answer
    ).strip()

    if not cleaned_answer:
        return False

    return cleaned_answer.endswith(
        (
            ".",
            "!",
            "?",
            "…",
        )
    )


def summarize_values(values):
    """
    Sayisal degerler icin temel istatistikleri
    hesaplar.
    """
    numeric_values = [
        float(value)
        for value in values
    ]

    if not numeric_values:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "minimum": 0.0,
            "maximum": 0.0,
        }

    return {
        "count": len(
            numeric_values
        ),
        "mean": mean(
            numeric_values
        ),
        "median": median(
            numeric_values
        ),
        "minimum": min(
            numeric_values
        ),
        "maximum": max(
            numeric_values
        ),
    }


def run_latency_case(
    embedder,
    generator,
    case,
    max_tokens,
    repetition,
):
    """
    Tek bir generation latency vakasini
    calistirir ve kalite kontrollerini yapar.
    """
    captured_output = StringIO()

    try:
        with redirect_stdout(
            captured_output
        ):
            result = answer_question(
                question=case["question"],
                embedder=embedder,
                generator=generator,
                manage_embedder_lifecycle=False,
                manage_generator_lifecycle=False,
            )

    except Exception:
        debug_output = (
            captured_output.getvalue()
        )

        if debug_output:
            print(
                "\nYAKALANAN RAG CIKTISI"
            )
            print(
                debug_output
            )

        raise

    answer = result["answer"]

    concept_result = (
        evaluate_concept_groups(
            answer=answer,
            concept_groups=case[
                "required_concept_groups"
            ],
        )
    )

    status_correct = (
        result["status"] == "answered"
    )

    source_correct = (
        result["primary_source"]
        == case["expected_source"]
    )

    fallback_not_used = (
        result["status"]
        != "insufficient_context"
    )

    clean_ending = answer_ends_cleanly(
        answer
    )

    answer_length_valid = (
        40
        <= len(answer)
        <= 600
    )

    chat_reuse_correct = (
        result["chat_model_used"]
        and result["chat_model_reused"]
    )

    embedding_reuse_correct = (
        result["embedding_model_reused"]
    )

    passed = all(
        [
            status_correct,
            source_correct,
            fallback_not_used,
            concept_result["passed"],
            clean_ending,
            answer_length_valid,
            chat_reuse_correct,
            embedding_reuse_correct,
        ]
    )

    generation_metrics = result[
        "generation_metrics"
    ]

    performance_metrics = result[
        "performance_metrics"
    ]

    return {
        "case_id": case["id"],
        "repetition": repetition,
        "max_tokens": max_tokens,
        "question": case["question"],
        "expected_source": (
            case["expected_source"]
        ),
        "actual_source": (
            result["primary_source"]
        ),
        "answer": answer,
        "answer_length": len(
            answer
        ),
        "status_correct": (
            status_correct
        ),
        "source_correct": (
            source_correct
        ),
        "fallback_not_used": (
            fallback_not_used
        ),
        "concepts_correct": (
            concept_result["passed"]
        ),
        "concept_groups": (
            concept_result["groups"]
        ),
        "clean_ending": clean_ending,
        "answer_length_valid": (
            answer_length_valid
        ),
        "chat_reuse_correct": (
            chat_reuse_correct
        ),
        "embedding_reuse_correct": (
            embedding_reuse_correct
        ),
        "passed": passed,
        "generation_metrics": {
            "time_to_first_token_seconds": float(
                generation_metrics[
                    "time_to_first_token_seconds"
                ]
            ),
            "generation_total_seconds": float(
                generation_metrics[
                    "generation_total_seconds"
                ]
            ),
            "streaming_seconds": float(
                generation_metrics[
                    "streaming_seconds"
                ]
            ),
            "streaming_chunk_count": int(
                generation_metrics[
                    "streaming_chunk_count"
                ]
            ),
            "answer_character_count": int(
                generation_metrics[
                    "answer_character_count"
                ]
            ),
        },
        "service_total_seconds": float(
            performance_metrics[
                "service_total_seconds"
            ]
        ),
    }


def summarize_configuration(
    max_tokens,
    runs,
):
    """
    Tek bir max-token yapilandirmasinin
    performans ve kalite ozetini olusturur.
    """
    passed_runs = sum(
        run["passed"]
        for run in runs
    )

    total_runs = len(
        runs
    )

    return {
        "max_tokens": max_tokens,
        "total_runs": total_runs,
        "passed_runs": passed_runs,
        "failed_runs": (
            total_runs
            - passed_runs
        ),
        "quality_rate": (
            passed_runs
            / total_runs
            * 100
            if total_runs
            else 0.0
        ),
        "all_quality_checks_passed": (
            passed_runs
            == total_runs
        ),
        "time_to_first_token_seconds": (
            summarize_values(
                [
                    run[
                        "generation_metrics"
                    ][
                        "time_to_first_token_seconds"
                    ]
                    for run in runs
                ]
            )
        ),
        "generation_total_seconds": (
            summarize_values(
                [
                    run[
                        "generation_metrics"
                    ][
                        "generation_total_seconds"
                    ]
                    for run in runs
                ]
            )
        ),
        "streaming_seconds": (
            summarize_values(
                [
                    run[
                        "generation_metrics"
                    ][
                        "streaming_seconds"
                    ]
                    for run in runs
                ]
            )
        ),
        "streaming_chunk_count": (
            summarize_values(
                [
                    run[
                        "generation_metrics"
                    ][
                        "streaming_chunk_count"
                    ]
                    for run in runs
                ]
            )
        ),
        "answer_character_count": (
            summarize_values(
                [
                    run[
                        "generation_metrics"
                    ][
                        "answer_character_count"
                    ]
                    for run in runs
                ]
            )
        ),
        "service_total_seconds": (
            summarize_values(
                [
                    run[
                        "service_total_seconds"
                    ]
                    for run in runs
                ]
            )
        ),
    }


def select_fastest_valid_configuration(
    configuration_summaries,
):
    """
    Tum kalite kontrollerini gecen yapilandirmalar
    arasinda generation medyani en dusuk olani
    benchmark adayi olarak secer.

    Bu secim nihai varsayilan ayar degildir.
    """
    valid_configurations = [
        configuration
        for configuration in (
            configuration_summaries
        )
        if configuration[
            "all_quality_checks_passed"
        ]
    ]

    if not valid_configurations:
        return None

    return min(
        valid_configurations,
        key=lambda configuration: (
            configuration[
                "generation_total_seconds"
            ][
                "median"
            ]
        ),
    )


def save_generation_latency_report(
    report,
    file_path=(
        GENERATION_LATENCY_REPORT_PATH
    ),
):
    """
    Generation latency raporunu JSON olarak
    kaydeder.
    """
    path = Path(
        file_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


def run_generation_latency_benchmark(
    repeats=DEFAULT_REPEATS,
):
    """
    Max-token yapilandirmalarini ayni model,
    ayni sorular ve kalici embedding modeliyle
    karsilastirir.
    """
    if repeats <= 0:
        raise ValueError(
            "Tekrar sayisi sifirdan buyuk "
            "olmalidir."
        )

    embedder = LocalEmbedder()

    all_runs = []
    configuration_summaries = []
    model_load_metrics = {}

    try:
        print(
            "Kalici embedding modeli "
            "yukleniyor..."
        )

        embedding_load_start = perf_counter()

        embedder.load()

        embedding_load_seconds = (
            perf_counter()
            - embedding_load_start
)

        for max_tokens in (
            MAX_TOKEN_CONFIGURATIONS
        ):
            print(
                "\n" + "=" * 70
            )

            print(
                "YAPILANDIRMA BASLATILIYOR"
            )

            print(
                f"Model: {CHAT_MODEL_ALIAS}"
            )

            print(
                f"Max tokens: {max_tokens}"
            )

            print(
                "=" * 70
            )

            generator = LocalGenerator(
                model_alias=CHAT_MODEL_ALIAS,
                max_tokens=max_tokens,
                temperature=(
                    DEFAULT_TEMPERATURE
                ),
            )

            load_start = datetime.now(
                timezone.utc
            )

            generator.load()

            load_end = datetime.now(
                timezone.utc
            )

            model_load_metrics[
                str(max_tokens)
            ] = {
                "chat_model_load_seconds": (
                    load_end
                    - load_start
                ).total_seconds()
            }

            try:
                print(
                    "Chat modeli warm-up "
                    "calismasi yapiliyor..."
                )

                with redirect_stdout(
                    StringIO()
                ):
                    warmup_result = (
                        answer_question(
                            question=(
                                WARMUP_QUESTION
                            ),
                            embedder=embedder,
                            generator=generator,
                            manage_embedder_lifecycle=False,
                            manage_generator_lifecycle=False,
                        )
                    )

                if (
                    warmup_result["status"]
                    != "answered"
                ):
                    raise RuntimeError(
                        "Warm-up sorusu "
                        "cevaplanamadi."
                    )

                configuration_runs = []

                total_configuration_runs = (
                    len(
                        GENERATION_LATENCY_CASES
                    )
                    * repeats
                )

                current_run = 0

                for repetition in range(
                    1,
                    repeats + 1,
                ):
                    for case in (
                        GENERATION_LATENCY_CASES
                    ):
                        current_run += 1

                        print(
                            "Generation benchmark: "
                            f"{current_run}/"
                            f"{total_configuration_runs} "
                            f"| max_tokens="
                            f"{max_tokens} "
                            f"| vaka={case['id']} "
                            f"| tekrar="
                            f"{repetition}/{repeats}"
                        )

                        run_result = (
                            run_latency_case(
                                embedder=embedder,
                                generator=generator,
                                case=case,
                                max_tokens=(
                                    max_tokens
                                ),
                                repetition=(
                                    repetition
                                ),
                            )
                        )

                        configuration_runs.append(
                            run_result
                        )

                        all_runs.append(
                            run_result
                        )

                        generation_seconds = (
                            run_result[
                                "generation_metrics"
                            ][
                                "generation_total_seconds"
                            ]
                        )

                        ttft_seconds = (
                            run_result[
                                "generation_metrics"
                            ][
                                "time_to_first_token_seconds"
                            ]
                        )

                        print(
                            "  Gecti: "
                            f"{run_result['passed']} "
                            "| TTFT: "
                            f"{ttft_seconds:.4f} sn "
                            "| Generation: "
                            f"{generation_seconds:.4f} sn "
                            "| Karakter: "
                            f"{run_result['answer_length']}"
                        )

                configuration_summaries.append(
                    summarize_configuration(
                        max_tokens=max_tokens,
                        runs=configuration_runs,
                    )
                )

            finally:
                generator.unload()

    finally:
        embedder.unload()

    fastest_valid_configuration = (
        select_fastest_valid_configuration(
            configuration_summaries
        )
    )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "benchmark_type": (
            "generation_max_tokens"
        ),
        "model_alias": CHAT_MODEL_ALIAS,
        "temperature": (
            DEFAULT_TEMPERATURE
        ),
        "max_token_configurations": (
            MAX_TOKEN_CONFIGURATIONS
        ),
        "repeats": repeats,
        "case_count": len(
            GENERATION_LATENCY_CASES
        ),
        "measured_run_count": len(
            all_runs
        ),
        "embedding_model_load_seconds": (
            embedding_load_seconds
        ),
        "chat_model_load_metrics": (
            model_load_metrics
        ),
        "configuration_summaries": (
            configuration_summaries
        ),
        "fastest_valid_configuration": (
            fastest_valid_configuration
        ),
        "runs": all_runs,
        "measurement_note": (
            "Time to first token represents the "
            "first non-empty streaming text chunk "
            "returned by the Foundry Local SDK, "
            "not necessarily one tokenizer token."
        ),
        "truncation_note": (
            "Clean answer ending is a heuristic "
            "and does not prove whether the model "
            "reached its token limit."
        ),
    }

    report_path = (
        save_generation_latency_report(
            report
        )
    )

    return {
        "report": report,
        "report_path": report_path,
    }