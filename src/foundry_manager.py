from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.exception import FoundryLocalException


APP_NAME = "foundry-local-rag-assistant"


def get_foundry_manager():
    """
    FoundryLocalManager singleton nesnesini dondurur.

    Manager daha once baslatilmadiysa initialize eder.
    Daha once baslatildiysa mevcut instance'i yeniden kullanir.
    """
    try:
        manager = FoundryLocalManager.instance
    except FoundryLocalException:
        manager = None

    if manager is None:
        FoundryLocalManager.initialize(
            Configuration(app_name=APP_NAME)
        )
        manager = FoundryLocalManager.instance

    return manager