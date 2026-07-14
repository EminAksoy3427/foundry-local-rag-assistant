from collections.abc import Callable

from src.context_builder import build_rag_prompt
from src.generator import CHAT_MODEL_ALIAS, LocalGenerator
from src.retrieval import retrieve_top_chunks


DEFAULT_TOP_K = 3


def answer_question(
    question,
    top_k=DEFAULT_TOP_K,
    on_token: Callable[[str], None] | None = None,
):
    """
    Kullanici sorusunu uctan uca local RAG pipeline'inda isler.

    Adimlar:
    1. Soruyla alakali chunk'lari getirir
    2. RAG context ve prompt'larini olusturur
    3. Yerel chat modelini yukler
    4. Dokumanlara dayali cevabi uretir
    5. Cevap, kaynaklar ve retrieval sonuclarini dondurur

    on_token verilirse streaming cevap parcalari bu fonksiyona gonderilir.
    """
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Kullanici sorusu bos olamaz.")

    if top_k <= 0:
        raise ValueError("top_k sifirdan buyuk olmalidir.")

    print("RAG servisi: ilgili chunk'lar getiriliyor...")
    retrieved_chunks = retrieve_top_chunks(
        query=cleaned_question,
        top_k=top_k,
    )

    print("\nRAG servisi: context ve prompt'lar olusturuluyor...")
    rag_prompt = build_rag_prompt(
        question=cleaned_question,
        retrieved_chunks=retrieved_chunks,
    )

    generator = LocalGenerator()

    try:
        print("\nRAG servisi: yerel chat modeli yukleniyor...")
        generator.load()

        print("\nRAG servisi: cevap uretiliyor...")
        answer = generator.generate(
            system_prompt=rag_prompt["system_prompt"],
            user_prompt=rag_prompt["user_prompt"],
            on_token=on_token,
        )
    finally:
        if on_token is not None:
            print()

        generator.unload()

    return {
        "question": cleaned_question,
        "answer": answer,
        "source_references": rag_prompt["source_references"],
        "retrieved_chunks": retrieved_chunks,
        "model_alias": generator.model_alias,
    }