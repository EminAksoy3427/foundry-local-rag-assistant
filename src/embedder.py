from src.foundry_manager import get_foundry_manager


EMBEDDING_MODEL_ALIASES = [
    "qwen3-embedding-0.6b",
    "qwen3-0.6b-embedding",
]


class LocalEmbedder:
    """
    Foundry Local embedding modelini yoneten yardimci sinif.

    Bu sinif:

    - Foundry Local SDK'yi baslatir
    - Uygun embedding modelini katalogdan bulur
    - Modeli indirir ve yukler
    - Metinleri embedding vektorune cevirir
    - Ayni model nesnesinin tekrar kullanilmasini saglar
    - Is bitince modeli guvenli sekilde kapatir
    """

    def __init__(self):
        self.manager = None
        self.model = None
        self.client = None
        self.selected_model_alias = None

    @property
    def is_loaded(self):
        """
        Embedding modelinin kullanima hazir olup
        olmadigini dondurur.
        """
        return self.client is not None

    def _find_embedding_model(self):
        """
        Bilinen embedding model alias'larini sirayla
        dener ve ilk bulunan modeli dondurur.
        """
        for alias in EMBEDDING_MODEL_ALIASES:
            print(f"Model alias deneniyor: {alias}")

            model = self.manager.catalog.get_model(
                alias
            )

            if model is not None:
                self.selected_model_alias = alias
                return model

        available_aliases = ", ".join(
            EMBEDDING_MODEL_ALIASES
        )

        raise ValueError(
            "Embedding modeli bulunamadi. "
            "Denenen alias'lar: "
            f"{available_aliases}"
        )

    def load(self):
        """
        Embedding modelini indirir, cache kontrolu
        yapar ve yukler.

        Model zaten yukluyse yeniden yukleme yapmaz.

        Returns:
            bool: Model bu cagri sirasinda yuklendiyse
            True, daha once yukluyse False.
        """
        if self.is_loaded:
            print(
                "Embedding modeli zaten yuklu. "
                "Mevcut model yeniden kullaniliyor."
            )
            return False

        print(
            "Foundry Local embedding sistemi "
            "baslatiliyor..."
        )

        self.manager = get_foundry_manager()

        print("Embedding modeli aliniyor...")

        self.model = self._find_embedding_model()

        print(
            "Secilen embedding modeli: "
            f"{self.selected_model_alias}"
        )

        print(
            "Embedding modeli indiriliyor veya "
            "cache kontrol ediliyor..."
        )

        self.model.download(
            lambda progress: print(
                "\rDownloading embedding model: "
                f"{progress:.0f}%",
                end="",
                flush=True,
            )
        )

        print("\nEmbedding modeli yukleniyor...")

        self.model.load()

        self.client = (
            self.model.get_embedding_client()
        )

        print("Embedding modeli hazir.")

        return True

    def embed_text(self, text):
        """
        Tek bir metni embedding vektorune cevirir.
        """
        if self.client is None:
            raise RuntimeError(
                "Embedding client hazir degil. "
                "Once load() cagrilmali."
            )

        cleaned_text = str(text).strip()

        if not cleaned_text:
            raise ValueError(
                "Embedding uretilecek metin "
                "bos olamaz."
            )

        response = (
            self.client.generate_embedding(
                cleaned_text
            )
        )

        if not response.data:
            raise RuntimeError(
                "Embedding modeli veri dondurmedi."
            )

        return response.data[0].embedding

    def embed_chunks(self, chunks):
        """
        Chunk listesindeki her chunk icin
        embedding uretir.
        """
        if not isinstance(chunks, list):
            raise TypeError(
                "chunks parametresi bir liste "
                "olmalidir."
            )

        embedded_chunks = []

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            print(
                f"Embedding uretiliyor: "
                f"{index}/{len(chunks)} "
                f"| {chunk['source']} "
                f"| Chunk {chunk['chunk_index']}"
            )

            embedding = self.embed_text(
                chunk["chunk_text"]
            )

            embedded_chunks.append(
                {
                    "source": chunk["source"],
                    "chunk_index": chunk[
                        "chunk_index"
                    ],
                    "chunk_text": chunk[
                        "chunk_text"
                    ],
                    "embedding": embedding,
                }
            )

        return embedded_chunks

    def unload(self):
        """
        Model yuklendiyse guvenli sekilde kapatir.

        Returns:
            bool: Model kapatildiysa True,
            zaten kapaliysa False.
        """
        if self.model is None:
            self.client = None
            return False

        print("Embedding modeli kapatiliyor...")

        try:
            self.model.unload()
        finally:
            self.client = None
            self.model = None

        return True

    def __enter__(self):
        """
        LocalEmbedder sinifinin with bloguyla
        kullanilabilmesini saglar.
        """
        self.load()
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        traceback,
    ):
        """
        with blogu bittiginde modeli kapatir.
        """
        self.unload()
        return False