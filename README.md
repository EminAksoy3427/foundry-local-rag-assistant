# Foundry Local RAG Assistant

Bu proje, Microsoft Foundry Local kullanarak yerel çalışan bir RAG tabanlı doküman soru-cevap asistanı geliştirmeyi amaçlar.

## Proje Amacı

Kullanıcı bir soru sorduğunda sistem:

1. Yerel dokümanlar içinden ilgili parçaları bulur.
2. Bu parçaları modele bağlam olarak verir.
3. Foundry Local üzerinde çalışan yerel LLM ile cevap üretir.

## Kullanılacak Teknolojiler

- Python
- Microsoft Foundry Local
- Embeddings
- Vector Search
- SQLite
- Git / GitHub

## Planlanan Mimari

```text
User Question
     ↓
Embedding
     ↓
Vector Search
     ↓
Relevant Document Chunks
     ↓
Prompt + Context
     ↓
Foundry Local LLM
     ↓
Answer


## Proje Durumu

- [x] GitHub repository oluşturuldu
- [x] Python .gitignore eklendi
- [x] MIT License eklendi
- [x] Proje klasör yapısı hazırlandı
- [x] İlk Python dosyası oluşturuldu
- [x] Python sanal ortam kurulumu
- [x] Foundry Local SDK kurulumu
- [x] Basit Foundry Local model testi
- [x] Embedding denemesi
- [x] SQLite veritabanı
- [x] Doküman seti ve dosya okuma
- [x] Chunking
- [x] Chunk embedding üretimi
- [ ] SQLite ingestion pipeline
- [ ] Retrieval pipeline
- [ ] LLM entegrasyonu
- [ ] CLI arayüz


## Embedding Demo

```powershell
python src\embedding_demo.py
```

Bu demo, örnek dokümanları ve kullanıcı sorusunu embedding vektörlerine çevirir. Ardından cosine similarity ile en alakalı dokümanı bulur.

## SQLite Demo

```powershell
python src\sqlite_demo.py
```

Bu demo, `storage/rag.db` dosyasını oluşturur ve örnek doküman parçalarını `documents` tablosuna kaydeder.

Not: `storage/rag.db` otomatik üretilen bir dosyadır ve GitHub'a yüklenmez.

## Document Loader Demo

```powershell
python src\document_loader_demo.py
```

Bu demo, `data/documents` klasöründeki `.txt` dosyalarını okur ve her dokümanın kaynak adını, karakter sayısını, kelime sayısını ve kısa ön izlemesini gösterir.

## Chunking Demo

```powershell
python src\chunking_demo.py
```

Bu demo, `data/documents` klasöründeki `.txt` dokümanları okur ve her dokümanı paragraflara göre küçük chunk'lara böler.

Her chunk şu bilgileri içerir:

- source
- chunk_index
- chunk_text


## Chunk Embedding Demo

```powershell
python src\chunk_embedding_demo.py
```

Bu demo, `data/documents` klasöründeki dokümanları okur, chunk'lara böler ve her chunk için Foundry Local embedding modeliyle embedding vektörü üretir.

Her embedded chunk şu bilgileri içerir:

- source
- chunk_index
- chunk_text
- embedding

Bu projede ana embedding modeli olarak `qwen3-embedding-0.6b` kullanılmaktadır.