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


### Day 13 — Interactive Command-Line Interface

The project now includes an interactive command-line interface for asking multiple questions about local documents.

The CLI:

1. Checks whether the SQLite knowledge base contains document chunks
2. Repeatedly accepts user questions
3. Calls the reusable `answer_question()` service
4. Streams the local LLM answer to the terminal
5. Displays the actual retrieved sources
6. Shows the selected model and retrieved chunk count
7. Continues running after recoverable errors
8. Exits cleanly with `exit`, `quit`, `q`, or Turkish exit commands

New module:

- `src/cli.py` — interactive terminal interface

Updated module:

- `src/main.py` — starts the CLI as the main application entry point

The CLI uses:

- Embedding model: `qwen3-embedding-0.6b`
- Chat model: `phi-4-mini`
- SQLite-backed local knowledge base
- Reusable RAG service layer


### Day 14 — Retrieval Safety and Similarity Threshold

The project now checks whether the local knowledge base contains sufficiently relevant information before loading the chat model.

The retrieval safety flow:

1. Generates an embedding for the user question
2. Retrieves the top candidate chunks from SQLite
3. Reads the highest cosine similarity score
4. Compares the highest score with a minimum threshold
5. Generates an answer only when sufficient context exists
6. Returns a safe fallback when the context is insufficient

Current configuration:

- Minimum similarity threshold: `0.60`
- Fallback answer: `Bu bilgi verilen dokumanlarda bulunmuyor.`

When the highest similarity score is below the threshold:

- The local chat model is not loaded
- No document source is presented as supporting evidence
- The service returns `insufficient_context`

When the highest score reaches the threshold:

- All top-k candidate chunks are preserved as context
- The local chat model generates a grounded answer
- Actual retrieval sources are displayed

New module:

- `src/retrieval_safety_demo.py` — tests answerable and unanswerable questions

Updated modules:

- `src/retrieval.py` — defines the default similarity threshold
- `src/rag_service.py` — applies question-level retrieval safety
- `src/cli.py` — displays answer status, scores, and model usage


### Day 15 — Systematic Retrieval Evaluation

The retrieval safety layer was evaluated with a structured test dataset.

Evaluation dataset:

- 8 answerable questions
- 4 unanswerable questions
- 2 diagnostic borderline questions
- 14 total questions
- 12 questions included in strict accuracy metrics

The evaluation measures:

- Expected and predicted answer status
- Highest cosine similarity score
- Top retrieved source
- Source correctness
- False positives
- False negatives
- Input validation behavior

Results:

- Overall accuracy: `100%`
- Status decision accuracy: `100%`
- Top-source accuracy: `100%`
- True positives: `8`
- True negatives: `4`
- False positives: `0`
- False negatives: `0`

Current threshold:

- Minimum similarity score: `0.60`

Observed score range:

- Lowest supported-question score: `0.6203`
- Highest unsupported-question score: `0.3312`

The `0.60` threshold was retained because it correctly separated all strict supported and unsupported questions in the current evaluation dataset.

New files:

- `data/evaluation_questions.json` — structured retrieval test dataset
- `src/evaluation.py` — evaluation and metric calculation logic
- `src/evaluation_demo.py` — terminal evaluation report


### Day 16 — Persistent Evaluation Reporting

The project now saves retrieval evaluation results as a version-controlled JSON report.

The reporting pipeline:

1. Loads the structured evaluation dataset
2. Runs all retrieval test cases
3. Calculates accuracy and decision metrics
4. Analyzes supported and unsupported score ranges
5. Separates failed and diagnostic cases
6. Saves the results as a structured JSON report
7. Reads the saved report back for validation
8. Compares the new metrics with the previous report

New files:

- `src/evaluation_report.py` — builds, saves, loads, and compares reports
- `src/evaluation_report_demo.py` — runs evaluation and generates the report
- `reports/evaluation_report.json` — latest version-controlled evaluation result

The report includes:

- Schema version
- UTC generation timestamp
- Embedding model
- Top-k configuration
- Minimum similarity threshold
- Accuracy metrics
- False-positive and false-negative counts
- Score separation analysis
- Failed cases
- Diagnostic borderline cases
- Individual test-case results

Latest result:

- Total cases: `14`
- Strict cases: `12`
- Passed cases: `12`
- Overall accuracy: `100%`
- False positives: `0`
- False negatives: `0`
- Score separation margin: `0.289075`


### Day 17 — Generation Evaluation and Hybrid Source Ranking

The project now evaluates final answer quality in addition to raw retrieval accuracy.

Generation evaluation checks:

- Expected answer status
- Correct source usage
- Required concept coverage
- Answer length
- Local chat model usage
- Safe fallback behavior
- Unexpected fallback text
- Empty source behavior for unsupported questions

Generation evaluation dataset:

- 4 answerable questions
- 1 unanswerable question
- 5 total cases

Latest generation result:

- Passed cases: `5`
- Failed cases: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- Concept accuracy: `100%`
- Length accuracy: `100%`
- Clean-answer accuracy: `100%`
- Fallback accuracy: `100%`

The retrieval pipeline now uses hybrid source ranking.

Updated flow:

1. Retrieve a wider pool of candidate chunks
2. Check the highest semantic score against the safety threshold
3. Group candidate chunks by source
4. Calculate lexical query coverage for each source
5. Combine semantic similarity with lexical coverage
6. Select the highest-ranked source
7. Send only the best chunks from that source to the chat model

