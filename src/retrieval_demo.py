from src.retrieval import retrieve_top_chunks


DEFAULT_QUERY = "How does RAG make answers more reliable?"
DEFAULT_TOP_K = 3


def preview_text(text, max_length=180):
    """
    Uzun chunk metinlerini terminalde okunabilir bicimde kisaltir.
    """
    single_line_text = " ".join(text.split())

    if len(single_line_text) <= max_length:
        return single_line_text

    return single_line_text[:max_length] + "..."


def print_results(query, results):
    """
    Retrieval sonuclarini terminalde okunabilir bicimde gosterir.
    """
    print("\nSemantic retrieval sonuclari")
    print("=" * 70)
    print(f"Soru: {query}")
    print(f"Getirilen chunk sayisi: {len(results)}")

    for rank, result in enumerate(results, start=1):
        print("\n" + "-" * 70)
        print(f"Sira: {rank}")
        print(f"Kaynak: {result['source']}")
        print(f"Chunk index: {result['chunk_index']}")
        print(f"Benzerlik skoru: {result['similarity_score']:.4f}")
        print(f"Metin: {preview_text(result['chunk_text'])}")


def main():
    print("Semantic retrieval demo baslatiliyor...\n")

    results = retrieve_top_chunks(
        query=DEFAULT_QUERY,
        top_k=DEFAULT_TOP_K,
    )

    print_results(
        query=DEFAULT_QUERY,
        results=results,
    )


if __name__ == "__main__":
    main()