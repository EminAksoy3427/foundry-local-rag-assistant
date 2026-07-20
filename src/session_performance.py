import json
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from src.performance import (
    PERFORMANCE_CASES,
    normalize_metrics,
    summarize_metric_collection,
    summarize_numeric_values,
)
from src.rag_session import LocalRAGSession


BASE_DIR = Path(__file__).resolve().parents[1]

BASELINE_REPORT_PATH = (
    BASE_DIR
    / "reports"
    / "performance_baseline.json"
)

OPTIMIZED_REPORT_PATH = (
    BASE_DIR
    / "reports"
    / "performance_optimized.json"
)

DEFAULT_SESSION_REPEATS = 3

WARMUP_CASE = {
    "id": "session_warmup",
    "question": (
        "SQLite RAG sisteminde hangi bilgileri saklar?"
    ),
    "expected_status": "answered",
    "expected_source": "sqlite_notes.txt",
}


def load_json_report(file_path):
    """
    Belirtilen JSON raporunu yukler.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Rapor bulunamadi: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def calculate_improvement(
    baseline_seconds,
    optimized_seconds,
):
    """
    Baseline ve optimize sureleri arasindaki
    hizlanma ve tasarruf oranini hesaplar.
    """
    if (
        baseline_seconds <= 0
        or optimized_seconds <= 0
    ):
        return {
            "baseline_seconds": baseline_seconds,
            "optimized_seconds": optimized_seconds,
            "saved_seconds": 0.0,
            "improvement_percentage": 0.0,
            "speedup_ratio": None,
        }

    saved_seconds = (
        baseline_seconds
        - optimized_seconds
    )

    improvement_percentage = (
        saved_seconds
        / baseline_seconds
        * 100
    )

    speedup_ratio = (
        baseline_seconds
        / optimized_seconds
    )

    return {
        "baseline_seconds": baseline_seconds,
        "optimized_seconds": optimized_seconds,
        "saved_seconds": saved_seconds,
        "improvement_percentage": (
            improvement_percentage
        ),
        "speedup_ratio": speedup_ratio,
    }


def run_session_case(
    session,
    case,
    repetition,
):
    """
    Tek bir performans vakasini kalici session
    uzerinden calistirir.
    """
    captured_output = StringIO()

    try:
        with redirect_stdout(captured_output):
            result = session.answer_question(
                case["question"]
            )
    except Exception:
        captured_text = (
            captured_output.getvalue()
        )

        if captured_text:
            print(
                "\nYAKALANAN SESSION CIKTISI"
            )
            print(captured_text)

        raise

    status_correct = (
        result["status"]
        == case["expected_status"]
    )

    if (
        case["expected_status"]
        == "answered"
    ):
        source_correct = (
            result["primary_source"]
            == case["expected_source"]
        )
    else:
        source_correct = (
            result["primary_source"] is None
        )

    return {
        "case_id": case["id"],
        "repetition": repetition,
        "question": case["question"],
        "expected_status": (
            case["expected_status"]
        ),
        "actual_status": result["status"],
        "status_correct": status_correct,
        "expected_source": (
            case["expected_source"]
        ),
        "actual_source": (
            result["primary_source"]
        ),
        "source_correct": source_correct,
        "passed": bool(
            status_correct
            and source_correct
        ),
        "model_alias": result["model_alias"],
        "embedding_model_reused": result[
            "embedding_model_reused"
        ],
        "chat_model_used": result[
            "chat_model_used"
        ],
        "chat_model_reused": result[
            "chat_model_reused"
        ],
        "answer_length": len(
            result["answer"]
        ),
        "performance_metrics": (
            normalize_metrics(
                result[
                    "performance_metrics"
                ]
            )
        ),
    }


def summarize_case_runs(
    case,
    case_runs,
):
    """
    Bir performans vakasi icin tekrarlarin
    ozetini olusturur.
    """
    passed_runs = sum(
        run["passed"]
        for run in case_runs
    )

    return {
        "id": case["id"],
        "question": case["question"],
        "expected_status": (
            case["expected_status"]
        ),
        "expected_source": (
            case["expected_source"]
        ),
        "run_count": len(case_runs),
        "passed_runs": passed_runs,
        "failed_runs": (
            len(case_runs)
            - passed_runs
        ),
        "all_runs_passed": (
            passed_runs
            == len(case_runs)
        ),
        "metrics": (
            summarize_metric_collection(
                case_runs
            )
        ),
    }


def save_optimized_report(
    report,
    file_path=OPTIMIZED_REPORT_PATH,
):
    """
    Optimize performans raporunu kaydeder.
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


