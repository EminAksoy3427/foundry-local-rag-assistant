from collections.abc import Callable
from time import perf_counter

from src.foundry_manager import get_foundry_manager


CHAT_MODEL_ALIAS = "phi-4-mini"
DEFAULT_MAX_TOKENS = 160
DEFAULT_TEMPERATURE = 0.0


class LocalGenerator:
    """
    Foundry Local chat modelini yoneten yardimci sinif.

    Bu sinif:

    - Foundry Local SDK'yi baslatir
    - Yerel chat modelini katalogdan alir
    - Modeli indirir ve yukler
    - Modelin tekrar kullanilmasini saglar
    - Streaming cevap uretir
    - Generation performans metriklerini olcer
    - Is bitince modeli guvenli sekilde kapatir
    """

    def __init__(
        self,
        model_alias=CHAT_MODEL_ALIAS,
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
    ):
        if max_tokens <= 0:
            raise ValueError(
                "max_tokens sifirdan buyuk olmalidir."
            )

        if temperature < 0:
            raise ValueError(
                "temperature negatif olamaz."
            )

        self.model_alias = model_alias
        self.max_tokens = max_tokens
        self.temperature = temperature

        self.manager = None
        self.model = None
        self.client = None

    @property
    def is_loaded(self):
        """
        Chat modelinin kullanima hazir olup
        olmadigini dondurur.
        """
        return self.client is not None

    def load(self):
        """
        Foundry Local chat modelini indirir,
        cache kontrolu yapar ve yukler.

        Model zaten yukluyse yeniden yukleme yapmaz.

        Returns:
            bool: Model bu cagri sirasinda yuklendiyse
            True, daha once yukluyse False.
        """
        if self.is_loaded:
            print(
                "Chat modeli zaten yuklu. "
                "Mevcut model yeniden kullaniliyor."
            )
            return False

        print(
            "Foundry Local chat sistemi "
            "baslatiliyor..."
        )

        self.manager = get_foundry_manager()

        print(
            "Chat modeli aliniyor: "
            f"{self.model_alias}"
        )

        self.model = (
            self.manager.catalog.get_model(
                self.model_alias
            )
        )

        if self.model is None:
            raise ValueError(
                "Chat modeli katalogda bulunamadi: "
                f"{self.model_alias}"
            )

        print(
            "Chat modeli indiriliyor veya "
            "cache kontrol ediliyor..."
        )

        self.model.download(
            lambda progress: print(
                "\rDownloading chat model: "
                f"{progress:.0f}%",
                end="",
                flush=True,
            )
        )

        print("\nChat modeli yukleniyor...")

        self.model.load()

        self.client = self.model.get_chat_client()

        self.client.settings.temperature = (
            self.temperature
        )

        self.client.settings.max_tokens = (
            self.max_tokens
        )

        print(
            "Chat modeli hazir. "
            f"Temperature: {self.temperature}, "
            f"Max tokens: {self.max_tokens}"
        )

        return True

    def generate_with_metrics(
        self,
        system_prompt,
        user_prompt,
        on_token: Callable[[str], None] | None = None,
    ):
        """
        Streaming cevap uretir ve generation
        performans metriklerini dondurur.

        Olculen degerler:

        - Ilk metin parcasina kadar gecen sure
        - Toplam generation suresi
        - Ilk parcadan son parcaya kadar gecen sure
        - Streaming parca sayisi
        - Cevap karakter sayisi
        """
        if self.client is None:
            raise RuntimeError(
                "Chat client hazir degil. "
                "Once load() cagrilmali."
            )

        cleaned_system_prompt = str(
            system_prompt
        ).strip()

        cleaned_user_prompt = str(
            user_prompt
        ).strip()

        if not cleaned_system_prompt:
            raise ValueError(
                "System prompt bos olamaz."
            )

        if not cleaned_user_prompt:
            raise ValueError(
                "User prompt bos olamaz."
            )

        messages = [
            {
                "role": "system",
                "content": cleaned_system_prompt,
            },
            {
                "role": "user",
                "content": cleaned_user_prompt,
            },
        ]

        answer_parts = []
        streaming_chunk_count = 0
        first_token_seconds = None

        generation_start = perf_counter()

        for chunk in (
            self.client.complete_streaming_chat(
                messages
            )
        ):
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            content = getattr(
                delta,
                "content",
                None,
            )

            if not content:
                continue

            if first_token_seconds is None:
                first_token_seconds = (
                    perf_counter()
                    - generation_start
                )

            answer_parts.append(content)
            streaming_chunk_count += 1

            if on_token is not None:
                on_token(content)

        generation_total_seconds = (
            perf_counter()
            - generation_start
        )

        answer = "".join(
            answer_parts
        ).strip()

        if not answer:
            raise RuntimeError(
                "Yerel chat modeli bos cevap "
                "uretti."
            )

        if first_token_seconds is None:
            first_token_seconds = (
                generation_total_seconds
            )

        streaming_seconds = max(
            generation_total_seconds
            - first_token_seconds,
            0.0,
        )

        return {
            "answer": answer,
            "metrics": {
                "time_to_first_token_seconds": (
                    first_token_seconds
                ),
                "generation_total_seconds": (
                    generation_total_seconds
                ),
                "streaming_seconds": (
                    streaming_seconds
                ),
                "streaming_chunk_count": (
                    streaming_chunk_count
                ),
                "answer_character_count": len(
                    answer
                ),
            },
        }

    def generate(
        self,
        system_prompt,
        user_prompt,
        on_token: Callable[[str], None] | None = None,
    ):
        """
        Geriye donuk uyumluluk icin yalnizca
        uretilen cevap metnini dondurur.

        Ayrintili generation metrikleri gereken
        durumlarda generate_with_metrics()
        kullanilmalidir.
        """
        generation_result = (
            self.generate_with_metrics(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                on_token=on_token,
            )
        )

        return generation_result["answer"]

    def unload(self):
        """
        Chat modeli yuklendiyse guvenli sekilde
        kapatir.

        Returns:
            bool: Model kapatildiysa True,
            zaten kapaliysa False.
        """
        if self.model is None:
            self.client = None
            return False

        print("Chat modeli kapatiliyor...")

        try:
            self.model.unload()
        finally:
            self.client = None
            self.model = None

        return True

    def __enter__(self):
        """
        LocalGenerator sinifinin with bloguyla
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