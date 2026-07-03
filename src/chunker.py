def split_text_into_paragraphs(text):
    """
    Verilen metni bos satirlara gore paragraflara ayirir.

    RAG sistemlerinde paragraflar genellikle iyi bir baslangic chunk'idir.
    """
    paragraphs = []

    for paragraph in text.split("\n\n"):
        cleaned_paragraph = " ".join(paragraph.split())

        if cleaned_paragraph:
            paragraphs.append(cleaned_paragraph)

    return paragraphs


def chunk_document(document):
    """
    Tek bir dokumani chunk listesine donusturur.

    Input:
        {
            "source": "rag_notes.txt",
            "text": "..."
        }

    Output:
        [
            {
                "source": "rag_notes.txt",
                "chunk_index": 1,
                "chunk_text": "..."
            }
        ]
    """
    paragraphs = split_text_into_paragraphs(document["text"])
    chunks = []

    for index, paragraph in enumerate(paragraphs, start=1):
        chunks.append(
            {
                "source": document["source"],
                "chunk_index": index,
                "chunk_text": paragraph,
            }
        )

    return chunks


def chunk_documents(documents):
    """
    Birden fazla dokumani chunk listesine donusturur.
    """
    all_chunks = []

    for document in documents:
        document_chunks = chunk_document(document)
        all_chunks.extend(document_chunks)

    return all_chunks