def run_persistent_session_benchmark(
    repeats=DEFAULT_SESSION_REPEATS,
):
    """
    Kalici model session'inin warm performansini
    olcer ve stateless baseline ile karsilastirir.
    """
    if repeats <= 0:
        raise ValueError(
            "Tekrar sayisi sifirdan buyuk "
            "olmalidir."
        )

    baseline_report = load_json_report(
        BASELINE_REPORT_PATH
    )

    session = LocalRAGSession()

    runs = []
    startup_metrics = {}
    shutdown_metrics = {}
    warmup_result = None

    try:
        startup_metrics = session.start()

        print(
            "Chat modelini yuklemek icin "
            "warm-up vakasi calistiriliyor..."
        )

        warmup_result = run_session_case(
            session=session,
            case=WARMUP_CASE,
            repetition=0,
        )

        if not warmup_result["passed"]:
            raise RuntimeError(
                "Warm-up vakasi beklenen "
                "sonucu uretmedi."
            )

        total_runs = (
            len(PERFORMANCE_CASES)
            * repeats
        )

        current_run = 0

        for repetition in range(
            1,
            repeats + 1,
        ):
            for case in PERFORMANCE_CASES:
                current_run += 1

                print(
                    f"Persistent benchmark: "
                    f"{current_run}/{total_runs} "
                    f"| Tekrar: "
                    f"{repetition}/{repeats} "
                    f"| Vaka: {case['id']}"
                )

                run_result = run_session_case(
                    session=session,
                    case=case,
                    repetition=repetition,
                )

                runs.append(run_result)

                service_seconds = (
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
                    f"{service_seconds:.4f} saniye"
                )

    finally:
        shutdown_metrics = session.close()

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

    answered_summary = (
        summarize_numeric_values(
            [
                run["performance_metrics"][
                    "service_total_seconds"
                ]
                for run in answered_runs
            ]
        )
    )

    unsupported_summary = (
        summarize_numeric_values(
            [
                run["performance_metrics"][
                    "service_total_seconds"
                ]
                for run in unsupported_runs
            ]
        )
    )

    baseline_summary = baseline_report[
        "summary"
    ]

    baseline_answered_median = (
        baseline_summary[
            "answered_total_seconds"
        ][
            "median"
        ]
    )

    baseline_unsupported_median = (
        baseline_summary[
            "unsupported_total_seconds"
        ][
            "median"
        ]
    )

    answered_comparison = (
        calculate_improvement(
            baseline_seconds=(
                baseline_answered_median
            ),
            optimized_seconds=(
                answered_summary["median"]
            ),
        )
    )

    unsupported_comparison = (
        calculate_improvement(
            baseline_seconds=(
                baseline_unsupported_median
            ),
            optimized_seconds=(
                unsupported_summary["median"]
            ),
        )
    )

    case_summaries = []

    for case in PERFORMANCE_CASES:
        case_runs = [
            run
            for run in runs
            if run["case_id"] == case["id"]
        ]

        case_summaries.append(
            summarize_case_runs(
                case=case,
                case_runs=case_runs,
            )
        )

    passed_runs = sum(
        run["passed"]
        for run in runs
    )

    answered_reuse_correct = all(
        run["embedding_model_reused"]
        and run["chat_model_used"]
        and run["chat_model_reused"]
        for run in answered_runs
    )

    unsupported_reuse_correct = all(
        run["embedding_model_reused"]
        and not run["chat_model_used"]
        and not run["chat_model_reused"]
        for run in unsupported_runs
    )

    warmup_service_seconds = (
        warmup_result[
            "performance_metrics"
        ][
            "service_total_seconds"
        ]
    )

    first_user_total_seconds = (
        startup_metrics[
            "session_start_total_seconds"
        ]
        + warmup_service_seconds
    )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": "persistent_session",
        "configuration": {
            "repeats": repeats,
            "case_count": len(
                PERFORMANCE_CASES
            ),
            "total_benchmark_runs": len(
                runs
            ),
            "warmup_case": (
                WARMUP_CASE["id"]
            ),
        },
        "startup_metrics": (
            startup_metrics
        ),
        "warmup": {
            **warmup_result,
            "first_user_total_seconds": (
                first_user_total_seconds
            ),
        },
        "shutdown_metrics": (
            shutdown_metrics
        ),
        "summary": {
            "total_runs": len(runs),
            "passed_runs": passed_runs,
            "failed_runs": (
                len(runs) - passed_runs
            ),
            "correctness_rate": (
                passed_runs
                / len(runs)
                * 100
                if runs
                else 0.0
            ),
            "answered_total_seconds": (
                answered_summary
            ),
            "unsupported_total_seconds": (
                unsupported_summary
            ),
            "answered_comparison": (
                answered_comparison
            ),
            "unsupported_comparison": (
                unsupported_comparison
            ),
            "answered_model_reuse_correct": (
                answered_reuse_correct
            ),
            "unsupported_model_behavior_correct": (
                unsupported_reuse_correct
            ),
        },
        "cases": case_summaries,
        "runs": runs,
    }

    saved_path = save_optimized_report(
        report
    )

    return {
        "report": report,
        "report_path": saved_path,
    }