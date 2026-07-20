import json
import statistics
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from src.rag_service import answer_question


BASE_DIR = Path(__file__).resolve().parents[1]

DEFAULT_PERFORMANCE_REPORT_PATH = (
    BASE_DIR
    / "reports"
    / "performance_report.json"
)

DEFAULT_REPEATS = 3

PERFORMANCE_CASES = [
    {
        "id": "supported_sqlite",
        "question": (
            "SQLite RAG sisteminde hangi bilgileri saklar?"
        ),
        "expected_status": "answered",
        "expected_source": "sqlite_notes.txt",
    },
    {
        "id": "supported_foundry_local",
        "question": "Foundry Local ne ise yarar?",
        "expected_status": "answered",
        "expected_source": "foundry_local_notes.txt",
    },
    {
        "id": "unsupported_jupiter",
        "question": "Jupiter'in kac uydusu vardir?",
        "expected_status": "insufficient_context",
        "expected_source": None,
    },
]

PERFORMANCE_METRIC_NAMES = [
    "database_read_seconds",
    "embedding_model_load_seconds",
    "query_embedding_seconds",
    "embedding_model_unload_seconds",
    "similarity_ranking_seconds",
    "retrieval_total_seconds",
    "source_ranking_seconds",
    "context_selection_seconds",
    "prompt_build_seconds",
    "chat_model_load_seconds",
    "generation_seconds",
    "chat_model_unload_seconds",
    "service_total_seconds",
]

SERVICE_STAGE_METRICS = [
    "retrieval_total_seconds",
    "source_ranking_seconds",
    "context_selection_seconds",
    "prompt_build_seconds",
    "chat_model_load_seconds",
    "generation_seconds",
    "chat_model_unload_seconds",
]

RETRIEVAL_STAGE_METRICS = [
    "database_read_seconds",
    "embedding_model_load_seconds",
    "query_embedding_seconds",
    "embedding_model_unload_seconds",
    "similarity_ranking_seconds",
]

METRIC_LABELS = {
    "database_read_seconds": "SQLite okuma",
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
    "retrieval_total_seconds": "Toplam retrieval",
    "source_ranking_seconds": (
        "Hibrit kaynak siralama"
    ),
    "context_selection_seconds": "Context secimi",
    "prompt_build_seconds": "Prompt hazirlama",
    "chat_model_load_seconds": (
        "Chat modeli yukleme"
    ),
    "generation_seconds": "Cevap uretme",
    "chat_model_unload_seconds": (
        "Chat modeli kapatma"
    ),
    "service_total_seconds": (
        "Toplam RAG servis suresi"
    ),
}


def validate_performance_cases(cases):
    """
    Performans test vakalarinin gerekli alanlara
    ve gecerli degerlere sahip oldugunu dogrular.
    """
    if not isinstance(cases, list):
        raise TypeError(
            "Performans vakalari bir liste olmalidir."
        )

    if not cases:
        raise ValueError(
            "Performans vaka listesi bos olamaz."
        )

    required_fields = {
        "id",
        "question",
        "expected_status",
        "expected_source",
    }

    valid_statuses = {
        "answered",
        "insufficient_context",
    }

    seen_ids = set()

    for position, case in enumerate(
        cases,
        start=1,
    ):
        if not isinstance(case, dict):
            raise TypeError(
                f"{position}. performans vakasi "
                "bir sozluk olmalidir."
            )

        missing_fields = (
            required_fields - case.keys()
        )

        if missing_fields:
            missing_text = ", ".join(
                sorted(missing_fields)
            )

            raise ValueError(
                f"{position}. performans vakasinda "
                f"eksik alanlar var: {missing_text}"
            )

        case_id = str(case["id"]).strip()
        question = str(case["question"]).strip()

        if not case_id:
            raise ValueError(
                f"{position}. performans vakasinin "
                "id degeri bos olamaz."
            )

        if case_id in seen_ids:
            raise ValueError(
                "Tekrarlanan performans vaka id'si: "
                f"{case_id}"
            )

        seen_ids.add(case_id)

        if not question:
            raise ValueError(
                f"{case_id} vakasinin sorusu "
                "bos olamaz."
            )

        if (
            case["expected_status"]
            not in valid_statuses
        ):
            raise ValueError(
                f"{case_id} icin gecersiz "
                "expected_status degeri."
            )


def normalize_metrics(performance_metrics):
    """
    RAG servisinden gelen performans metriklerini
    eksiksiz ve sayisal bir sozluge cevirir.
    """
    normalized_metrics = {}

    for metric_name in PERFORMANCE_METRIC_NAMES:
        value = performance_metrics.get(
            metric_name,
            0.0,
        )

        normalized_metrics[metric_name] = float(
            value
        )

    return normalized_metrics


