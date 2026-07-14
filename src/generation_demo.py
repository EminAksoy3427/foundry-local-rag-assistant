from src.context_builder import build_rag_prompt
from src.generator import LocalGenerator
from src.retrieval import retrieve_top_chunks


DEFAULT_QUERY = "RAG cevaplari nasil daha guvenilir hale getirir?"
DEFAULT_TOP_K = 3


def print_stream_token(token):
    """
    Modelden gelen streaming cevap parcasini anlik yazdirir.
    """
    print(token, end="", flush=True)


def print_retrieved_sources(results):
    """
    LLM'e context olarak verilen kaynaklari gosterir.
    """
    print("\nKullanilan retrieval sonuclari")
    print("=" * 70)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['source']} "
            f"| Chunk {result['chunk_index']} "
            f"| Skor: {result['similarity_score']:.4f}"
        )


def main():
    print("Local RAG generation demo baslatiliyor...\n")
    print(f"Kullanici sorusu: {DEFAULT_QUERY}")

    print("\n1. Ilgili chunk'lar getiriliyor...")
    retrieved_chunks = retrieve_top_chunks(
        query=DEFAULT_QUERY,
        top_k=DEFAULT_TOP_K,
    )

    print_retrieved_sources(retrieved_chunks)

    print("\n2. RAG context ve prompt'lari olusturuluyor...")
    rag_prompt = build_rag_prompt(
        question=DEFAULT_QUERY,
        retrieved_chunks=retrieved_chunks,
    )

    generator = LocalGenerator()

    try:
        print("\n3. Yerel chat modeli yukleniyor...")
        generator.load()

        print("\n4. Yerel LLM cevabi uretiliyor...")
        print("=" * 70)

        answer = generator.generate(
            system_prompt=rag_prompt["system_prompt"],
            user_prompt=rag_prompt["user_prompt"],
            on_token=print_stream_token,
        )

        print("\n" + "=" * 70)

        print("\nKaynaklar:")
        for source_reference in rag_prompt["source_references"]:
            print(f"- {source_reference}")

        print("\nCevap basariyla uretildi.")
        print(f"Cevap karakter sayisi: {len(answer)}")

    finally:
        print()
        generator.unload()

    print("\nLocal RAG generation demo tamamlandi.")


if __name__ == "__main__":
    main()