SYSTEM_PROMPT = """
Sen tamamen yerel calisan bir dokuman soru-cevap asistanisin.

Kurallar:
- Yalnizca verilen baglama dayanarak cevap ver.
- Dilbilgisel olarak tamamlanmis ve dogal cumleler kur.
- Baglam disinda bilgi ekleme veya tahmin yurutme.
- Cevabi kullanicinin sordugu dilde ver.
- Sorunun ana kavramini cevapta acikca belirt.
- Neden veya nasil sorularinda baglamdaki somut nedenleri ya da adimlari kullan.
- En fazla uc kisa cumle kullan.
- Liste, baslik veya kaynak bolumu olusturma.
- Cevabi acik ve dogrudan yaz.
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

def build_source_references(retrieved_chunks):
    """
    Retrieval sonuclarindan tekrarsiz kaynak referanslari olusturur.

    Kaynaklari modelin uretmesine birakmak yerine uygulama tarafinda
    olusturmak, gosterilen kaynaklarin gercek retrieval sonuclariyla
    uyumlu olmasini garanti eder.
    """
    chunks = validate_retrieved_chunks(retrieved_chunks)

    source_references = []
    seen_references = set()

    for chunk in chunks:
        source = str(chunk["source"]).strip()
        chunk_index = chunk["chunk_index"]
        reference = f"[{source} - Chunk {chunk_index}]"

        if reference in seen_references:
            continue

        seen_references.add(reference)
        source_references.append(reference)

    return source_references


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
    "BAGLAM:\n"
    f"{cleaned_context}\n\n"
    "SORU:\n"
    f"{cleaned_question}\n\n"
    "CEVAP:"
)

def build_rag_prompt(question, retrieved_chunks):
    """
    Retrieval sonuclarindan LLM'e gonderilmeye hazir
    prompt'lari ve kaynak referanslarini olusturur.
    """
    chunks = validate_retrieved_chunks(retrieved_chunks)
    context = build_context(chunks)
    user_prompt = build_user_prompt(question, context)
    source_references = build_source_references(chunks)

    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "context": context,
        "source_references": source_references,
    }