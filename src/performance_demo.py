from src.performance import (
    DEFAULT_PERFORMANCE_REPORT_PATH,
    DEFAULT_REPEATS,
    PERFORMANCE_CASES,
    run_performance_benchmark,
)


def print_seconds_summary(label, summary):
    """
    Bir sure ozetini okunabilir bicimde yazdirir.
    """
    print(label)
    print(
        f"  Ortalama: "
        f"{summary['mean']:.4f} saniye"
    )
    print(
        f"  Medyan: "
        f"{summary['median']:.4f} saniye"
    )
    print(
        f"  Minimum: "
        f"{summary['minimum']:.4f} saniye"
    )
    print(
        f"  Maksimum: "
        f"{summary['maximum']:.4f} saniye"
    )


def print_breakdown(title, breakdown):
    """
    Darbogaz siralamasini terminale yazdirir.
    """
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    for index, item in enumerate(
        breakdown,
        start=1,
    ):
        print(
            f"{index}. {item['label']}: "
            f"{item['median_seconds']:.4f} saniye "
            f"| %{item['percentage_of_total']:.2f}"
        )


def main():
    """
    Tekrarlanabilir yerel RAG performans
    benchmark'ini calistirir.
    """
    print("Performance benchmark baslatiliyor.")
    print(
        f"Vaka sayisi: "
        f"{len(PERFORMANCE_CASES)}"
    )
    print(
        f"Her vaka icin tekrar: "
        f"{DEFAULT_REPEATS}"
    )
    print(
        "Toplam calisma sayisi: "
        f"{len(PERFORMANCE_CASES) * DEFAULT_REPEATS}"
    )
    print(
        f"Rapor yolu: "
        f"{DEFAULT_PERFORMANCE_REPORT_PATH}"
    )

    print(
        "\nNot: Cevaplanabilir vakalar yerel chat "
        "modelini yukleyip cevap uretecegi icin "
        "benchmark birkac dakika surebilir.\n"
    )

    benchmark_result = (
        run_performance_benchmark()
    )

    report = benchmark_result["report"]
    summary = report["summary"]

    print("\n" + "=" * 70)
    print("PERFORMANS RAPORU OZETI")
    print("=" * 70)

    print(
        f"Toplam calisma: "
        f"{summary['total_runs']}"
    )
    print(
        f"Basarili calisma: "
        f"{summary['passed_runs']}"
    )
    print(
        f"Basarisiz calisma: "
        f"{summary['failed_runs']}"
    )
    print(
        f"Dogru davranis orani: "
        f"%{summary['correctness_rate']:.2f}"
    )

    print()

    print_seconds_summary(
        "Cevaplanabilir sorular:",
        summary["answered_total_seconds"],
    )

    print()

    print_seconds_summary(
        "Cevaplanamaz sorular:",
        summary["unsupported_total_seconds"],
    )

    ratio = summary[
        "answered_to_unsupported_ratio"
    ]

    if ratio is not None:
        print(
            "\nCevaplanabilir / cevaplanamaz "
            f"sure orani: {ratio:.2f}x"
        )

    print_breakdown(
        title=(
            "CEVAPLANABILIR SORULARDA "
            "SERVIS DARBogAZ SIRALAMASI"
        ),
        breakdown=summary[
            "answered_service_breakdown"
        ],
    )

    print_breakdown(
        title=(
            "TUM CALISMALARDA RETRIEVAL "
            "DARBogAZ SIRALAMASI"
        ),
        breakdown=summary[
            "retrieval_breakdown_all_runs"
        ],
    )

    print("\n" + "=" * 70)
    print("VAKA BAZLI MEDYAN SURELER")
    print("=" * 70)

    for case_summary in report["cases"]:
        service_summary = case_summary[
            "metrics"
        ][
            "service_total_seconds"
        ]

        print(
            f"- {case_summary['id']}: "
            f"{service_summary['median']:.4f} saniye "
            f"| Gecen: "
            f"{case_summary['passed_runs']}/"
            f"{case_summary['run_count']}"
        )

    primary_service_bottleneck = summary[
        "primary_service_bottleneck"
    ]

    primary_retrieval_bottleneck = summary[
        "primary_retrieval_bottleneck"
    ]

    print("\n" + "=" * 70)
    print("TESPIT EDILEN ANA DARBogAZLAR")
    print("=" * 70)

    if primary_service_bottleneck:
        print(
            "Servis seviyesi: "
            f"{primary_service_bottleneck['label']} "
            f"({primary_service_bottleneck['median_seconds']:.4f} saniye)"
        )

    if primary_retrieval_bottleneck:
        print(
            "Retrieval seviyesi: "
            f"{primary_retrieval_bottleneck['label']} "
            f"({primary_retrieval_bottleneck['median_seconds']:.4f} saniye)"
        )

    print("\n" + "=" * 70)
    print("RAPOR KAYIT SONUCU")
    print("=" * 70)

    print(
        "Rapor kaydedildi: "
        f"{benchmark_result['report_path']}"
    )
    print(
        "Rapor schema version: "
        f"{report['schema_version']}"
    )

    print("\nPerformance benchmark tamamlandi.")


if __name__ == "__main__":
    main()