Current configuration:

- Context top-k: `3`
- Retrieval candidate multiplier: `3`
- Default candidate pool: `9`
- Minimum similarity threshold: `0.60`
- Lexical ranking weight: `0.05`

Source-selection formula:

    selection_score =
        semantic_score +
        lexical_weight * lexical_coverage

This fixed a regression where a SQLite question ranked a general RAG chunk slightly above the correct SQLite document.

Before hybrid source ranking:

- Semantic top source: `rag_notes.txt`
- Primary source: `rag_notes.txt`
- Generated answer used incorrect context

After hybrid source ranking:

- Semantic top source: `rag_notes.txt`
- Hybrid primary source: `sqlite_notes.txt`
- Selected context contains only SQLite chunks
- Generated answer correctly describes the information stored by SQLite

Final retrieval regression result:

- Strict cases: `12`
- Passed cases: `12`
- Overall accuracy: `100%`
- Source accuracy: `100%`
- False positives: `0`
- False negatives: `0`

New files:

- `data/generation_evaluation_questions.json`
- `src/generation_evaluation.py`
- `src/generation_evaluation_demo.py`
- `reports/generation_evaluation_report.json`

Updated files:

- `src/retrieval.py`
- `src/rag_service.py`
- `src/evaluation.py`
- `src/context_builder.py`
- `data/documents/sqlite_notes.txt`

Limitation:

Automated keyword and structural checks cannot fully measure grammar, fluency, natural expression, or subtle factual quality. Generated answers still require human review.


### Day 18 — Performance Measurement and Persistent Model Sessions

The project now measures the execution time of each major RAG pipeline stage.

Measured stages include:

- SQLite document loading
- Embedding model loading
- Query embedding generation
- Embedding model unloading
- Cosine similarity calculation and ranking
- Hybrid source ranking
- Context selection
- Prompt construction
- Chat model loading
- Answer generation
- Chat model unloading
- Total service time

Three repeated benchmark cases were used:

- Answerable SQLite question
- Answerable Foundry Local question
- Unsupported Jupiter question

Each case was executed three times.

## Stateless performance baseline

Baseline benchmark results:

- Total runs: `9`
- Passed runs: `9`
- Correctness rate: `100%`
- Answerable median latency: `25.2748 seconds`
- Unsupported median latency: `3.0760 seconds`

Main service bottlenecks:

1. Answer generation
2. Chat model loading
3. Retrieval

Main retrieval bottleneck:

- Embedding model loading

Stateless answerable-stage median values:

- Answer generation: `11.8997 seconds`
- Chat model loading: `8.6434 seconds`
- Retrieval: `2.4662 seconds`

Retrieval-stage median values:

- Embedding model loading: `2.1602 seconds`
- Query embedding generation: `0.5750 seconds`
- Embedding model unloading: `0.0940 seconds`
- SQLite reading: `0.0086 seconds`
- Similarity ranking: `0.0053 seconds`

## Persistent RAG session

A new `LocalRAGSession` class keeps local models available across multiple questions.

Session behavior:

1. The embedding model is loaded once when the session starts.
2. The same embedding model is reused for every question.
3. The chat model is loaded lazily on the first answerable question.
4. The loaded chat model is reused for later answerable questions.
5. Unsupported questions do not invoke the chat model.
6. Both models are safely unloaded when the session closes.

The existing stateless `answer_question()` interface remains supported.

This allows two execution modes:

    Stateless usage:
        answer_question(question)

    Persistent usage:
        with LocalRAGSession() as session:
            session.answer_question(question)

## Optimized persistent-session result

Persistent benchmark results:

- Total measured runs: `9`
- Passed runs: `9`
- Correctness rate: `100%`
- Model reuse checks: passed

Answerable questions:

- Baseline median: `25.2748 seconds`
- Optimized median: `13.6945 seconds`
- Saved time: `11.5803 seconds`
- Improvement: `45.82%`
- Speedup: `1.85x`

Unsupported questions:

- Baseline median: `3.0760 seconds`
- Optimized median: `0.6877 seconds`
- Saved time: `2.3883 seconds`
- Improvement: `77.64%`
- Speedup: `4.47x`

Warm case medians:

- SQLite question: `11.9033 seconds`
- Foundry Local question: `15.4109 seconds`
- Unsupported question: `0.6877 seconds`

First-user experience:

- Session startup: `3.9259 seconds`
- First answer service time: `18.9104 seconds`
- Startup plus first answer: `22.8364 seconds`

The main warm-request bottleneck is now answer generation rather than model loading.

## Performance reports

The project stores three performance reports:

- `reports/performance_report.json`
  - Original stateless benchmark output
- `reports/performance_baseline.json`
  - Fixed reference copy of the pre-optimization result
- `reports/performance_optimized.json`
  - Persistent-session benchmark result

## New files

- `src/rag_session.py`
- `src/performance.py`
- `src/performance_demo.py`
- `src/session_performance.py`
- `src/session_performance_demo.py`
- `reports/performance_report.json`
- `reports/performance_baseline.json`
- `reports/performance_optimized.json`

## Updated files

- `src/embedder.py`
- `src/generator.py`
- `src/retrieval.py`
- `src/rag_service.py`
- `src/cli.py`

## Running the benchmarks

Run the stateless benchmark:

    python -m src.performance_demo

Run the persistent-session benchmark:

    python -m src.session_performance_demo

Run the optimized interactive CLI:

    python -m src.main