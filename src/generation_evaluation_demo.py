from src.generation_evaluation import (
    DEFAULT_TOP_K,
    GENERATION_REPORT_PATH,
    build_generation_report,
    evaluate_generation_cases,
    load_generation_evaluation_cases,
    load_generation_report,
    save_generation_report,
    summarize_generation_evaluation,
)
from src.retrieval import DEFAULT_MIN_SIMILARITY_SCORE


def result_label(result):
    """
    Vakanin sonucuna gore terminal etiketi dondurur.
    """
    return "PASS" if result["passed"] else "FAIL"


def print_case_result(result):
    """
    Tek bir generation sonucunu terminalde gosterir.
    """
    print("\n" + "-" * 70)
    print(f"[{result_label(result)}] {result['id']}")
    print(f"Soru: {result['question']}")
    print(f"Beklenen durum: {result['expected_status']}")
    print(f"Gerceklesen durum: {result['predicted_status']}")
    print(f"Durum dogru: {result['status_correct']}")
    print(f"Model: {result['model_alias']}")
    print(f"Cevap karakter sayisi: {result['answer_length']}")
    print(f"Uzunluk uygun: {result['length_correct']}")
    print(f"Kaynak dogru: {result['source_correct']}")
    print(
        "Beklenmeyen fallback: "
        f"{result['unexpected_fallback']}"
    )
    print(
        "Ana fikir gruplari uygun: "
        f"{result['concept_evaluation']['all_groups_matched']}"
    )

    print("\nCevap:")
    print(result["answer"])

    print("\nKaynaklar:")

    if result["source_references"]:
        for source_reference in result["source_references"]:
            print(f"- {source_reference}")
    else:
        print("- Kaynak kullanilmadi.")

    if result["concept_evaluation"]["groups"]:
        print("\nAna fikir kontrolleri:")

        for index, group in enumerate(
            result["concept_evaluation"]["groups"],
            start=1,
        ):
            print(
                f"  {index}. {group['keywords']} "
                f"| Eslesen: {group['matched_keywords']} "
                f"| Sonuc: {group['matched']}"
            )

    if result["fallback_correct"] is not None:
        print(
            "Fallback cevabi dogru: "
            f"{result['fallback_correct']}"
        )

    if result["sources_empty"] is not None:
        print(
            "Kaynak listesi bos: "
            f"{result['sources_empty']}"
        )

    print(
        "En yuksek retrieval skoru: "
        f"{result['top_similarity_score']}"
    )


def print_summary(summary):
    """
    Generation degerlendirme ozetini gosterir.
    """
    print("\n" + "=" * 70)
    print("GENERATION DEGERLENDIRME OZETI")
    print("=" * 70)
    print(f"Toplam vaka: {summary['total_cases']}")
    print(f"Desteklenen vaka: {summary['supported_cases']}")
    print(
        "Desteklenmeyen vaka: "
        f"{summary['unsupported_cases']}"
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
        "Kaynak basarisi: "
        f"%{summary['source_accuracy']:.2f}"
    )
    print(
        "Ana fikir basarisi: "
        f"%{summary['concept_accuracy']:.2f}"
    )
    print(
        "Cevap uzunlugu basarisi: "
        f"%{summary['length_accuracy']:.2f}"
    )
    print(
        "Temiz cevap basarisi: "
        f"%{summary['clean_answer_accuracy']:.2f}"
    )
    print(
        "Fallback basarisi: "
        f"%{summary['fallback_accuracy']:.2f}"
    )
    print(
        "Ortalama cevap uzunlugu: "
        f"{summary['average_answer_length']:.2f}"
    )


def main():
    print("Generation evaluation demo baslatiliyor.")
    print(f"Chat modeli: phi-4-mini")
    print(
        "Minimum benzerlik esigi: "
        f"{DEFAULT_MIN_SIMILARITY_SCORE:.4f}"
    )
    print(f"Top-k: {DEFAULT_TOP_K}")
    print(f"Rapor yolu: {GENERATION_REPORT_PATH}")

    previous_report = load_generation_report()

    if previous_report is None:
        print("Onceki generation raporu bulunamadi.")
    else:
        print(
            "Onceki generation raporu: "
            f"{previous_report.get('generated_at_utc')}"
        )

    cases = load_generation_evaluation_cases()

    print(f"Yuklenen generation vakasi: {len(cases)}")
    print(
        "\nNot: Cevaplanabilir her soru local chat modelini "
        "calistiracagi icin bu test biraz surebilir."
    )

    results = evaluate_generation_cases(
        cases=cases,
        top_k=DEFAULT_TOP_K,
        min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
    )

    for result in results:
        print_case_result(result)

    summary = summarize_generation_evaluation(results)

    report = build_generation_report(
        results=results,
        summary=summary,
        top_k=DEFAULT_TOP_K,
        min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
    )

    saved_path = save_generation_report(report)
    loaded_report = load_generation_report(saved_path)

    if loaded_report is None:
        raise RuntimeError(
            "Kaydedilen generation raporu okunamadi."
        )

    if len(loaded_report["cases"]) != len(cases):
        raise RuntimeError(
            "Kaydedilen generation vaka sayisi uyusmuyor."
        )

    print_summary(summary)

    print("\n" + "=" * 70)
    print("GENERATION RAPOR KAYIT SONUCU")
    print("=" * 70)
    print(f"Rapor kaydedildi: {saved_path}")
    print(
        "Rapor vaka sayisi: "
        f"{len(loaded_report['cases'])}"
    )
    print(
        "Rapor schema version: "
        f"{loaded_report['schema_version']}"
    )

    print("\nGeneration evaluation demo tamamlandi.")


if __name__ == "__main__":
    main()