import json
from datetime import datetime, timezone
from pathlib import Path

from src.embedder import EMBEDDING_MODEL_ALIASES
from src.generator import CHAT_MODEL_ALIAS
from src.rag_service import (
    FALLBACK_ANSWER,
    answer_question,
)
from src.retrieval import DEFAULT_MIN_SIMILARITY_SCORE


BASE_DIR = Path(__file__).resolve().parents[1]

GENERATION_EVALUATION_PATH = (
    BASE_DIR / "data" / "generation_evaluation_questions.json"
)

GENERATION_REPORT_PATH = (
    BASE_DIR / "reports" / "generation_evaluation_report.json"
)

REPORT_SCHEMA_VERSION = 1
DEFAULT_TOP_K = 3

VALID_STATUSES = {
    "answered",
    "insufficient_context",
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


def normalize_text(text):
    """
    Metni anahtar kavram kontrolune uygun hale getirir.

    Turkce karakterleri sade karsiliklarina cevirir,
    kucuk harfe donusturur ve fazla bosluklari temizler.
    """
    normalized = str(text).translate(TURKISH_CHARACTER_MAP)
    normalized = normalized.lower()
    return " ".join(normalized.split())


def load_generation_evaluation_cases(
    file_path=GENERATION_EVALUATION_PATH,
):
    """
    Generation degerlendirme veri setini yukler ve dogrular.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Generation degerlendirme dosyasi bulunamadi: {path}"
        )

    cases = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(cases, list):
        raise ValueError(
            "Generation degerlendirme dosyasinin "
            "kok degeri liste olmalidir."
        )

    if not cases:
        raise ValueError(
            "Generation degerlendirme veri seti bos olamaz."
        )

    required_fields = {
        "id",
        "category",
        "question",
        "expected_status",
        "acceptable_sources",
        "required_concept_groups",
        "min_answer_chars",
        "max_answer_chars",
    }

    seen_ids = set()

    for position, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise TypeError(
                f"{position}. generation test vakasi sozluk degil."
            )

        missing_fields = required_fields - case.keys()

        if missing_fields:
            missing_text = ", ".join(sorted(missing_fields))

            raise ValueError(
                f"{position}. generation test vakasinda "
                f"eksik alanlar var: {missing_text}"
            )

        case_id = str(case["id"]).strip()

        if not case_id:
            raise ValueError(
                f"{position}. test vakasinin id degeri bos olamaz."
            )

        if case_id in seen_ids:
            raise ValueError(
                f"Tekrarlanan generation test id degeri: {case_id}"
            )

        seen_ids.add(case_id)

        if not str(case["question"]).strip():
            raise ValueError(
                f"{case_id} test vakasinin sorusu bos olamaz."
            )

        expected_status = case["expected_status"]

        if expected_status not in VALID_STATUSES:
            raise ValueError(
                f"{case_id} icin gecersiz expected_status: "
                f"{expected_status}"
            )

        if not isinstance(case["acceptable_sources"], list):
            raise TypeError(
                f"{case_id} acceptable_sources liste olmalidir."
            )

        concept_groups = case["required_concept_groups"]

        if not isinstance(concept_groups, list):
            raise TypeError(
                f"{case_id} required_concept_groups liste olmalidir."
            )

        for group_position, concept_group in enumerate(
            concept_groups,
            start=1,
        ):
            if not isinstance(concept_group, list):
                raise TypeError(
                    f"{case_id} icindeki {group_position}. "
                    "kavram grubu liste olmalidir."
                )

            if not concept_group:
                raise ValueError(
                    f"{case_id} icindeki {group_position}. "
                    "kavram grubu bos olamaz."
                )

        min_chars = case["min_answer_chars"]
        max_chars = case["max_answer_chars"]

        if not isinstance(min_chars, int) or min_chars < 0:
            raise ValueError(
                f"{case_id} min_answer_chars gecersiz."
            )

        if not isinstance(max_chars, int) or max_chars <= min_chars:
            raise ValueError(
                f"{case_id} max_answer_chars gecersiz."
            )

    return cases


def evaluate_concept_groups(answer, required_concept_groups):
    """
    Her kavram grubundan en az bir anahtar ifadenin
    cevapta bulunup bulunmadigini kontrol eder.

    Ornek:
        ["dokuman", "belge"]

    Bu gruptan en az bir kelime cevapta varsa grup basarili sayilir.
    """
    normalized_answer = normalize_text(answer)
    group_results = []

    for concept_group in required_concept_groups:
        normalized_keywords = [
            normalize_text(keyword)
            for keyword in concept_group
        ]

        matched_keywords = [
            keyword
            for keyword in normalized_keywords
            if keyword in normalized_answer
        ]

        group_results.append(
            {
                "keywords": concept_group,
                "matched": bool(matched_keywords),
                "matched_keywords": matched_keywords,
            }
        )

    all_groups_matched = all(
        group_result["matched"]
        for group_result in group_results
    )

    return {
        "all_groups_matched": all_groups_matched,
        "groups": group_results,
    }


def source_is_acceptable(
    source_references,
    acceptable_sources,
):
    """
    Gercek retrieval kaynaklarinda kabul edilen dokumanlardan
    en az birinin bulunup bulunmadigini kontrol eder.
    """
    if not acceptable_sources:
        return None

    return any(
        acceptable_source in source_reference
        for acceptable_source in acceptable_sources
        for source_reference in source_references
    )


def evaluate_generation_case(
    case,
    top_k=DEFAULT_TOP_K,
    min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
):
    """
    Tek bir soruyu gercek RAG servisiyle calistirir
    ve generation kalitesi kontrollerini uygular.
    """
    result = answer_question(
        question=case["question"],
        top_k=top_k,
        min_similarity_score=min_similarity_score,
        on_token=None,
    )

    answer = str(result["answer"]).strip()
    answer_length = len(answer)
    normalized_answer = normalize_text(answer)
    normalized_fallback_answer = normalize_text(FALLBACK_ANSWER)

    contains_fallback_answer = (
        normalized_fallback_answer in normalized_answer
)

    expected_status = case["expected_status"]
    status_correct = result["status"] == expected_status

    length_correct = (
        case["min_answer_chars"]
        <= answer_length
        <= case["max_answer_chars"]
    )

    concept_evaluation = evaluate_concept_groups(
        answer=answer,
        required_concept_groups=case[
            "required_concept_groups"
        ],
    )

    source_correct = source_is_acceptable(
        source_references=result["source_references"],
        acceptable_sources=case["acceptable_sources"],
    )

    if expected_status == "answered":
        model_usage_correct = result["model_alias"] is not None
        unexpected_fallback = contains_fallback_answer

        passed = bool(
            status_correct
            and answer
            and length_correct
            and concept_evaluation["all_groups_matched"]
            and source_correct
            and model_usage_correct
            and not unexpected_fallback
    )

        fallback_correct = None
        sources_empty = None    

    else:
        fallback_correct = (
            normalized_answer == normalized_fallback_answer
    )
        sources_empty = not result["source_references"]
        model_usage_correct = result["model_alias"] is None
        unexpected_fallback = None

        passed = bool(
            status_correct
            and fallback_correct
            and sources_empty
            and model_usage_correct
            and length_correct
        )

    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "expected_status": expected_status,
        "predicted_status": result["status"],
        "status_correct": status_correct,
        "answer": answer,
        "answer_length": answer_length,
        "min_answer_chars": case["min_answer_chars"],
        "max_answer_chars": case["max_answer_chars"],
        "length_correct": length_correct,
        "acceptable_sources": case["acceptable_sources"],
        "source_references": result["source_references"],
        "source_correct": source_correct,
        "concept_evaluation": concept_evaluation,
        "contains_fallback_answer": contains_fallback_answer,
        "unexpected_fallback": unexpected_fallback,
        "fallback_correct": fallback_correct,
        "sources_empty": sources_empty,
        "model_alias": result["model_alias"],
        "model_usage_correct": model_usage_correct,
        "top_similarity_score": result[
            "top_similarity_score"
        ],
        "min_similarity_score": result[
            "min_similarity_score"
        ],
        "passed": passed,
    }


def evaluate_generation_cases(
    cases,
    top_k=DEFAULT_TOP_K,
    min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
):
    """
    Tum generation test vakalarini sirayla calistirir.

    Bu islem birden fazla local LLM cevabi uretecegi icin
    retrieval degerlendirmesinden daha uzun surebilir.
    """
    results = []

    for index, case in enumerate(cases, start=1):
        print("\n" + "=" * 70)
        print(
            f"Generation vakasi calistiriliyor: "
            f"{index}/{len(cases)} | {case['id']}"
        )
        print("=" * 70)
        print(f"Soru: {case['question']}\n")

        case_result = evaluate_generation_case(
            case=case,
            top_k=top_k,
            min_similarity_score=min_similarity_score,
        )

        results.append(case_result)

    return results


def summarize_generation_evaluation(results):
    """
    Generation degerlendirme sonuclarindan temel metrikleri hesaplar.
    """
    total_cases = len(results)

    passed_cases = sum(
        result["passed"] is True
        for result in results
    )

    supported_results = [
        result
        for result in results
        if result["expected_status"] == "answered"
    ]

    unsupported_results = [
        result
        for result in results
        if result["expected_status"]
        == "insufficient_context"
    ]

    status_correct_cases = sum(
        result["status_correct"] is True
        for result in results
    )

    source_correct_cases = sum(
        result["source_correct"] is True
        for result in supported_results
    )

    concept_correct_cases = sum(
        result["concept_evaluation"]["all_groups_matched"]
        is True
        for result in supported_results
    )

    length_correct_cases = sum(
        result["length_correct"] is True
        for result in results
    )

    fallback_correct_cases = sum(
        result["fallback_correct"] is True
        for result in unsupported_results
    )


    clean_supported_cases = sum(
        result["unexpected_fallback"] is False
        for result in supported_results
    )

    overall_accuracy = (
        passed_cases / total_cases * 100
        if total_cases
        else 0.0
    )

    source_accuracy = (
        source_correct_cases / len(supported_results) * 100
        if supported_results
        else 0.0
    )

    concept_accuracy = (
        concept_correct_cases / len(supported_results) * 100
        if supported_results
        else 0.0
    )

    fallback_accuracy = (
        fallback_correct_cases
        / len(unsupported_results)
        * 100
        if unsupported_results
        else 0.0
    )

    average_answer_length = (
        sum(
            result["answer_length"]
            for result in results
        )
        / total_cases
        if total_cases
        else 0.0
    )

    return {
        "total_cases": total_cases,
        "supported_cases": len(supported_results),
        "unsupported_cases": len(unsupported_results),
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "overall_accuracy": overall_accuracy,
        "status_accuracy": (
            status_correct_cases / total_cases * 100
            if total_cases
            else 0.0
        ),
        "source_accuracy": source_accuracy,
        "concept_accuracy": concept_accuracy,
        "length_accuracy": (
            length_correct_cases / total_cases * 100
            if total_cases
            else 0.0
        ),
        "clean_answer_accuracy": (
            clean_supported_cases
            / len(supported_results)
            * 100
            if supported_results
            else 0.0
        ),
        "fallback_accuracy": fallback_accuracy,
        "average_answer_length": average_answer_length,
    }


def build_generation_report(
    results,
    summary,
    top_k=DEFAULT_TOP_K,
    min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
):
    """
    Generation sonuclarindan kalici JSON raporu olusturur.
    """
    failed_cases = [
        result
        for result in results
        if result["passed"] is False
    ]

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "configuration": {
            "embedding_model": EMBEDDING_MODEL_ALIASES[0],
            "chat_model": CHAT_MODEL_ALIAS,
            "top_k": top_k,
            "min_similarity_score": min_similarity_score,
        },
        "summary": summary,
        "failed_cases": failed_cases,
        "cases": results,
    }


def save_generation_report(
    report,
    file_path=GENERATION_REPORT_PATH,
):
    """
    Generation raporunu gecici dosya uzerinden guvenli kaydeder.
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


def load_generation_report(
    file_path=GENERATION_REPORT_PATH,
):
    """
    Daha once kaydedilen generation raporunu yukler.
    """
    report_path = Path(file_path)

    if not report_path.exists():
        return None

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    if not isinstance(report, dict):
        raise ValueError(
            "Generation raporunun kok degeri sozluk olmalidir."
        )

    return report