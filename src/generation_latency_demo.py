from src.generation_latency import (
    DEFAULT_REPEATS,
    GENERATION_LATENCY_REPORT_PATH,
    run_generation_latency_benchmark,
)


def print_duration_summary(
    label,
    summary,
):
    """
    Bir sure metriginin ozetini yazdirir.
    """
    print(label)

    print(
        "  Ortalama: "
        f"{summary['mean']:.4f} saniye"
    )

    print(
        "  Medyan: "
        f"{summary['median']:.4f} saniye"
    )

    print(
        "  Minimum: "
        f"{summary['minimum']:.4f} saniye"
    )

    print(
        "  Maksimum: "
        f"{summary['maximum']:.4f} saniye"
    )


def main():
    """
    Max-token generation benchmark'ini
    calistirir ve ozetini terminale yazdirir.
    """
    print(
        "Generation latency benchmark "
        "baslatiliyor."
    )

    print(
        "Tekrar sayisi: "
        f"{DEFAULT_REPEATS}"
    )

    print(
        "Rapor yolu: "
        f"{GENERATION_LATENCY_REPORT_PATH}"
    )

    benchmark_result = (
        run_generation_latency_benchmark()
    )

    report = benchmark_result["report"]

    print(
        "\n" + "=" * 70
    )

    print(
        "GENERATION LATENCY RAPOR OZETI"
    )

    print(
        "=" * 70
    )

    print(
        "Olculen toplam calisma: "
        f"{report['measured_run_count']}"
    )

    for configuration in report[
        "configuration_summaries"
    ]:
        print(
            "\n" + "-" * 70
        )

        print(
            "MAX TOKENS: "
            f"{configuration['max_tokens']}"
        )

        print(
            "Kalite sonucu: "
            f"{configuration['passed_runs']}/"
            f"{configuration['total_runs']}"
        )

        print(
            "Kalite orani: "
            f"%{configuration['quality_rate']:.2f}"
        )

        print()

        print_duration_summary(
            "Time to first token:",
            configuration[
                "time_to_first_token_seconds"
            ],
        )

        print()

        print_duration_summary(
            "Toplam generation:",
            configuration[
                "generation_total_seconds"
            ],
        )

        print()

        print_duration_summary(
            "Streaming:",
            configuration[
                "streaming_seconds"
            ],
        )

        character_summary = configuration[
            "answer_character_count"
        ]

        print(
            "\nCevap karakter sayisi medyani: "
            f"{character_summary['median']:.1f}"
        )

    fastest = report[
        "fastest_valid_configuration"
    ]

    print(
        "\n" + "=" * 70
    )

    print(
        "BENCHMARK ADAYI"
    )

    print(
        "=" * 70
    )

    if fastest is None:
        print(
            "Tum kalite kontrollerini gecen "
            "yapilandirma bulunamadi."
        )

    else:
        print(
            "En hizli gecerli max_tokens: "
            f"{fastest['max_tokens']}"
        )

        print(
            "Generation medyani: "
            f"{fastest['generation_total_seconds']['median']:.4f} "
            "saniye"
        )

        print(
            "TTFT medyani: "
            f"{fastest['time_to_first_token_seconds']['median']:.4f} "
            "saniye"
        )

        print(
            "Kalite orani: "
            f"%{fastest['quality_rate']:.2f}"
        )

        print(
            "\nBu yalnizca benchmark adayidir. "
            "Nihai varsayilan ayar generation "
            "regression testinden sonra secilecek."
        )

    print(
        "\nRapor kaydedildi: "
        f"{benchmark_result['report_path']}"
    )


if __name__ == "__main__":
    main()