from foundry_local_sdk import Configuration, FoundryLocalManager


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
    - Modeli indirir/yukler
    - Metinleri embedding vektorune cevirir
    - Is bitince modeli kapatir
    """

    def __init__(self):
        self.manager = None
        self.model = None
        self.client = None
        self.selected_model_alias = None

    def _find_embedding_model(self):
        """
        Bilinen embedding model alias'larini sirayla dener.
        Ilk bulunan modeli dondurur.
        """
        for alias in EMBEDDING_MODEL_ALIASES:
            print(f"Model alias deneniyor: {alias}")
            model = self.manager.catalog.get_model(alias)

            if model is not None:
                self.selected_model_alias = alias
                return model

        available_aliases = ", ".join(EMBEDDING_MODEL_ALIASES)

        raise ValueError(
            "Embedding modeli bulunamadi. Denenen alias'lar: "
            f"{available_aliases}"
        )

    def load(self):
        """
        Embedding modelini indirir/cache kontrolu yapar ve yukler.
        """
        print("Foundry Local embedding sistemi baslatiliyor...")

        FoundryLocalManager.initialize(
            Configuration(app_name="foundry-local-rag-assistant")
        )
        self.manager = FoundryLocalManager.instance

        print("Embedding modeli aliniyor...")
        self.model = self._find_embedding_model()

        print(f"Secilen embedding modeli: {self.selected_model_alias}")

        print("Embedding modeli indiriliyor veya cache kontrol ediliyor...")
        self.model.download(
            lambda progress: print(
                f"\rDownloading embedding model: {progress:.0f}%",
                end="",
                flush=True,
            )
        )

        print("\nEmbedding modeli yukleniyor...")
        self.model.load()

        self.client = self.model.get_embedding_client()

    def embed_text(self, text):
        """
        Tek bir metni embedding vektorune cevirir.
        """
        if self.client is None:
            raise RuntimeError("Embedding client hazir degil. Once load() cagrilmali.")

        response = self.client.generate_embedding(text)
        return response.data[0].embedding

    def embed_chunks(self, chunks):
        """
        Chunk listesindeki her chunk icin embedding uretir.
        """
        embedded_chunks = []

        for index, chunk in enumerate(chunks, start=1):
            print(
                f"Embedding uretiliyor: {index}/{len(chunks)} "
                f"| {chunk['source']} | Chunk {chunk['chunk_index']}"
            )

            embedding = self.embed_text(chunk["chunk_text"])

            embedded_chunks.append(
                {
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "chunk_text": chunk["chunk_text"],
                    "embedding": embedding,
                }
            )

        return embedded_chunks

    def unload(self):
        """
        Model yuklendiyse kapatir.
        """
        if self.model is not None:
            print("Embedding modeli kapatiliyor...")
            self.model.unload()