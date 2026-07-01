from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    print("Foundry Local test baslatiliyor...")

    FoundryLocalManager.initialize(
        Configuration(app_name="foundry-local-rag-assistant")
    )
    manager = FoundryLocalManager.instance

    print("Model bilgisi aliniyor...")
    model = manager.catalog.get_model("qwen2.5-0.5b")

    print("Model indiriliyor veya cache kontrol ediliyor...")
    model.download(
        lambda progress: print(
            f"\rDownloading {progress:.0f}%",
            end="",
            flush=True
        )
    )

    print("\nModel yukleniyor...")
    model.load()

    client = model.get_chat_client()

    print("Modele test sorusu soruluyor...\n")

    messages = [
        {
            "role": "user",
            "content": "Explain in one short sentence what an on-device AI model is."
        }
    ]

    for chunk in client.complete_streaming_chat(messages):
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)

    print("\n\nModel kapatiliyor...")
    model.unload()

    print("Foundry Local testi tamamlandi.")


if __name__ == "__main__":
    main()