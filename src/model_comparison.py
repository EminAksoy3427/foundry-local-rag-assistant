import json
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from time import perf_counter

from src.embedder import LocalEmbedder
from src.generation_latency import (
    GENERATION_LATENCY_CASES,
    answer_ends_cleanly,
    evaluate_concept_groups,
    summarize_values,
)
from src.generator import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    LocalGenerator,
)
from src.rag_service import (
    FALLBACK_ANSWER,
    answer_question,
)


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_COMPARISON_REPORT_PATH = (
    BASE_DIR
    / "reports"
    / "model_comparison_report.json"
)

MODEL_ALIASES = [
    "phi-4-mini",
    "phi-3.5-mini",
    "qwen2.5-1.5b",
]

DEFAULT_REPEATS = 2

WARMUP_QUESTION = (
    "SQLite RAG sisteminde hangi bilgileri saklar?"
)

UNSUPPORTED_CASE = {
    "id": "model_unsupported_jupiter",
    "question": "Jupiter'in kac uydusu vardir?",
    "expected_status": "insufficient_context",
}


def create_failed_run(
    model_alias,
    case_id,
    question,
    repetition,
    error,
    expected_status,
    expected_source=None,
):
    """
    Model vakasi hata verdiginde rapora
    yazilacak standart sonucu olusturur.
    """
    return {
        "model_alias": model_alias,
        "case_id": case_id,
        "question": question,
        "repetition": repetition,
        "expected_status": expected_status,
        "actual_status": None,
        "expected_source": expected_source,
        "actual_source": None,
        "answer": None,
        "answer_length": 0,
        "passed": False,
        "error": (
            f"{type(error).__name__}: {error}"
        ),
        "checks": {},
        "generation_metrics": {
            "time_to_first_token_seconds": 0.0,
            "generation_total_seconds": 0.0,
            "streaming_seconds": 0.0,
            "streaming_chunk_count": 0,
            "answer_character_count": 0,
        },
        "service_total_seconds": 0.0,
    }


def run_supported_case(
    embedder,
    generator,
    model_alias,
    case,
    repetition,
):
    """
    Bir cevaplanabilir RAG vakasini calistirir
    ve kalite kontrollerini uygular.
    """
    captured_output = StringIO()

    try:
        with redirect_stdout(captured_output):
            result = answer_question(
                question=case["question"],
                embedder=embedder,
                generator=generator,
                manage_embedder_lifecycle=False,
                manage_generator_lifecycle=False,
            )

    except Exception as error:
        debug_output = captured_output.getvalue()

        if debug_output:
            print("\nYAKALANAN RAG CIKTISI")
            print(debug_output)

        return create_failed_run(
            model_alias=model_alias,
            case_id=case["id"],
            question=case["question"],
            repetition=repetition,
            error=error,
            expected_status="answered",
            expected_source=case[
                "expected_source"
            ],
        )

    answer = str(result["answer"]).strip()

    concept_result = evaluate_concept_groups(
        answer=answer,
        concept_groups=case[
            "required_concept_groups"
        ],
    )

    checks = {
        "status_correct": (
            result["status"] == "answered"
        ),
        "source_correct": (
            result["primary_source"]
            == case["expected_source"]
        ),
        "concepts_correct": (
            concept_result["passed"]
        ),
        "clean_ending": (
            answer_ends_cleanly(answer)
        ),
        "answer_length_valid": (
            40 <= len(answer) <= 600
        ),
        "fallback_not_used": (
            answer != FALLBACK_ANSWER
        ),
        "embedding_reused": (
            result["embedding_model_reused"]
        ),
        "chat_model_used": (
            result["chat_model_used"]
        ),
        "chat_model_reused": (
            result["chat_model_reused"]
        ),
        "model_alias_correct": (
            result["model_alias"]
            == model_alias
        ),
    }

    passed = all(checks.values())

    metrics = result["generation_metrics"]

    return {
        "model_alias": model_alias,
        "case_id": case["id"],
        "question": case["question"],
        "repetition": repetition,
        "expected_status": "answered",
        "actual_status": result["status"],
        "expected_source": (
            case["expected_source"]
        ),
        "actual_source": (
            result["primary_source"]
        ),
        "answer": answer,
        "answer_length": len(answer),
        "passed": passed,
        "error": None,
        "checks": checks,
        "concept_groups": (
            concept_result["groups"]
        ),
        "generation_metrics": {
            "time_to_first_token_seconds": float(
                metrics[
                    "time_to_first_token_seconds"
                ]
            ),
            "generation_total_seconds": float(
                metrics[
                    "generation_total_seconds"
                ]
            ),
            "streaming_seconds": float(
                metrics[
                    "streaming_seconds"
                ]
            ),
            "streaming_chunk_count": int(
                metrics[
                    "streaming_chunk_count"
                ]
            ),
            "answer_character_count": int(
                metrics[
                    "answer_character_count"
                ]
            ),
        },
        "service_total_seconds": float(
            result["performance_metrics"][
                "service_total_seconds"
            ]
        ),
    }