def run_single_performance_case(
    case,
    repetition,
):
    """
    Tek bir performans vakasini calistirir.

    RAG servisinin ayrintili terminal ciktilari
    benchmark sirasinda gizlenir. Bir hata olursa
    yakalanan cikti hata ayiklama icin yazdirilir.
    """
    captured_output = StringIO()

    try:
        with redirect_stdout(captured_output):
            result = answer_question(
                case["question"]
            )
    except Exception:
        logged_text = captured_output.getvalue()

        if logged_text:
            print("\nYAKALANAN RAG SERVISI CIKTISI")
            print(logged_text)

        raise

    expected_status = case["expected_status"]
    expected_source = case["expected_source"]

    status_correct = (
        result["status"] == expected_status
    )

    if expected_status == "answered":
        source_correct = (
            result["primary_source"]
            == expected_source
        )
    else:
        source_correct = (
            result["primary_source"] is None
        )

    passed = bool(
        status_correct
        and source_correct
    )

    return {
        "case_id": case["id"],
        "repetition": repetition,
        "question": case["question"],
        "expected_status": expected_status,
        "actual_status": result["status"],
        "status_correct": status_correct,
        "expected_source": expected_source,
        "actual_source": result[
            "primary_source"
        ],
        "source_correct": source_correct,
        "passed": passed,
        "model_alias": result["model_alias"],
        "answer_length": len(result["answer"]),
        "top_similarity_score": result[
            "top_similarity_score"
        ],
        "performance_metrics": normalize_metrics(
            result["performance_metrics"]
        ),
    }


def summarize_numeric_values(values):
    """
    Bir sayi listesi icin ortalama, medyan,
    minimum ve maksimum degerleri hesaplar.
    """
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "minimum": 0.0,
            "maximum": 0.0,
        }

    numeric_values = [
        float(value)
        for value in values
    ]

    return {
        "count": len(numeric_values),
        "mean": statistics.fmean(
            numeric_values
        ),
        "median": statistics.median(
            numeric_values
        ),
        "minimum": min(numeric_values),
        "maximum": max(numeric_values),
    }


def summarize_metric_collection(runs):
    """
    Bir grup benchmark calismasindaki tum
    performans metriklerini ozetler.
    """
    metric_summary = {}

    for metric_name in PERFORMANCE_METRIC_NAMES:
        values = [
            run["performance_metrics"][
                metric_name
            ]
            for run in runs
        ]

        metric_summary[metric_name] = (
            summarize_numeric_values(values)
        )

    return metric_summary


def calculate_stage_breakdown(
    runs,
    stage_metrics,
    total_metric,
):
    """
    Asama medyanlarini ve toplam sure icindeki
    yaklasik yuzdelerini hesaplar.
    """
    if not runs:
        return []

    total_values = [
        run["performance_metrics"][
            total_metric
        ]
        for run in runs
    ]

    total_median = statistics.median(
        total_values
    )

    breakdown = []

    for metric_name in stage_metrics:
        metric_values = [
            run["performance_metrics"][
                metric_name
            ]
            for run in runs
        ]

        metric_median = statistics.median(
            metric_values
        )

        percentage = (
            metric_median
            / total_median
            * 100
            if total_median > 0
            else 0.0
        )

        breakdown.append(
            {
                "metric": metric_name,
                "label": METRIC_LABELS[
                    metric_name
                ],
                "median_seconds": (
                    metric_median
                ),
                "percentage_of_total": (
                    percentage
                ),
            }
        )

    breakdown.sort(
        key=lambda item: item[
            "median_seconds"
        ],
        reverse=True,
    )

    return breakdown


def summarize_case(case, case_runs):
    """
    Tek bir test vakasi icin doğruluk ve
    performans ozetini olusturur.
    """
    passed_runs = sum(
        run["passed"]
        for run in case_runs
    )

    return {
        "id": case["id"],
        "question": case["question"],
        "expected_status": case[
            "expected_status"
        ],
        "expected_source": case[
            "expected_source"
        ],
        "run_count": len(case_runs),
        "passed_runs": passed_runs,
        "failed_runs": (
            len(case_runs) - passed_runs
        ),
        "all_runs_passed": (
            passed_runs == len(case_runs)
        ),
        "metrics": summarize_metric_collection(
            case_runs
        ),
    }


