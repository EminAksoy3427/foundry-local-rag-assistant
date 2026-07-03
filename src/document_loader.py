from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"


def read_text_file(file_path):
    """
    Verilen .txt dosyasini UTF-8 formatinda okur.
    """
    return file_path.read_text(encoding="utf-8")


def load_documents():
    """
    data/documents klasorundeki .txt dosyalarini okur.

    Her dokumani source ve text bilgisiyle birlikte liste olarak dondurur.
    """
    documents = []

    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(f"Documents folder not found: {DOCUMENTS_DIR}")

    text_files = sorted(DOCUMENTS_DIR.glob("*.txt"))

    for file_path in text_files:
        text = read_text_file(file_path).strip()

        if not text:
            continue

        documents.append(
            {
                "source": file_path.name,
                "text": text,
            }
        )

    return documents


def preview_text(text, max_length=120):
    """
    Uzun metinlerin terminalde kisa on izlemesini gosterir.
    """
    single_line_text = " ".join(text.split())

    if len(single_line_text) <= max_length:
        return single_line_text

    return single_line_text[:max_length] + "..."