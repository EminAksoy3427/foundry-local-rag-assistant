from src.model_comparison import (
    DEFAULT_REPEATS,
    MODEL_COMPARISON_REPORT_PATH,
    run_model_comparison,
)


def print_duration_summary(
    label,
    summary,
):
    """
    Bir sure metriginin ozetini terminale
    yazdirir.
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


def print_model_summary(
    model_summary,
):
    """
    Tek bir modelin kalite, guvenlik ve
    performans ozetini yazdirir.
    """
    print("\n" + "-" * 70)

    print(
        "MODEL: "
        f"{model_summary['model_alias']}"
    )

    print(
        "Kullanilabilir: "
        f"{model_summary['available']}"
    )

    print(
        "Model yukleme: "
        f"{model_summary['load_success']}"
    )

    print(
        "Model kapatma: "
        f"{model_summary['unload_success']}"
    )

    print(
        "Yukleme suresi: "
        f"{model_summary['load_seconds']:.4f} saniye"
    )

    print(
        "Kapatma suresi: "
        f"{model_summary['unload_seconds']:.4f} saniye"
    )

    if model_summary["load_error"]:
        print(
            "Model hatasi: "
            f"{model_summary['load_error']}"
        )

    print(
        "Toplam vaka: "
        f"{model_summary['total_runs']}"
    )

    print(
        "Basarili vaka: "
        f"{model_summary['passed_runs']}"
    )

    print(
        "Basarisiz vaka: "
        f"{model_summary['failed_runs']}"
    )

    print(
        "Kalite orani: "
        f"%{model_summary['quality_rate']:.2f}"
    )

    print(
        "Tum kontroller gecti: "
        f"{model_summary['all_quality_checks_passed']}"
    )

    print(
        "Cevaplanabilir vakalar: "
        f"{model_summary['supported_passed_runs']}/"
        f"{model_summary['supported_runs']}"
    )

    print(
        "Cevaplanamaz vakalar: "
        f"{model_summary['unsupported_passed_runs']}/"
        f"{model_summary['unsupported_runs']}"
    )

    if (
        model_summary[
            "time_to_first_token_seconds"
        ]["count"]
        > 0
    ):
        print()

        print_duration_summary(
            "Time to first token:",
            model_summary[
                "time_to_first_token_seconds"
            ],
        )

        print()

        print_duration_summary(
            "Toplam generation:",
            model_summary[
                "generation_total_seconds"
            ],
        )

        print()

        print_duration_summary(
            "Toplam servis:",
            model_summary[
                "service_total_seconds"
            ],
        )

        answer_summary = model_summary[
            "answer_character_count"
        ]

        print(
            "\nCevap karakter sayisi medyani: "
            f"{answer_summary['median']:.1f}"
        )


def print_failed_runs(report):
    """
    Kalite veya teknik kontrolden gecemeyen
    model vakalarini terminale yazdirir.
    """
    failed_runs = [
        run
        for run in report["runs"]
        if not run["passed"]
    ]

    print("\n" + "=" * 70)
    print("BASARISIZ MODEL VAKALARI")
    print("=" * 70)

    if not failed_runs:
        print(
            "Basarisiz model vakasi yok."
        )
        return

    for run in failed_runs:
        print("\n" + "-" * 70)

        print(
            "Model: "
            f"{run['model_alias']}"
        )

        print(
            "Vaka: "
            f"{run['case_id']}"
        )

        print(
            "Tekrar: "
            f"{run['repetition']}"
        )

        print(
            "Beklenen durum: "
            f"{run['expected_status']}"
        )

        print(
            "Gerceklesen durum: "
            f"{run['actual_status']}"
        )

        print(
            "Beklenen kaynak: "
            f"{run['expected_source']}"
        )

        print(
            "Gerceklesen kaynak: "
            f"{run['actual_source']}"
        )

        if run["error"]:
            print(
                "Hata: "
                f"{run['error']}"
            )

        checks = run.get(
            "checks",
            {},
        )

        if checks:
            print("Kontroller:")

            for check_name, check_result in (
                checks.items()
            ):
                print(
                    f"  {check_name}: "
                    f"{check_result}"
                )

        if run["answer"]:
            print("Cevap:")
            print(
                run["answer"]
            )


def main():
    """
    Yerel chat modeli karsilastirma
    benchmark'ini calistirir.
    """
    print(
        "Yerel chat modeli karsilastirma "
        "benchmark'i baslatiliyor."
    )

    print(
        "Tekrar sayisi: "
        f"{DEFAULT_REPEATS}"
    )

    print(
        "Rapor yolu: "
        f"{MODEL_COMPARISON_REPORT_PATH}"
    )

    benchmark_result = (
        run_model_comparison()
    )

    report = benchmark_result["report"]

    print("\n" + "=" * 70)
    print("MODEL KARSILASTIRMA RAPOR OZETI")
    print("=" * 70)

    print(
        "Karsilastirilan model sayisi: "
        f"{len(report['models'])}"
    )

    print(
        "Olculen toplam vaka: "
        f"{report['measured_run_count']}"
    )

    print(
        "Max tokens: "
        f"{report['max_tokens']}"
    )

    print(
        "Temperature: "
        f"{report['temperature']}"
    )

    print(
        "Embedding modeli yukleme suresi: "
        f"{report['embedding_model_load_seconds']:.4f} "
        "saniye"
    )

    for model_summary in report[
        "model_summaries"
    ]:
        print_model_summary(
            model_summary
        )

    fastest_model = report[
        "fastest_valid_model"
    ]

    print("\n" + "=" * 70)
    print("EN HIZLI GECERLI MODEL")
    print("=" * 70)

    if fastest_model is None:
        print(
            "Tum kalite ve guvenlik "
            "kontrollerini gecen model "
            "bulunamadi."
        )

    else:
        print(
            "Model: "
            f"{fastest_model['model_alias']}"
        )

        print(
            "Kalite orani: "
            f"%{fastest_model['quality_rate']:.2f}"
        )

        print(
            "TTFT medyani: "
            f"{fastest_model[
                'time_to_first_token_seconds'
            ]['median']:.4f} saniye"
        )

        print(
            "Generation medyani: "
            f"{fastest_model[
                'generation_total_seconds'
            ]['median']:.4f} saniye"
        )

        print(
            "Toplam servis medyani: "
            f"{fastest_model[
                'service_total_seconds'
            ]['median']:.4f} saniye"
        )

        print(
            "\nBu sonuc yalnizca benchmark "
            "adayidir. Varsayilan model "
            "regresyon testleri tamamlanmadan "
            "degistirilmeyecek."
        )

    print_failed_runs(
        report
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
        "\nModel karsilastirma benchmark'i "
        "tamamlandi."
    )


if __name__ == "__main__":
    main()