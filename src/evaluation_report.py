import json
from datetime import datetime, timezone
from pathlib import Path

from src.embedder import EMBEDDING_MODEL_ALIASES


BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "reports"
DEFAULT_REPORT_PATH = REPORTS_DIR / "evaluation_report.json"

REPORT_SCHEMA_VERSION = 1


def serialize_candidate_chunks(candidate_chunks):
    """
    Retrieval adaylarini JSON raporu icin sade bir yapida dondurur.

    Raporu gereksiz buyutmemek icin chunk metninin tamamini saklamaz.
    """
    serialized_chunks = []

    for chunk in candidate_chunks:
        serialized_chunks.append(
            {
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "similarity_score": round(
                    float(chunk["similarity_score"]),
                    6,
                ),
            }
        )

    return serialized_chunks


def serialize_case_result(result):
    """
    Tek bir degerlendirme sonucunu JSON uyumlu hale getirir.
    """
    top_similarity_score = result["top_similarity_score"]

    return {
        "id": result["id"],
        "category": result["category"],
        "question": result["question"],
        "expected_status": result["expected_status"],
        "predicted_status": result["predicted_status"],
        "status_correct": result["status_correct"],
        "acceptable_sources": result["acceptable_sources"],
        "top_source": result["top_source"],
        "source_correct": result["source_correct"],
        "top_similarity_score": (
            round(float(top_similarity_score), 6)
            if top_similarity_score is not None
            else None
        ),
        "include_in_accuracy": result["include_in_accuracy"],
        "passed": result["passed"],
        "candidate_chunks": serialize_candidate_chunks(
            result["candidate_chunks"]
        ),
    }


def calculate_score_analysis(results):
    """
    Desteklenen ve desteklenmeyen sorularin skor dagilimini ozetler.
    """
    supported_scores = [
        float(result["top_similarity_score"])
        for result in results
        if (
            result["include_in_accuracy"]
            and result["expected_status"] == "answered"
            and result["top_similarity_score"] is not None
        )
    ]

    unsupported_scores = [
        float(result["top_similarity_score"])
        for result in results
        if (
            result["include_in_accuracy"]
            and result["expected_status"]
            == "insufficient_context"
            and result["top_similarity_score"] is not None
        )
    ]

    lowest_supported_score = (
        min(supported_scores)
        if supported_scores
        else None
    )

    highest_unsupported_score = (
        max(unsupported_scores)
        if unsupported_scores
        else None
    )

    separation_margin = None

    if (
        lowest_supported_score is not None
        and highest_unsupported_score is not None
    ):
        separation_margin = (
            lowest_supported_score
            - highest_unsupported_score
        )

    return {
        "supported_case_count": len(supported_scores),
        "unsupported_case_count": len(unsupported_scores),
        "lowest_supported_score": (
            round(lowest_supported_score, 6)
            if lowest_supported_score is not None
            else None
        ),
        "highest_unsupported_score": (
            round(highest_unsupported_score, 6)
            if highest_unsupported_score is not None
            else None
        ),
        "separation_margin": (
            round(separation_margin, 6)
            if separation_margin is not None
            else None
        ),
    }


def build_evaluation_report(
    results,
    summary,
    top_k,
    min_similarity_score,
):
    """
    Degerlendirme sonuclarindan surumlenebilir JSON raporu olusturur.
    """
    if top_k <= 0:
        raise ValueError("top_k sifirdan buyuk olmalidir.")

    if not -1.0 <= min_similarity_score <= 1.0:
        raise ValueError(
            "Minimum benzerlik skoru -1.0 ile 1.0 arasinda olmalidir."
        )

    serialized_results = [
        serialize_case_result(result)
        for result in results
    ]

    failed_cases = [
        result
        for result in serialized_results
        if result["passed"] is False
    ]

    diagnostic_cases = [
        result
        for result in serialized_results
        if not result["include_in_accuracy"]
    ]

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "configuration": {
            "embedding_model": EMBEDDING_MODEL_ALIASES[0],
            "top_k": top_k,
            "min_similarity_score": min_similarity_score,
        },
        "dataset": {
            "total_cases": len(serialized_results),
            "strict_cases": summary["total_cases"],
            "diagnostic_cases": summary["diagnostic_cases"],
        },
        "summary": summary,
        "score_analysis": calculate_score_analysis(results),
        "failed_cases": failed_cases,
        "diagnostic_cases": diagnostic_cases,
        "cases": serialized_results,
    }


def save_evaluation_report(
    report,
    file_path=DEFAULT_REPORT_PATH,
):
    """
    Degerlendirme raporunu JSON dosyasina guvenli bicimde kaydeder.

    Once gecici dosyaya yazar, sonra asil rapor dosyasinin yerine koyar.
    """
    report_path = Path(file_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = report_path.with_suffix(
        report_path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(report_path)

    return report_path


def load_evaluation_report(
    file_path=DEFAULT_REPORT_PATH,
):
    """
    Daha once uretilen raporu yukler.

    Rapor yoksa None dondurur.
    """
    report_path = Path(file_path)

    if not report_path.exists():
        return None

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    if not isinstance(report, dict):
        raise ValueError(
            "Degerlendirme raporunun kok degeri sozluk olmalidir."
        )

    return report


def compare_report_summaries(previous_report, current_report):
    """
    Onceki ve yeni raporun temel metrik farklarini hesaplar.
    """
    if previous_report is None:
        return None

    previous_summary = previous_report.get("summary", {})
    current_summary = current_report.get("summary", {})

    metric_names = [
        "overall_accuracy",
        "status_accuracy",
        "source_accuracy",
        "false_positive",
        "false_negative",
    ]

    differences = {}

    for metric_name in metric_names:
        previous_value = previous_summary.get(metric_name)
        current_value = current_summary.get(metric_name)

        if previous_value is None or current_value is None:
            differences[metric_name] = None
            continue

        differences[metric_name] = (
            current_value - previous_value
        )

    return {
        "previous_generated_at_utc": previous_report.get(
            "generated_at_utc"
        ),
        "current_generated_at_utc": current_report.get(
            "generated_at_utc"
        ),
        "differences": differences,
    }