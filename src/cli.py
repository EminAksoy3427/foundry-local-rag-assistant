from src.db import count_documents, initialize_database
from src.rag_service import answer_question


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
    Modelden gelen streaming cevap parcasini anlik olarak terminale yazar.
    """
    print(token, end="", flush=True)


def print_welcome_message():
    """
    CLI baslangic mesajini gosterir.
    """
    print("=" * 70)
    print("Foundry Local RAG Assistant")
    print("=" * 70)
    print("Yerel dokumanlariniz hakkinda soru sorabilirsiniz.")
    print("Programdan cikmak icin: exit, quit veya q")
    print("=" * 70)


def database_is_ready():
    """
    SQLite tablosunun varligini ve dokuman kaydi bulunup
    bulunmadigini kontrol eder.
    """
    initialize_database()
    return count_documents() > 0


def print_sources(source_references):
    """
    RAG servisinin kullandigi gercek kaynaklari terminalde gosterir.
    """
    print("\nKaynaklar")
    print("-" * 70)

    if not source_references:
        print("Kaynak bulunamadi.")
        return

    for source_reference in source_references:
        print(f"- {source_reference}")


def run_cli():
    """
    Kullanicidan tekrar tekrar soru alan interaktif CLI dongusunu calistirir.
    """
    print_welcome_message()

    if not database_is_ready():
        print("\nSQLite veritabaninda dokuman bulunamadi.")
        print("Once ingestion pipeline'i calistirin:")
        print("python -m src.ingest_demo")
        return

    print(f"\nSQLite hazir. Kayit sayisi: {count_documents()}")

    while True:
        try:
            question = input("\nSorunuz: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nProgram kapatiliyor.")
            break

        if not question:
            print("Bos soru giremezsiniz.")
            continue

        if question.lower() in EXIT_COMMANDS:
            print("Program kapatiliyor.")
            break

        print("\nYerel LLM cevabi")
        print("=" * 70)

        try:
            result = answer_question(
                question=question,
                top_k=DEFAULT_TOP_K,
                on_token=print_stream_token,
            )
        except ValueError as error:
            print(f"\nGirdi hatasi: {error}")
            continue
        except Exception as error:
            print(
                f"\nRAG islemi sirasinda hata olustu "
                f"({type(error).__name__}): {error}"
            )
            continue

        print("=" * 70)

        print_sources(result["source_references"])

        print("\nCevap bilgisi")
        print("-" * 70)
        print(f"Model: {result['model_alias']}")
        print(f"Getirilen chunk sayisi: {len(result['retrieved_chunks'])}")


def main():
    run_cli()


if __name__ == "__main__":
    main()