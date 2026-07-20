from src.db import (
    count_documents,
    initialize_database,
)
from src.rag_session import LocalRAGSession


DEFAULT_TOP_K = 3

EXIT_COMMANDS = {
    "exit",
    "quit",
    "q",
    "cikis",
    "çıkış",
    "çikiş",
}


def print_stream_token(token):
    """
    Modelden gelen streaming cevap parcasini
    anlik olarak terminale yazar.
    """
    print(
        token,
        end="",
        flush=True,
    )


def print_welcome_message():
    """
    CLI baslangic mesajini gosterir.
    """
    print("=" * 70)
    print("Foundry Local RAG Assistant")
    print("=" * 70)

    print(
        "Yerel dokumanlariniz hakkinda "
        "soru sorabilirsiniz."
    )

    print(
        "Programdan cikmak icin: "
        "exit, quit veya q"
    )

    print("=" * 70)


def database_is_ready():
    """
    SQLite tablosunun varligini ve dokuman kaydi
    bulunup bulunmadigini kontrol eder.
    """
    initialize_database()

    return count_documents() > 0


def print_sources(source_references):
    """
    RAG servisinin kullandigi gercek kaynaklari
    terminalde gosterir.
    """
    print("\nKaynaklar")
    print("-" * 70)

    if not source_references:
        print("Kaynak bulunamadi.")
        return

    for source_reference in source_references:
        print(f"- {source_reference}")


def print_answer_information(result):
    """
    RAG sonucunun durum, model, kaynak ve
    performans bilgilerini terminalde gosterir.
    """
    print("\nCevap bilgisi")
    print("-" * 70)

    print(f"Durum: {result['status']}")

    model_name = (
        result["model_alias"]
        or "Yuklenmedi"
    )

    print(f"Model: {model_name}")

    print(
        "Ana kaynak: "
        f"{result['primary_source']}"
    )

    print(
        "Kullanilan chunk sayisi: "
        f"{len(result['retrieved_chunks'])}"
    )

    print(
        "Aday chunk sayisi: "
        f"{len(result['candidate_chunks'])}"
    )

    if (
        result["top_similarity_score"]
        is not None
    ):
        print(
            "En yuksek benzerlik skoru: "
            f"{result['top_similarity_score']:.4f}"
        )

    print(
        "Minimum benzerlik esigi: "
        f"{result['min_similarity_score']:.4f}"
    )

    print(
        "Embedding modeli yeniden kullanildi: "
        f"{result['embedding_model_reused']}"
    )

    print(
        "Chat modeli kullanildi: "
        f"{result['chat_model_used']}"
    )

    print(
        "Chat modeli yeniden kullanildi: "
        f"{result['chat_model_reused']}"
    )

    performance_metrics = result[
        "performance_metrics"
    ]

    print(
        "Retrieval suresi: "
        f"{performance_metrics['retrieval_total_seconds']:.4f} "
        "saniye"
    )

    print(
        "Chat modeli yukleme suresi: "
        f"{performance_metrics['chat_model_load_seconds']:.4f} "
        "saniye"
    )

    print(
        "Cevap uretme suresi: "
        f"{performance_metrics['generation_seconds']:.4f} "
        "saniye"
    )

    print(
        "Toplam servis suresi: "
        f"{performance_metrics['service_total_seconds']:.4f} "
        "saniye"
    )


def run_cli():
    """
    Kalici model session'i kullanan interaktif
    CLI dongusunu calistirir.

    Embedding modeli CLI baslangicinda bir kez
    yuklenir.

    Chat modeli ilk cevaplanabilir soruda
    lazy-load edilir ve sonraki sorularda
    yeniden kullanilir.
    """
    print_welcome_message()

    if not database_is_ready():
        print(
            "\nSQLite veritabaninda dokuman "
            "bulunamadi."
        )

        print(
            "Once ingestion pipeline'i "
            "calistirin:"
        )

        print(
            "python -m src.ingest_demo"
        )

        return

    document_count = count_documents()

    print(
        "\nSQLite hazir. "
        f"Kayit sayisi: {document_count}"
    )

    session = LocalRAGSession(
        top_k=DEFAULT_TOP_K
    )

    try:
        print(
            "\nYerel model session'i "
            "hazirlaniyor..."
        )

        startup_metrics = session.start()

        print(
            "Embedding modeli baslangic suresi: "
            f"{startup_metrics['embedding_model_load_seconds']:.4f} "
            "saniye"
        )

        print(
            "Chat modeli ilk cevaplanabilir "
            "soruda yuklenecek."
        )

        while True:
            try:
                question = input(
                    "\nSorunuz: "
                ).strip()

            except (
                KeyboardInterrupt,
                EOFError,
            ):
                print(
                    "\n\nProgram kapatiliyor."
                )
                break

            if not question:
                print(
                    "Bos soru giremezsiniz."
                )
                continue

            if (
                question.lower()
                in EXIT_COMMANDS
            ):
                print(
                    "Program kapatiliyor."
                )
                break

            print("\nYerel LLM cevabi")
            print("=" * 70)

            try:
                result = (
                    session.answer_question(
                        question=question,
                        on_token=(
                            print_stream_token
                        ),
                    )
                )

            except ValueError as error:
                print(
                    f"\nGirdi hatasi: {error}"
                )
                continue

            except Exception as error:
                print(
                    "\nRAG islemi sirasinda "
                    "hata olustu "
                    f"({type(error).__name__}): "
                    f"{error}"
                )
                continue

            print("=" * 70)

            print_sources(
                result["source_references"]
            )

            print_answer_information(
                result
            )

    finally:
        if (
            session.is_started
            or session.chat_model_is_loaded
        ):
            print(
                "\nYerel model session'i "
                "kapatiliyor..."
            )

            shutdown_metrics = (
                session.close()
            )

            print(
                "Chat modeli kapatma suresi: "
                f"{shutdown_metrics['chat_model_unload_seconds']:.4f} "
                "saniye"
            )

            print(
                "Embedding modeli kapatma suresi: "
                f"{shutdown_metrics['embedding_model_unload_seconds']:.4f} "
                "saniye"
            )

            print(
                "Toplam session kapanis suresi: "
                f"{shutdown_metrics['session_close_total_seconds']:.4f} "
                "saniye"
            )


def main():
    run_cli()


if __name__ == "__main__":
    main()