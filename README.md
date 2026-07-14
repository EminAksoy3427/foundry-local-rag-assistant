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

Run the SQLite ingestion demo:

```powershell
python -m src.ingest_demo

### Day 9 — Semantic Retrieval Pipeline

The project can now retrieve the most relevant document chunks for a user query.

The retrieval pipeline:

1. Loads stored document chunks and embeddings from SQLite
2. Converts the JSON embedding strings back into Python lists
3. Generates an embedding for the user query with Microsoft Foundry Local
4. Calculates cosine similarity between the query and every stored chunk
5. Sorts the chunks by similarity score
6. Returns the top matching chunks

New modules:

- `src/retrieval.py` — implements semantic retrieval and cosine similarity
- `src/retrieval_demo.py` — tests retrieval and displays ranked results

Current test result:

- Stored chunks: 16
- Query: `How does RAG make answers more reliable?`
- Top result: `rag_notes.txt`
- Top similarity score: `0.8245`
- Returned chunks: 3


### Day 10 — Context and Prompt Builder

The project can now transform retrieved document chunks into structured context and prompts for a local language model.

The prompt-building pipeline:

1. Retrieves the top matching chunks for a user question
2. Validates the retrieved chunk structure
3. Formats each chunk with its source file and chunk index
4. Combines the chunks into a structured context
5. Creates a system prompt with grounding rules
6. Creates a user prompt containing both the context and the question

New modules:

- `src/context_builder.py` — builds structured RAG context and prompts
- `src/context_builder_demo.py` — displays retrieval results, context, and prompts

The system prompt instructs the model to:

- Use only the supplied context
- Avoid unsupported claims
- State clearly when the context is insufficient
- Answer in the same language as the user
- Include document and chunk references


### Day 11 — Local RAG Answer Generation

The project can now generate document-grounded answers with a local language model.

The complete RAG pipeline:

1. Receives a user question
2. Generates a query embedding with Microsoft Foundry Local
3. Retrieves the top matching chunks from SQLite
4. Builds structured context and prompts
5. Sends the context and question to a local chat model
6. Streams and collects the generated answer
7. Displays the actual retrieved sources

New modules:

- `src/foundry_manager.py` — provides a shared Foundry Local manager instance
- `src/generator.py` — manages the local chat model and streaming generation
- `src/generation_demo.py` — runs the end-to-end RAG generation pipeline

Updated modules:

- `src/embedder.py` — reuses the shared Foundry Local manager
- `src/context_builder.py` — uses a simpler grounded prompt and creates deterministic source references

Model evaluation:

- `qwen2.5-0.5b` was too small for reliable Turkish RAG answers
- `qwen2.5-1.5b` did not follow the supplied context reliably
- `phi-3.5-mini` produced unclear answers
- `phi-4-mini` produced the best grounded response and became the default model

Current models:

- Embedding model: `qwen3-embedding-0.6b`
- Chat model: `phi-4-mini`


### Day 12 — Reusable RAG Service Layer

The project now exposes the complete local RAG workflow through a reusable service function.

The main service function:

    answer_question(question, top_k=3, on_token=None)

The service:

1. Validates the user question
2. Retrieves the most relevant chunks from SQLite
3. Builds the grounded context and prompts
4. Loads the local chat model
5. Generates a streaming answer
6. Unloads the model safely
7. Returns a structured result

The returned result includes:

- Original question
- Generated answer
- Retrieved chunks
- Deterministic source references
- Local chat model alias

New modules:

- `src/rag_service.py` — contains the reusable end-to-end RAG service
- `src/rag_service_demo.py` — demonstrates and validates the service output

This service layer separates the RAG business logic from the user interface. Future interfaces can call one function without directly managing retrieval, prompts, or model lifecycle.