def run_unsupported_case(
    embedder,
    generator,
    model_alias,
    repetition,
):
    """
    Cevaplanamaz soruda retrieval guvenligi ve
    chat modelinin atlanmasini kontrol eder.
    """
    captured_output = StringIO()

    try:
        with redirect_stdout(captured_output):
            result = answer_question(
                question=UNSUPPORTED_CASE[
                    "question"
                ],
                embedder=embedder,
                generator=generator,
                manage_embedder_lifecycle=False,
                manage_generator_lifecycle=False,
            )

    except Exception as error:
        debug_output = captured_output.getvalue()

        if debug_output:
            print("\nYAKALANAN RAG CIKTISI")
            print(debug_output)

        return create_failed_run(
            model_alias=model_alias,
            case_id=UNSUPPORTED_CASE["id"],
            question=UNSUPPORTED_CASE[
                "question"
            ],
            repetition=repetition,
            error=error,
            expected_status=(
                "insufficient_context"
            ),
        )

    metrics = result["generation_metrics"]

    checks = {
        "status_correct": (
            result["status"]
            == "insufficient_context"
        ),
        "fallback_correct": (
            result["answer"]
            == FALLBACK_ANSWER
        ),
        "source_empty": (
            not result["source_references"]
            and result["primary_source"] is None
        ),
        "chat_model_not_used": (
            not result["chat_model_used"]
        ),
        "generation_skipped": (
            metrics[
                "generation_total_seconds"
            ]
            == 0.0
            and metrics[
                "time_to_first_token_seconds"
            ]
            == 0.0
        ),
        "embedding_reused": (
            result["embedding_model_reused"]
        ),
    }

    passed = all(checks.values())

    return {
        "model_alias": model_alias,
        "case_id": UNSUPPORTED_CASE["id"],
        "question": UNSUPPORTED_CASE[
            "question"
        ],
        "repetition": repetition,
        "expected_status": (
            "insufficient_context"
        ),
        "actual_status": result["status"],
        "expected_source": None,
        "actual_source": (
            result["primary_source"]
        ),
        "answer": result["answer"],
        "answer_length": len(
            result["answer"]
        ),
        "passed": passed,
        "error": None,
        "checks": checks,
        "generation_metrics": {
            "time_to_first_token_seconds": float(
                metrics[
                    "time_to_first_token_seconds"
                ]
            ),
            "generation_total_seconds": float(
                metrics[
                    "generation_total_seconds"
                ]
            ),
            "streaming_seconds": float(
                metrics[
                    "streaming_seconds"
                ]
            ),
            "streaming_chunk_count": int(
                metrics[
                    "streaming_chunk_count"
                ]
            ),
            "answer_character_count": int(
                metrics[
                    "answer_character_count"
                ]
            ),
        },
        "service_total_seconds": float(
            result["performance_metrics"][
                "service_total_seconds"
            ]
        ),
    }


