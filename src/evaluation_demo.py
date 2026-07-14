from src.evaluation import (
    evaluate_retrieval_cases,
    load_evaluation_cases,
    summarize_evaluation,
)
from src.retrieval import (
    DEFAULT_MIN_SIMILARITY_SCORE,
    retrieve_top_chunks,
)


DEFAULT_TOP_K = 3


def result_label(result):
    """
    Test sonucuna uygun terminal etiketi dondurur.
    """
    if result["passed"] is True:
        return "PASS"

    if result["passed"] is False:
        return "FAIL"

    return "INFO"


def print_case_result(result):
    """
    Tek bir retrieval degerlendirme sonucunu gosterir.
    """
    print("\n" + "-" * 70)
    print(f"[{result_label(result)}] {result['id']}")
    print(f"Kategori: {result['category']}")
    print(f"Soru: {result['question']}")
    print(f"Beklenen durum: {result['expected_status']}")
    print(f"Tahmin edilen durum: {result['predicted_status']}")

    if result["top_similarity_score"] is not None:
        print(
            "En yuksek skor: "
            f"{result['top_similarity_score']:.4f}"
        )

    print(f"En ust kaynak: {result['top_source']}")

    if result["acceptable_sources"]:
        print(
            "Kabul edilen kaynaklar: "
            + ", ".join(result["acceptable_sources"])
        )

    print("Top-k adaylari:")

    for rank, chunk in enumerate(
        result["candidate_chunks"],
        start=1,
    ):
        print(
            f"  {rank}. {chunk['source']} "
            f"| Chunk {chunk['chunk_index']} "
            f"| {chunk['similarity_score']:.4f}"
        )


def print_summary(summary):
    """
    Genel degerlendirme metriklerini terminalde gosterir.
    """
    print("\n" + "=" * 70)
    print("DEGERLENDIRME OZETI")
    print("=" * 70)
    print(f"Kesin test sayisi: {summary['total_cases']}")
    print(f"Basarili: {summary['passed_cases']}")
    print(f"Basarisiz: {summary['failed_cases']}")
    print(
        "Genel basari orani: "
        f"%{summary['overall_accuracy']:.2f}"
    )
    print(
        "Durum karari basarisi: "
        f"%{summary['status_accuracy']:.2f}"
    )
    print(
        "Ust kaynak basarisi: "
        f"%{summary['source_accuracy']:.2f}"
    )

    print("\nKarar matrisi:")
    print(
        "  Cevaplanabilir ve kabul edildi: "
        f"{summary['true_positive']}"
    )
    print(
        "  Cevaplanabilir ama reddedildi: "
        f"{summary['false_negative']}"
    )
    print(
        "  Cevaplanamaz ve reddedildi: "
        f"{summary['true_negative']}"
    )
    print(
        "  Cevaplanamaz ama kabul edildi: "
        f"{summary['false_positive']}"
    )

    print(
        "\nBasari oranina katilmayan sinir testleri: "
        f"{summary['diagnostic_cases']}"
    )


def run_input_validation_checks():
    """
    Bos soru ve gecersiz top_k kontrollerini dogrular.
    """
    print("\n" + "=" * 70)
    print("GIRDI DOGRULAMA TESTLERI")
    print("=" * 70)

    try:
        retrieve_top_chunks("   ")
    except ValueError:
        print("[PASS] Bos soru reddedildi.")
    else:
        print("[FAIL] Bos soru reddedilmedi.")

    try:
        retrieve_top_chunks("RAG nedir?", top_k=0)
    except ValueError:
        print("[PASS] Gecersiz top_k reddedildi.")
    else:
        print("[FAIL] Gecersiz top_k reddedilmedi.")


def main():
    print("Retrieval evaluation demo baslatiliyor.")
    print(
        "Minimum benzerlik esigi: "
        f"{DEFAULT_MIN_SIMILARITY_SCORE:.4f}"
    )
    print(f"Top-k: {DEFAULT_TOP_K}")

    cases = load_evaluation_cases()

    print(f"Yuklenen test vakasi sayisi: {len(cases)}")

    results = evaluate_retrieval_cases(
        cases=cases,
        top_k=DEFAULT_TOP_K,
        min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
    )

    for result in results:
        print_case_result(result)

    summary = summarize_evaluation(results)
    print_summary(summary)

    run_input_validation_checks()

    print("\nRetrieval evaluation demo tamamlandi.")


if __name__ == "__main__":
    main()