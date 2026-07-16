from src.evaluation import (
    evaluate_retrieval_cases,
    load_evaluation_cases,
    summarize_evaluation,
)
from src.evaluation_report import (
    DEFAULT_REPORT_PATH,
    build_evaluation_report,
    compare_report_summaries,
    load_evaluation_report,
    save_evaluation_report,
)
from src.retrieval import DEFAULT_MIN_SIMILARITY_SCORE


DEFAULT_TOP_K = 3


def print_summary(report):
    """
    Raporun temel metriklerini terminalde gosterir.
    """
    summary = report["summary"]
    score_analysis = report["score_analysis"]

    print("\n" + "=" * 70)
    print("DEGERLENDIRME RAPORU OZETI")
    print("=" * 70)
    print(f"Toplam vaka: {report['dataset']['total_cases']}")
    print(f"Kesin vaka: {report['dataset']['strict_cases']}")
    print(
        "Sinir vaka: "
        f"{report['dataset']['diagnostic_cases']}"
    )
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
    print(f"False positive: {summary['false_positive']}")
    print(f"False negative: {summary['false_negative']}")

    print("\nSkor analizi:")
    print(
        "  En dusuk desteklenen soru skoru: "
        f"{score_analysis['lowest_supported_score']}"
    )
    print(
        "  En yuksek desteklenmeyen soru skoru: "
        f"{score_analysis['highest_unsupported_score']}"
    )
    print(
        "  Skor ayrim marji: "
        f"{score_analysis['separation_margin']}"
    )


def print_failed_cases(report):
    """
    Basarisiz kesin test vakalarini gosterir.
    """
    print("\n" + "=" * 70)
    print("BASARISIZ VAKALAR")
    print("=" * 70)

    failed_cases = report["failed_cases"]

    if not failed_cases:
        print("Basarisiz kesin test vakasi yok.")
        return

    for case in failed_cases:
        print(
            f"- {case['id']} | "
            f"Beklenen: {case['expected_status']} | "
            f"Tahmin: {case['predicted_status']} | "
            f"Skor: {case['top_similarity_score']}"
        )


def print_comparison(comparison):
    """
    Onceki rapor ile yeni rapor arasindaki farklari gosterir.
    """
    print("\n" + "=" * 70)
    print("ONCEKI RAPORLA KARSILASTIRMA")
    print("=" * 70)

    if comparison is None:
        print(
            "Onceki rapor bulunamadi. "
            "Bu ilk kalici degerlendirme raporudur."
        )
        return

    print(
        "Onceki rapor tarihi: "
        f"{comparison['previous_generated_at_utc']}"
    )
    print(
        "Yeni rapor tarihi: "
        f"{comparison['current_generated_at_utc']}"
    )

    for metric_name, difference in comparison[
        "differences"
    ].items():
        print(f"{metric_name}: {difference}")


def main():
    print("Evaluation report demo baslatiliyor.")
    print(f"Rapor yolu: {DEFAULT_REPORT_PATH}")
    print(
        "Minimum benzerlik esigi: "
        f"{DEFAULT_MIN_SIMILARITY_SCORE:.4f}"
    )
    print(f"Top-k: {DEFAULT_TOP_K}")

    previous_report = load_evaluation_report()

    cases = load_evaluation_cases()

    print(f"Yuklenen test vakasi sayisi: {len(cases)}")

    results = evaluate_retrieval_cases(
        cases=cases,
        top_k=DEFAULT_TOP_K,
        min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
    )

    summary = summarize_evaluation(results)

    current_report = build_evaluation_report(
        results=results,
        summary=summary,
        top_k=DEFAULT_TOP_K,
        min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
    )

    comparison = compare_report_summaries(
        previous_report=previous_report,
        current_report=current_report,
    )

    saved_path = save_evaluation_report(current_report)

    loaded_report = load_evaluation_report(saved_path)

    if loaded_report is None:
        raise RuntimeError(
            "Kaydedilen degerlendirme raporu tekrar okunamadi."
        )

    if (
        loaded_report.get("schema_version")
        != current_report["schema_version"]
    ):
        raise RuntimeError(
            "Kaydedilen raporun schema_version degeri uyusmuyor."
        )

    print_summary(current_report)
    print_failed_cases(current_report)
    print_comparison(comparison)

    print("\n" + "=" * 70)
    print("RAPOR KAYIT SONUCU")
    print("=" * 70)
    print(f"Rapor kaydedildi: {saved_path}")
    print(
        "JSON vaka sayisi: "
        f"{len(loaded_report['cases'])}"
    )
    print(
        "Rapor schema version: "
        f"{loaded_report['schema_version']}"
    )

    print("\nEvaluation report demo tamamlandi.")


if __name__ == "__main__":
    main()