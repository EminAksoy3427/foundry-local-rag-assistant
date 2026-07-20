from time import perf_counter

from src.embedder import LocalEmbedder
from src.generator import (
    CHAT_MODEL_ALIAS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    LocalGenerator,
)
from src.rag_service import (
    DEFAULT_TOP_K,
    answer_question,
)
from src.retrieval import (
    DEFAULT_MIN_SIMILARITY_SCORE,
)


class LocalRAGSession:
    """
    Birden fazla soru boyunca yerel modelleri
    tekrar kullanan kalici RAG oturumudur.

    Davranis:

    - Embedding modeli session baslangicinda yuklenir
    - Embedding modeli her soruda yeniden kullanilir
    - Chat modeli ilk cevaplanabilir soruda yuklenir
    - Chat modeli sonraki cevaplanabilir sorularda
      yeniden kullanilir
    - Cevaplanamaz sorularda chat modeli kullanilmaz
    - Session kapatilirken modeller guvenli sekilde
      kapatilir
    """

    def __init__(
        self,
        top_k=DEFAULT_TOP_K,
        min_similarity_score=(
            DEFAULT_MIN_SIMILARITY_SCORE
        ),
        chat_model_alias=CHAT_MODEL_ALIAS,
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
    ):
        if top_k <= 0:
            raise ValueError(
                "top_k sifirdan buyuk olmalidir."
            )

        if not (
            -1.0
            <= min_similarity_score
            <= 1.0
        ):
            raise ValueError(
                "Minimum benzerlik skoru -1.0 ile "
                "1.0 arasinda olmalidir."
            )

        self.top_k = top_k
        self.min_similarity_score = (
            min_similarity_score
        )

        self.embedder = LocalEmbedder()

        self.generator = LocalGenerator(
            model_alias=chat_model_alias,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        self.started = False

        self.startup_metrics = {
            "embedding_model_load_seconds": 0.0,
            "session_start_total_seconds": 0.0,
        }

        self.shutdown_metrics = {
            "chat_model_unload_seconds": 0.0,
            "embedding_model_unload_seconds": 0.0,
            "session_close_total_seconds": 0.0,
        }

    @property
    def is_started(self):
        """
        Session'in kullanima hazir olup olmadigini
        dondurur.
        """
        return (
            self.started
            and self.embedder.is_loaded
        )

    @property
    def chat_model_is_loaded(self):
        """
        Chat modelinin yuklu olup olmadigini
        dondurur.
        """
        return self.generator.is_loaded

    def start(self):
        """
        Kalici RAG session'ini baslatir.

        Embedding modeli burada bir kez yuklenir.
        Chat modeli ise lazy loading nedeniyle
        burada yuklenmez.
        """
        if self.is_started:
            print(
                "Kalici RAG session zaten acik."
            )

            return {
                **self.startup_metrics,
                "already_started": True,
            }

        print(
            "Kalici RAG session baslatiliyor..."
        )

        session_start = perf_counter()

        embedding_load_start = perf_counter()

        self.embedder.load()

        embedding_load_seconds = (
            perf_counter()
            - embedding_load_start
        )

        self.started = True

        self.startup_metrics = {
            "embedding_model_load_seconds": (
                embedding_load_seconds
            ),
            "session_start_total_seconds": (
                perf_counter()
                - session_start
            ),
        }

        print(
            "Kalici RAG session hazir."
        )

        print(
            "Embedding model startup suresi: "
            f"{embedding_load_seconds:.4f} saniye"
        )

        print(
            "Chat modeli lazy loading ile "
            "ilk cevaplanabilir soruda "
            "yuklenecek."
        )

        return {
            **self.startup_metrics,
            "already_started": False,
        }

    def answer_question(
        self,
        question,
        on_token=None,
        top_k=None,
        min_similarity_score=None,
    ):
        """
        Bir soruyu kalici model nesneleriyle
        cevaplar.
        """
        if not self.is_started:
            self.start()

        selected_top_k = (
            self.top_k
            if top_k is None
            else top_k
        )

        selected_min_similarity = (
            self.min_similarity_score
            if min_similarity_score is None
            else min_similarity_score
        )

        return answer_question(
            question=question,
            top_k=selected_top_k,
            min_similarity_score=(
                selected_min_similarity
            ),
            on_token=on_token,
            embedder=self.embedder,
            generator=self.generator,
            manage_embedder_lifecycle=False,
            manage_generator_lifecycle=False,
        )

    def close(self):
        """
        Session boyunca yuklu kalan modelleri
        guvenli sekilde kapatir.
        """
        close_start = perf_counter()

        chat_unload_seconds = 0.0
        embedding_unload_seconds = 0.0

        if self.generator.is_loaded:
            chat_unload_start = perf_counter()

            self.generator.unload()

            chat_unload_seconds = (
                perf_counter()
                - chat_unload_start
            )

        if self.embedder.is_loaded:
            embedding_unload_start = (
                perf_counter()
            )

            self.embedder.unload()

            embedding_unload_seconds = (
                perf_counter()
                - embedding_unload_start
            )

        self.started = False

        self.shutdown_metrics = {
            "chat_model_unload_seconds": (
                chat_unload_seconds
            ),
            "embedding_model_unload_seconds": (
                embedding_unload_seconds
            ),
            "session_close_total_seconds": (
                perf_counter()
                - close_start
            ),
        }

        print(
            "Kalici RAG session kapatildi."
        )

        return dict(
            self.shutdown_metrics
        )

    def __enter__(self):
        """
        Session'in with bloguyla kullanilmasini
        saglar.
        """
        self.start()
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        traceback,
    ):
        """
        with blogu bittiginde modelleri kapatir.
        """
        self.close()
        return False