def summarize_model(
    model_alias,
    runs,
    load_success,
    load_seconds,
    unload_success,
    unload_seconds,
    load_error=None,
):
    """
    Tek modelin kalite ve performans ozetini
    olusturur.
    """
    supported_runs = [
        run
        for run in runs
        if run["expected_status"] == "answered"
    ]

    unsupported_runs = [
        run
        for run in runs
        if (
            run["expected_status"]
            == "insufficient_context"
        )
    ]

    successful_supported_runs = [
        run
        for run in supported_runs
        if run["error"] is None
    ]

    total_runs = len(runs)

    passed_runs = sum(
        run["passed"]
        for run in runs
    )

    supported_passed_runs = sum(
        run["passed"]
        for run in supported_runs
    )

    unsupported_passed_runs = sum(
        run["passed"]
        for run in unsupported_runs
    )

    return {
        "model_alias": model_alias,
        "available": load_success,
        "load_success": load_success,
        "load_seconds": load_seconds,
        "load_error": load_error,
        "unload_success": unload_success,
        "unload_seconds": unload_seconds,
        "total_runs": total_runs,
        "passed_runs": passed_runs,
        "failed_runs": total_runs - passed_runs,
        "quality_rate": (
            passed_runs / total_runs * 100
            if total_runs
            else 0.0
        ),
        "all_quality_checks_passed": (
            load_success
            and total_runs > 0
            and passed_runs == total_runs
        ),
        "supported_runs": len(
            supported_runs
        ),
        "supported_passed_runs": (
            supported_passed_runs
        ),
        "unsupported_runs": len(
            unsupported_runs
        ),
        "unsupported_passed_runs": (
            unsupported_passed_runs
        ),
        "time_to_first_token_seconds": (
            summarize_values(
                [
                    run["generation_metrics"][
                        "time_to_first_token_seconds"
                    ]
                    for run in (
                        successful_supported_runs
                    )
                ]
            )
        ),
        "generation_total_seconds": (
            summarize_values(
                [
                    run["generation_metrics"][
                        "generation_total_seconds"
                    ]
                    for run in (
                        successful_supported_runs
                    )
                ]
            )
        ),
        "streaming_seconds": (
            summarize_values(
                [
                    run["generation_metrics"][
                        "streaming_seconds"
                    ]
                    for run in (
                        successful_supported_runs
                    )
                ]
            )
        ),
        "answer_character_count": (
            summarize_values(
                [
                    run["generation_metrics"][
                        "answer_character_count"
                    ]
                    for run in (
                        successful_supported_runs
                    )
                ]
            )
        ),
        "service_total_seconds": (
            summarize_values(
                [
                    run[
                        "service_total_seconds"
                    ]
                    for run in (
                        successful_supported_runs
                    )
                ]
            )
        ),
    }


def select_fastest_valid_model(
    model_summaries,
):
    """
    Tum kalite kontrollerini gecen modeller
    arasinda generation medyani en dusuk olani
    benchmark adayi olarak secer.
    """
    valid_models = [
        summary
        for summary in model_summaries
        if summary[
            "all_quality_checks_passed"
        ]
    ]

    if not valid_models:
        return None

    return min(
        valid_models,
        key=lambda summary: (
            summary[
                "generation_total_seconds"
            ]["median"]
        ),
    )


def save_model_comparison_report(
    report,
    file_path=MODEL_COMPARISON_REPORT_PATH,
):
    """
    Model karsilastirma raporunu JSON olarak
    kaydeder.
    """
    path = Path(file_path)

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


