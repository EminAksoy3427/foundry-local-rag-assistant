from src.context_builder import build_rag_prompt
from src.retrieval import retrieve_top_chunks


DEFAULT_QUERY = "RAG cevaplari nasil daha guvenilir hale getirir?"
DEFAULT_TOP_K = 3


def preview_text(text, max_length=130):
    """
    Uzun chunk metnini terminalde kisa gostermek icin kullanilir.
    """
    single_line_text = " ".join(text.split())

    if len(single_line_text) <= max_length:
        return single_line_text

    return single_line_text[:max_length] + "..."


def print_retrieval_summary(results):
    """
    Prompt olusturulmadan once retrieval sonuclarini ozetler.
    """
    print("\nRetrieval ozeti")
    print("=" * 70)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['source']} "
            f"| Chunk {result['chunk_index']} "
            f"| Skor: {result['similarity_score']:.4f}"
        )
        print(f"   {preview_text(result['chunk_text'])}")


def main():
    print("Context builder demo baslatiliyor...\n")
    print(f"Kullanici sorusu: {DEFAULT_QUERY}")

    results = retrieve_top_chunks(
        query=DEFAULT_QUERY,
        top_k=DEFAULT_TOP_K,
    )

    print_retrieval_summary(results)

    rag_prompt = build_rag_prompt(
        question=DEFAULT_QUERY,
        retrieved_chunks=results,
    )

    print("\n\nOlusturulan context")
    print("=" * 70)
    print(rag_prompt["context"])

    print("\n\nSystem prompt")
    print("=" * 70)
    print(rag_prompt["system_prompt"])

    print("\n\nUser prompt")
    print("=" * 70)
    print(rag_prompt["user_prompt"])

    print("\n\nPrompt olusturma basariyla tamamlandi.")


if __name__ == "__main__":
    main()