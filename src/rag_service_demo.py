from src.rag_service import answer_question


DEFAULT_QUERY = "RAG cevaplari nasil daha guvenilir hale getirir?"
DEFAULT_TOP_K = 3


def print_stream_token(token):
    """
    Modelden gelen streaming cevap parcasini terminale yazar.
    """
    print(token, end="", flush=True)


def print_retrieval_results(retrieved_chunks):
    """
    Service sonucundaki retrieval bilgilerini gosterir.
    """
    print("\nRetrieval sonuclari")
    print("=" * 70)

    for rank, chunk in enumerate(retrieved_chunks, start=1):
        print(
            f"{rank}. {chunk['source']} "
            f"| Chunk {chunk['chunk_index']} "
            f"| Skor: {chunk['similarity_score']:.4f}"
        )


def print_sources(source_references):
    """
    Gercek retrieval sonuclarindan olusturulan kaynaklari gosterir.
    """
    print("\nKaynaklar")
    print("=" * 70)

    for source_reference in source_references:
        print(f"- {source_reference}")


def main():
    print("RAG service demo baslatiliyor...\n")
    print(f"Kullanici sorusu: {DEFAULT_QUERY}")

    print("\nYerel LLM cevabi")
    print("=" * 70)

    result = answer_question(
        question=DEFAULT_QUERY,
        top_k=DEFAULT_TOP_K,
        on_token=print_stream_token,
    )

    print("\n" + "=" * 70)

    print_retrieval_results(result["retrieved_chunks"])
    print_sources(result["source_references"])

    print("\nService ozeti")
    print("=" * 70)
    print(f"Model: {result['model_alias']}")
    print(f"Soru: {result['question']}")
    print(f"Cevap karakter sayisi: {len(result['answer'])}")
    print(f"Kaynak sayisi: {len(result['source_references'])}")
    print(f"Retrieval sonucu sayisi: {len(result['retrieved_chunks'])}")

    print("\nRAG service demo basariyla tamamlandi.")


if __name__ == "__main__":
    main()