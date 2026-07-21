from src.final_audit import run_final_audit


def main():
    """
    Final release audit'ini calistirir ve
    sonucu terminale yazdirir.
    """
    print("=" * 70)
    print("FOUNDRY LOCAL RAG FINAL AUDIT")
    print("=" * 70)

    result = run_final_audit()
    report = result["report"]
    summary = report["summary"]

    for check in report["checks"]:
        status = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        blocking = (
            "BLOCKING"
            if check["blocking"]
            else "INFORMATIONAL"
        )

        print("\n" + "-" * 70)
        print(
            f"[{status}] {check['name']}"
        )
        print(
            f"Tip: {blocking}"
        )
        print(
            f"Detay: {check['details']}"
        )

    print("\n" + "=" * 70)
    print("FINAL AUDIT OZETI")
    print("=" * 70)

    print(
        "Toplam kontrol: "
        f"{summary['total_checks']}"
    )

    print(
        "Basarili kontrol: "
        f"{summary['passed_checks']}"
    )

    print(
        "Basarisiz kontrol: "
        f"{summary['failed_checks']}"
    )

    print(
        "Blocking kontrol: "
        f"{summary['blocking_passed']}/"
        f"{summary['blocking_total']}"
    )

    print(
        "Release hazir: "
        f"{summary['release_ready']}"
    )

    print("\nRapor dosyalari:")

    print(
        f"- JSON: {result['json_path']}"
    )

    print(
        f"- Markdown: "
        f"{result['markdown_path']}"
    )

    if not summary["release_ready"]:
        print(
            "\nRelease audit basarisiz. "
            "v1.0.0 surecine gecilmemelidir."
        )
        raise SystemExit(1)

    print(
        "\nTum blocking kontroller gecti."
    )

    print(
        "Proje v1.0.0 release sureci icin "
        "uygundur."
    )


if __name__ == "__main__":
    main()