import json
from pathlib import Path

from src.db import fetch_all_documents
from src.embedder import LocalEmbedder
from src.retrieval import (
    DEFAULT_MIN_SIMILARITY_SCORE,
    rank_documents,
)


BASE_DIR = Path(__file__).resolve().parents[1]
EVALUATION_PATH = BASE_DIR / "data" / "evaluation_questions.json"

VALID_EXPECTED_STATUSES = {
    "answered",
    "insufficient_context",
}


def load_evaluation_cases(file_path=EVALUATION_PATH):
    """
    JSON dosyasindaki retrieval test vakalarini yukler
    ve temel alanlari dogrular.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Degerlendirme dosyasi bulunamadi: {file_path}"
        )

    raw_text = file_path.read_text(encoding="utf-8")
    cases = json.loads(raw_text)

    if not isinstance(cases, list):
        raise ValueError(
            "Degerlendirme dosyasinin kok degeri bir liste olmalidir."
        )

    if not cases:
        raise ValueError("Degerlendirme veri seti bos olamaz.")

    required_fields = {
        "id",
        "category",
        "question",
        "expected_status",
        "acceptable_sources",
        "include_in_accuracy",
    }

    seen_ids = set()

    for position, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise TypeError(
                f"{position}. test vakasi bir sozluk degil."
            )

        missing_fields = required_fields - case.keys()

        if missing_fields:
            missing_text = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"{position}. test vakasinda eksik alanlar var: "
                f"{missing_text}"
            )

        case_id = str(case["id"]).strip()

        if not case_id:
            raise ValueError(
                f"{position}. test vakasinin id degeri bos olamaz."
            )

        if case_id in seen_ids:
            raise ValueError(
                f"Tekrarlanan test vakasi id degeri: {case_id}"
            )

        seen_ids.add(case_id)

        if not str(case["question"]).strip():
            raise ValueError(
                f"{case_id} test vakasinin sorusu bos olamaz."
            )

        expected_status = case["expected_status"]

        if (
            expected_status is not None
            and expected_status not in VALID_EXPECTED_STATUSES
        ):
            raise ValueError(
                f"{case_id} icin gecersiz expected_status: "
                f"{expected_status}"
            )

        if not isinstance(case["acceptable_sources"], list):
            raise TypeError(
                f"{case_id} acceptable_sources alani liste olmalidir."
            )

        if not isinstance(case["include_in_accuracy"], bool):
            raise TypeError(
                f"{case_id} include_in_accuracy alani boolean olmalidir."
            )

    return cases


def evaluate_retrieval_cases(
    cases,
    top_k=3,
    min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
):
    """
    Test sorularini tek embedding model oturumunda degerlendirir.

    Bu fonksiyon chat modelini calistirmaz. Yalnizca retrieval,
    kaynak siralamasi ve esik kararini olcer.
    """
    if top_k <= 0:
        raise ValueError("top_k sifirdan buyuk olmalidir.")

    if not -1.0 <= min_similarity_score <= 1.0:
        raise ValueError(
            "Minimum benzerlik skoru -1.0 ile 1.0 arasinda olmalidir."
        )

    stored_documents = fetch_all_documents()

    if not stored_documents:
        raise ValueError(
            "SQLite veritabaninda degerlendirilecek dokuman bulunamadi."
        )

    results = []
    embedder = LocalEmbedder()

    try:
        print("Degerlendirme embedding modeli yukleniyor...")
        embedder.load()

        for index, case in enumerate(cases, start=1):
            question = str(case["question"]).strip()

            print(
                f"\nSoru degerlendiriliyor: {index}/{len(cases)} "
                f"| {case['id']}"
            )

            query_embedding = embedder.embed_text(question)

            ranked_documents = rank_documents(
                query_embedding=query_embedding,
                stored_documents=stored_documents,
            )

            candidate_chunks = ranked_documents[:top_k]

            top_similarity_score = (
                candidate_chunks[0]["similarity_score"]
                if candidate_chunks
                else None
            )

            top_source = (
                candidate_chunks[0]["source"]
                if candidate_chunks
                else None
            )

            predicted_status = (
                "answered"
                if (
                    top_similarity_score is not None
                    and top_similarity_score
                    >= min_similarity_score
                )
                else "insufficient_context"
            )

            expected_status = case["expected_status"]
            acceptable_sources = set(case["acceptable_sources"])

            status_correct = (
                None
                if expected_status is None
                else predicted_status == expected_status
            )

            if expected_status == "answered":
                source_correct = top_source in acceptable_sources
            elif expected_status == "insufficient_context":
                source_correct = None
            else:
                source_correct = (
                    top_source in acceptable_sources
                    if acceptable_sources
                    else None
                )

            include_in_accuracy = case["include_in_accuracy"]

            if include_in_accuracy:
                passed = bool(
                    status_correct
                    and (
                        source_correct
                        if expected_status == "answered"
                        else True
                    )
                )
            else:
                passed = None

            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "question": question,
                    "expected_status": expected_status,
                    "predicted_status": predicted_status,
                    "status_correct": status_correct,
                    "acceptable_sources": list(
                        case["acceptable_sources"]
                    ),
                    "top_source": top_source,
                    "source_correct": source_correct,
                    "top_similarity_score": top_similarity_score,
                    "candidate_chunks": candidate_chunks,
                    "include_in_accuracy": include_in_accuracy,
                    "passed": passed,
                }
            )

    finally:
        embedder.unload()

    return results


def summarize_evaluation(results):
    """
    Degerlendirme sonuclarindan temel basari metriklerini hesaplar.
    """
    strict_results = [
        result
        for result in results
        if result["include_in_accuracy"]
    ]

    total_cases = len(strict_results)

    passed_cases = sum(
        result["passed"] is True
        for result in strict_results
    )

    status_correct_cases = sum(
        result["status_correct"] is True
        for result in strict_results
    )

    supported_results = [
        result
        for result in strict_results
        if result["expected_status"] == "answered"
    ]

    source_correct_cases = sum(
        result["source_correct"] is True
        for result in supported_results
    )

    true_positive = sum(
        result["expected_status"] == "answered"
        and result["predicted_status"] == "answered"
        for result in strict_results
    )

    false_negative = sum(
        result["expected_status"] == "answered"
        and result["predicted_status"] == "insufficient_context"
        for result in strict_results
    )

    true_negative = sum(
        result["expected_status"] == "insufficient_context"
        and result["predicted_status"] == "insufficient_context"
        for result in strict_results
    )

    false_positive = sum(
        result["expected_status"] == "insufficient_context"
        and result["predicted_status"] == "answered"
        for result in strict_results
    )

    overall_accuracy = (
        passed_cases / total_cases * 100
        if total_cases
        else 0.0
    )

    status_accuracy = (
        status_correct_cases / total_cases * 100
        if total_cases
        else 0.0
    )

    source_accuracy = (
        source_correct_cases / len(supported_results) * 100
        if supported_results
        else 0.0
    )

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "overall_accuracy": overall_accuracy,
        "status_accuracy": status_accuracy,
        "source_accuracy": source_accuracy,
        "true_positive": true_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "diagnostic_cases": sum(
            not result["include_in_accuracy"]
            for result in results
        ),
    }