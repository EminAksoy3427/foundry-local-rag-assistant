from collections.abc import Callable

from src.foundry_manager import get_foundry_manager


CHAT_MODEL_ALIAS = "phi-4-mini"
DEFAULT_MAX_TOKENS = 220
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
    - Is bitince modeli guvenli sekilde kapatir
    """

    def __init__(
        self,
        model_alias=CHAT_MODEL_ALIAS,
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
    ):
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
            f"Chat modeli aliniyor: "
            f"{self.model_alias}"
        )

        self.model = (
            self.manager.catalog.get_model(
                self.model_alias
            )
        )

        if self.model is None:
            raise ValueError(
                "Chat modeli katalogda "
                "bulunamadi: "
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

    def generate(
        self,
        system_prompt,
        user_prompt,
        on_token: Callable[[str], None] | None = None,
    ):
        """
        System ve user prompt'larini kullanarak
        streaming cevap uretir.

        on_token verilirse her yeni cevap parcasi
        bu fonksiyona gonderilir.
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

            answer_parts.append(content)

            if on_token is not None:
                on_token(content)

        answer = "".join(
            answer_parts
        ).strip()

        if not answer:
            raise RuntimeError(
                "Yerel chat modeli bos cevap "
                "uretti."
            )

        return answer

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