def run_model_comparison(
    repeats=DEFAULT_REPEATS,
):
    """
    Yerel chat modellerini ayni RAG vakalari,
    prompt, retrieval sonucu ve generation
    ayarlariyla karsilastirir.
    """
    if repeats <= 0:
        raise ValueError(
            "Tekrar sayisi sifirdan buyuk "
            "olmalidir."
        )

    embedder = LocalEmbedder()

    all_runs = []
    model_summaries = []

    embedding_load_start = perf_counter()

    embedder.load()

    embedding_load_seconds = (
        perf_counter()
        - embedding_load_start
    )

    try:
        for model_alias in MODEL_ALIASES:
            print("\n" + "=" * 70)
            print("MODEL KARSILASTIRMASI")
            print(f"Model: {model_alias}")
            print(
                f"Max tokens: "
                f"{DEFAULT_MAX_TOKENS}"
            )
            print(
                f"Temperature: "
                f"{DEFAULT_TEMPERATURE}"
            )
            print("=" * 70)

            generator = LocalGenerator(
                model_alias=model_alias,
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=(
                    DEFAULT_TEMPERATURE
                ),
            )

            model_runs = []
            load_success = False
            unload_success = False
            load_seconds = 0.0
            unload_seconds = 0.0
            load_error = None

            try:
                load_start = perf_counter()

                generator.load()

                load_seconds = (
                    perf_counter()
                    - load_start
                )

                load_success = True

                print(
                    "Model yukleme suresi: "
                    f"{load_seconds:.4f} saniye"
                )

                print(
                    "Model warm-up calismasi "
                    "yapiliyor..."
                )

                with redirect_stdout(StringIO()):
                    warmup_result = answer_question(
                        question=WARMUP_QUESTION,
                        embedder=embedder,
                        generator=generator,
                        manage_embedder_lifecycle=False,
                        manage_generator_lifecycle=False,
                    )

                if (
                    warmup_result["status"]
                    != "answered"
                ):
                    raise RuntimeError(
                        "Model warm-up sorusunu "
                        "cevaplayamadi."
                    )

                total_runs = (
                    (
                        len(
                            GENERATION_LATENCY_CASES
                        )
                        + 1
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
                            "Model benchmark: "
                            f"{current_run}/"
                            f"{total_runs} "
                            f"| model={model_alias} "
                            f"| vaka={case['id']} "
                            f"| tekrar="
                            f"{repetition}/{repeats}"
                        )

                        run_result = (
                            run_supported_case(
                                embedder=embedder,
                                generator=generator,
                                model_alias=(
                                    model_alias
                                ),
                                case=case,
                                repetition=(
                                    repetition
                                ),
                            )
                        )

                        model_runs.append(
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

                    current_run += 1

                    unsupported_result = (
                        run_unsupported_case(
                            embedder=embedder,
                            generator=generator,
                            model_alias=model_alias,
                            repetition=repetition,
                        )
                    )

                    model_runs.append(
                        unsupported_result
                    )
                    all_runs.append(
                        unsupported_result
                    )

                    print(
                        "Model benchmark: "
                        f"{current_run}/"
                        f"{total_runs} "
                        f"| model={model_alias} "
                        "| vaka="
                        f"{UNSUPPORTED_CASE['id']} "
                        f"| tekrar="
                        f"{repetition}/{repeats}"
                    )

                    print(
                        "  Gecti: "
                        f"{unsupported_result['passed']} "
                        "| Chat kullanildi: False"
                    )

            except Exception as error:
                load_error = (
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                print(
                    "\nMODEL CALISTIRMA HATASI: "
                    f"{load_error}"
                )

            finally:
                unload_start = perf_counter()

                try:
                    generator.unload()

                    unload_success = (
                        not generator.is_loaded
                    )

                except Exception as error:
                    unload_success = False

                    if load_error is None:
                        load_error = (
                            f"{type(error).__name__}: "
                            f"{error}"
                        )

                unload_seconds = (
                    perf_counter()
                    - unload_start
                )

            model_summaries.append(
                summarize_model(
                    model_alias=model_alias,
                    runs=model_runs,
                    load_success=load_success,
                    load_seconds=load_seconds,
                    unload_success=(
                        unload_success
                    ),
                    unload_seconds=(
                        unload_seconds
                    ),
                    load_error=load_error,
                )
            )

    finally:
        embedder.unload()

    fastest_valid_model = (
        select_fastest_valid_model(
            model_summaries
        )
    )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "benchmark_type": (
            "local_chat_model_comparison"
        ),
        "models": MODEL_ALIASES,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "temperature": DEFAULT_TEMPERATURE,
        "repeats": repeats,
        "supported_case_count": len(
            GENERATION_LATENCY_CASES
        ),
        "unsupported_case_count": 1,
        "measured_run_count": len(
            all_runs
        ),
        "embedding_model_load_seconds": (
            embedding_load_seconds
        ),
        "model_summaries": model_summaries,
        "fastest_valid_model": (
            fastest_valid_model
        ),
        "runs": all_runs,
        "selection_note": (
            "Only models that pass every quality "
            "and safety check are eligible for "
            "fastest-valid-model selection."
        ),
    }

    report_path = save_model_comparison_report(
        report
    )

    return {
        "report": report,
        "report_path": report_path,
    }