from src.session_performance import (
    DEFAULT_SESSION_REPEATS,
    OPTIMIZED_REPORT_PATH,
    run_persistent_session_benchmark,
)


def print_time_summary(
    label,
    summary,
):
    """
    Sure ozetini terminale yazdirir.
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


def print_comparison(
    label,
    comparison,
):
    """
    Baseline ve optimize sonucu karsilastirir.
    """
    print(label)

    print(
        "  Baseline medyan: "
        f"{comparison['baseline_seconds']:.4f} saniye"
    )

    print(
        "  Optimize medyan: "
        f"{comparison['optimized_seconds']:.4f} saniye"
    )

    print(
        "  Kazanilan sure: "
        f"{comparison['saved_seconds']:.4f} saniye"
    )

    print(
        "  Iyilesme: "
        f"%{comparison['improvement_percentage']:.2f}"
    )

    speedup_ratio = comparison[
        "speedup_ratio"
    ]

    if speedup_ratio is not None:
        print(
            "  Hizlanma orani: "
            f"{speedup_ratio:.2f}x"
        )


def main():
    """
    Kalici RAG session performans benchmark'ini
    calistirir.
    """
    print(
        "Persistent session benchmark "
        "baslatiliyor."
    )

    print(
        "Tekrar sayisi: "
        f"{DEFAULT_SESSION_REPEATS}"
    )

    print(
        "Rapor yolu: "
        f"{OPTIMIZED_REPORT_PATH}"
    )

    benchmark_result = (
        run_persistent_session_benchmark()
    )

    report = benchmark_result["report"]
    summary = report["summary"]

    print("\n" + "=" * 70)
    print("PERSISTENT SESSION RAPOR OZETI")
    print("=" * 70)

    print(
        f"Toplam calisma: "
        f"{summary['total_runs']}"
    )

    print(
        f"Basarili: "
        f"{summary['passed_runs']}"
    )

    print(
        f"Basarisiz: "
        f"{summary['failed_runs']}"
    )

    print(
        "Dogru davranis orani: "
        f"%{summary['correctness_rate']:.2f}"
    )

    print()

    print_time_summary(
        "Warm cevaplanabilir sorular:",
        summary[
            "answered_total_seconds"
        ],
    )

    print()

    print_time_summary(
        "Warm cevaplanamaz sorular:",
        summary[
            "unsupported_total_seconds"
        ],
    )

    print("\n" + "=" * 70)
    print("BASELINE KARSILASTIRMASI")
    print("=" * 70)

    print_comparison(
        "Cevaplanabilir sorular:",
        summary["answered_comparison"],
    )

    print()

    print_comparison(
        "Cevaplanamaz sorular:",
        summary["unsupported_comparison"],
    )

    print("\n" + "=" * 70)
    print("MODEL YENIDEN KULLANIM KONTROLU")
    print("=" * 70)

    print(
        "Cevaplanabilir vakalar: "
        f"{summary['answered_model_reuse_correct']}"
    )

    print(
        "Cevaplanamaz vakalar: "
        f"{summary['unsupported_model_behavior_correct']}"
    )

    print("\n" + "=" * 70)
    print("ILK KULLANICI DENEYIMI")
    print("=" * 70)

    print(
        "Session startup: "
        f"{report['startup_metrics']['session_start_total_seconds']:.4f} "
        "saniye"
    )

    print(
        "Ilk cevap servis suresi: "
        f"{report['warmup']['performance_metrics']['service_total_seconds']:.4f} "
        "saniye"
    )

    print(
        "Startup + ilk cevap: "
        f"{report['warmup']['first_user_total_seconds']:.4f} "
        "saniye"
    )

    print("\n" + "=" * 70)
    print("VAKA BAZLI WARM MEDYANLAR")
    print("=" * 70)

    for case in report["cases"]:
        median_seconds = case[
            "metrics"
        ][
            "service_total_seconds"
        ][
            "median"
        ]

        print(
            f"- {case['id']}: "
            f"{median_seconds:.4f} saniye "
            f"| Gecen: "
            f"{case['passed_runs']}/"
            f"{case['run_count']}"
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

    print(
        "\nPersistent session benchmark "
        "tamamlandi."
    )


if __name__ == "__main__":
    main()