def build_performance_summary(
    cases,
    runs,
):
    """
    Tum benchmark calismalari icin genel
    performans ve dogruluk ozetini olusturur.
    """
    answered_runs = [
        run
        for run in runs
        if run["actual_status"] == "answered"
    ]

    unsupported_runs = [
        run
        for run in runs
        if (
            run["actual_status"]
            == "insufficient_context"
        )
    ]

    passed_runs = sum(
        run["passed"]
        for run in runs
    )

    answered_total_summary = (
        summarize_numeric_values(
            [
                run["performance_metrics"][
                    "service_total_seconds"
                ]
                for run in answered_runs
            ]
        )
    )

    unsupported_total_summary = (
        summarize_numeric_values(
            [
                run["performance_metrics"][
                    "service_total_seconds"
                ]
                for run in unsupported_runs
            ]
        )
    )

    answered_median = (
        answered_total_summary["median"]
    )

    unsupported_median = (
        unsupported_total_summary["median"]
    )

    answered_to_unsupported_ratio = (
        answered_median / unsupported_median
        if unsupported_median > 0
        else None
    )

    service_breakdown = (
        calculate_stage_breakdown(
            runs=answered_runs,
            stage_metrics=SERVICE_STAGE_METRICS,
            total_metric="service_total_seconds",
        )
    )

    retrieval_breakdown = (
        calculate_stage_breakdown(
            runs=runs,
            stage_metrics=(
                RETRIEVAL_STAGE_METRICS
            ),
            total_metric="retrieval_total_seconds",
        )
    )

    return {
        "total_runs": len(runs),
        "passed_runs": passed_runs,
        "failed_runs": (
            len(runs) - passed_runs
        ),
        "correctness_rate": (
            passed_runs / len(runs) * 100
            if runs
            else 0.0
        ),
        "answered_run_count": len(
            answered_runs
        ),
        "unsupported_run_count": len(
            unsupported_runs
        ),
        "answered_total_seconds": (
            answered_total_summary
        ),
        "unsupported_total_seconds": (
            unsupported_total_summary
        ),
        "answered_to_unsupported_ratio": (
            answered_to_unsupported_ratio
        ),
        "answered_service_breakdown": (
            service_breakdown
        ),
        "retrieval_breakdown_all_runs": (
            retrieval_breakdown
        ),
        "primary_service_bottleneck": (
            service_breakdown[0]
            if service_breakdown
            else None
        ),
        "primary_retrieval_bottleneck": (
            retrieval_breakdown[0]
            if retrieval_breakdown
            else None
        ),
    }


def save_performance_report(
    report,
    file_path=DEFAULT_PERFORMANCE_REPORT_PATH,
):
    """
    Performans raporunu JSON dosyasina kaydeder.
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


def run_performance_benchmark(
    cases=None,
    repeats=DEFAULT_REPEATS,
    report_path=DEFAULT_PERFORMANCE_REPORT_PATH,
):
    """
    Performans vakalarini belirtilen tekrar
    sayisiyla calistirir ve kalici rapor uretir.
    """
    selected_cases = (
        PERFORMANCE_CASES
        if cases is None
        else cases
    )

    validate_performance_cases(
        selected_cases
    )

    if repeats <= 0:
        raise ValueError(
            "Tekrar sayisi sifirdan buyuk "
            "olmalidir."
        )

    runs = []
    total_runs = (
        len(selected_cases) * repeats
    )
    current_run = 0

    for repetition in range(
        1,
        repeats + 1,
    ):
        for case in selected_cases:
            current_run += 1

            print(
                f"Benchmark: {current_run}/"
                f"{total_runs} "
                f"| Tekrar: {repetition}/"
                f"{repeats} "
                f"| Vaka: {case['id']}"
            )

            run_result = (
                run_single_performance_case(
                    case=case,
                    repetition=repetition,
                )
            )

            runs.append(run_result)

            total_seconds = (
                run_result[
                    "performance_metrics"
                ][
                    "service_total_seconds"
                ]
            )

            print(
                f"  Durum: "
                f"{run_result['actual_status']} "
                f"| Gecti: "
                f"{run_result['passed']} "
                f"| Sure: "
                f"{total_seconds:.4f} saniye"
            )

    case_summaries = []

    for case in selected_cases:
        case_runs = [
            run
            for run in runs
            if run["case_id"] == case["id"]
        ]

        case_summaries.append(
            summarize_case(
                case=case,
                case_runs=case_runs,
            )
        )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "configuration": {
            "repeats": repeats,
            "case_count": len(
                selected_cases
            ),
            "expected_total_runs": (
                total_runs
            ),
        },
        "summary": build_performance_summary(
            cases=selected_cases,
            runs=runs,
        ),
        "cases": case_summaries,
        "runs": runs,
    }

    saved_path = save_performance_report(
        report=report,
        file_path=report_path,
    )

    return {
        "report": report,
        "report_path": saved_path,
    }


def load_performance_report(
    file_path=DEFAULT_PERFORMANCE_REPORT_PATH,
):
    """
    Daha once kaydedilen performans raporunu
    yukler.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            "Performans raporu bulunamadi: "
            f"{path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )