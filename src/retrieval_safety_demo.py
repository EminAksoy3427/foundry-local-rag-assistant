from src.rag_service import (
    DEFAULT_MIN_SIMILARITY_SCORE,
    answer_question,
)


TEST_CASES = [
    {
        "label": "Dokumanlarda bulunmayan soru",
        "question": "Jupiter'in kac uydusu vardir?",
    },
    {
        "label": "Dokumanlarda bulunan soru",
        "question": "Foundry Local ne ise yarar?",
    },
]


def print_candidate_scores(candidate_chunks):
    """
    Esik kontrolunden onceki top-k aday sonuclari gosterir.
    """
    print("\nAday retrieval sonuclari:")

    for rank, chunk in enumerate(candidate_chunks, start=1):
        print(
            f"{rank}. {chunk['source']} "
            f"| Chunk {chunk['chunk_index']} "
            f"| Skor: {chunk['similarity_score']:.4f}"
        )


def main():
    print("Retrieval safety demo baslatiliyor.")
    print(
        "Minimum benzerlik esigi: "
        f"{DEFAULT_MIN_SIMILARITY_SCORE:.4f}"
    )

    for test_case in TEST_CASES:
        print("\n" + "=" * 70)
        print(test_case["label"])
        print("=" * 70)
        print(f"Soru: {test_case['question']}\n")

        result = answer_question(
            question=test_case["question"],
            top_k=3,
            min_similarity_score=DEFAULT_MIN_SIMILARITY_SCORE,
        )

        print(f"\nDurum: {result['status']}")
        print(f"Cevap: {result['answer']}")

        model_name = result["model_alias"] or "Yuklenmedi"
        print(f"Model: {model_name}")

        if result["top_similarity_score"] is not None:
            print(
                "En yuksek skor: "
                f"{result['top_similarity_score']:.4f}"
            )

        print(
            "Kullanilan chunk sayisi: "
            f"{len(result['retrieved_chunks'])}"
        )

        print_candidate_scores(result["candidate_chunks"])

        print("\nKaynaklar:")

        if result["source_references"]:
            for reference in result["source_references"]:
                print(f"- {reference}")
        else:
            print("- Kaynak kullanilmadi.")

    print("\nRetrieval safety demo tamamlandi.")


if __name__ == "__main__":
    main()