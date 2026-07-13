SYSTEM_PROMPT = """
Sen tamamen yerel calisan bir dokuman soru-cevap asistanisin.

Kurallar:
- Yalnizca kullanici mesajinda verilen baglami kullan.
- Baglamda cevap yoksa bunu acikca soyle.
- Tahmin yurutme ve baglam disinda bilgi uydurma.
- Cevabi kullanicinin sordugu dilde ver.
- Kullandigin bilgilerin kaynaklarini
  [dosya_adi - Chunk N] biciminde belirt.
- Cevabi acik, dogrudan ve gereksiz ayrintidan uzak tut.
""".strip()


def validate_retrieved_chunks(retrieved_chunks):
    """
    Retrieval sonucundaki chunk'larin gerekli alanlara sahip
    olup olmadigini kontrol eder.
    """
    chunks = list(retrieved_chunks)

    if not chunks:
        raise ValueError("Context olusturmak icin en az bir chunk gereklidir.")

    required_fields = {
        "source",
        "chunk_index",
        "chunk_text",
    }

    for position, chunk in enumerate(chunks, start=1):
        if not isinstance(chunk, dict):
            raise TypeError(
                f"{position}. retrieval sonucu bir sozluk degil."
            )

        missing_fields = required_fields - chunk.keys()

        if missing_fields:
            missing_text = ", ".join(sorted(missing_fields))

            raise ValueError(
                f"{position}. chunk icinde eksik alanlar var: "
                f"{missing_text}"
            )

        if not str(chunk["source"]).strip():
            raise ValueError(
                f"{position}. chunk icinde source bos olamaz."
            )

        if not str(chunk["chunk_text"]).strip():
            raise ValueError(
                f"{position}. chunk icinde chunk_text bos olamaz."
            )

    return chunks


def build_context(retrieved_chunks):
    """
    Retrieval sonuclarini kaynak bilgileriyle birlikte
    LLM'e verilecek duzenli bir context metnine cevirir.
    """
    chunks = validate_retrieved_chunks(retrieved_chunks)
    context_sections = []

    for position, chunk in enumerate(chunks, start=1):
        source = str(chunk["source"]).strip()
        chunk_index = chunk["chunk_index"]
        chunk_text = str(chunk["chunk_text"]).strip()

        context_sections.append(
            "\n".join(
                [
                    f"[KAYNAK {position}]",
                    f"Dosya: {source}",
                    f"Chunk: {chunk_index}",
                    "Icerik:",
                    chunk_text,
                ]
            )
        )

    return "\n\n".join(context_sections)


def build_user_prompt(question, context):
    """
    Kullanici sorusunu ve retrieval context'ini
    tek bir user prompt icinde birlestirir.
    """
    cleaned_question = question.strip()
    cleaned_context = context.strip()

    if not cleaned_question:
        raise ValueError("Kullanici sorusu bos olamaz.")

    if not cleaned_context:
        raise ValueError("Prompt context'i bos olamaz.")

    return (
        "Asagidaki baglami kullanarak soruyu cevapla.\n\n"
        "===== BAGLAM =====\n"
        f"{cleaned_context}\n"
        "===== BAGLAM SONU =====\n\n"
        "===== KULLANICI SORUSU =====\n"
        f"{cleaned_question}"
    )


def build_rag_prompt(question, retrieved_chunks):
    """
    Retrieval sonuclarindan LLM'e gonderilmeye hazir
    system ve user prompt'larini olusturur.
    """
    context = build_context(retrieved_chunks)
    user_prompt = build_user_prompt(question, context)

    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "context": context,
    }