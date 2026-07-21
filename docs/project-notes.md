# Project Notes

## Gun 1 - Proje Baslangici

Bugun GitHub uzerinde proje reposu olusturuldu ve yerel gelistirme ortami hazirlandi.

## Proje Amaci

Bu projenin amaci, Microsoft Foundry Local kullanarak yerelde calisan bir RAG tabanli dokuman soru-cevap asistani gelistirmektir.

## RAG Mantigi

RAG = Retrieve + Augment + Generate

- Retrieve: Kullanici sorusuyla ilgili dokuman parcalarini bul.
- Augment: Bulunan parcalari modele context olarak ver.
- Generate: Modelden bu context'e dayali cevap uret.

## Genel Akis

1. Kullanici soru sorar.
2. Soru embedding'e cevrilir.
3. SQLite icindeki dokuman embedding'leriyle karsilastirilir.
4. En alakali dokuman parcalari secilir.
5. Bu parcalar prompt'a eklenir.
6. Foundry Local uzerindeki model cevap uretir.
7. Cevap kullaniciya gosterilir.

## Gun 1 Ciktisi

- Repository hazir.
- Proje klasor yapisi olustu.
- Ilk Python dosyasi yazildi.
- README eklendi.

## Gun 2 - Python Ortami ve Foundry Local Testi

Bugun projeye ozel Python sanal ortami olusturuldu ve Foundry Local SDK ile basit bir model testi yapildi.

Bu adimin amaci, ileride RAG pipeline'inin Generate asamasinda kullanacagimiz yerel LLM'in bilgisayarda calistigini dogrulamaktir.

Test akisi:

1. Foundry Local baslatildi.
2. Model bilgisi alindi.
3. Model indirildi veya cache'den kontrol edildi.
4. Model yuklendi.
5. Modele basit bir soru soruldu.
6. Model cevap uretti.
7. Model kapatildi.

Sonuc:

Foundry Local testi basariyla tamamlandi.


## Gun 3 - Embedding ve Benzerlik Aramasi

Bugun RAG sisteminin Retrieve asamasinin temel mantigi ogrenildi.

Embedding, bir metni sayisal vektore cevirmektir. Bu sayede bilgisayar iki metnin anlamca birbirine yakin olup olmadigini hesaplayabilir.

Bugun yapilan demo:

1. Ornek dokumanlar belirlendi.
2. Her dokuman embedding'e cevrildi.
3. Kullanici sorusu embedding'e cevrildi.
4. Soru embedding'i ile dokuman embedding'leri cosine similarity ile karsilastirildi.
5. En yuksek skora sahip dokuman en alakali sonuc olarak secildi.

Sonuc:

Sistem, "How does RAG make answers more reliable?" sorusu icin en alakali dokuman olarak RAG'in hallucination'i azalttigini anlatan dokumani secti.

Gun 3 ciktisi:

- src/embedding_demo.py eklendi.
- Foundry Local embedding modeli test edildi.
- Cosine similarity fonksiyonu yazildi.
- Soruya en alakali dokumani bulma mantigi calisti.

## Gun 4 - SQLite Veritabani

Bugun RAG projesinin yerel veri katmani icin SQLite kullanildi.

SQLite'in projedeki gorevi:

- Dokuman parcalarini saklamak
- Her parcanin kaynak dosya adini tutmak
- Ileride embedding vektorlerini saklamak
- Retrieval asamasinda kayitlari tekrar okumak

Olusturulan tablo:

documents

Alanlar:

- id: Otomatik benzersiz kayit numarasi
- source: Dokumanin geldigi kaynak dosya
- chunk_index: Dokuman icindeki parca sirasi
- chunk_text: Asil dokuman parcasi
- embedding: Ileride embedding vektorunun saklanacagi alan
- created_at: Kayit tarihi

Bugun yapilan demo:

1. storage/rag.db olusturuldu.
2. documents tablosu kuruldu.
3. Ornek dokuman parcalari tabloya eklendi.
4. Kayitlar SQLite'tan tekrar okundu.

Gun 4 ciktisi:

- src/db.py eklendi.
- src/sqlite_demo.py eklendi.
- SQLite ile veri yazma ve okuma test edildi.

## Gun 5 - Dokuman Seti ve Dosya Okuma

Bugun RAG projesi icin ilk gercek dokuman seti hazirlandi.

Eklenen dokumanlar:

- rag_notes.txt
- foundry_local_notes.txt
- sqlite_notes.txt
- project_overview.txt

Bu adimin amaci, dokumanlari artik Python listesi icinde degil, gercek dosyalar olarak saklamaktir.

Document loader'in gorevi:

1. data/documents klasorunu bulmak
2. .txt dosyalarini okumak
3. Her dokumani source ve text bilgisiyle listelemek
4. Ileride chunking ve embedding islemlerine veri saglamak

Neden source bilgisi tutuyoruz?

Cunku RAG sisteminde cevap verirken bilginin hangi dokumandan geldigini bilmek isteriz. Ileride kaynak gostermek icin source alani onemli olacak.

Gun 5 ciktisi:

- data/documents icine ornek .txt dokumanlar eklendi.
- src/document_loader.py eklendi.
- src/document_loader_demo.py eklendi.
- Python ile dokuman okuma test edildi.


## Gun 6 - Chunking

Bugun dokumanlari kucuk parcalara bolme mantigi ogrenildi.

Chunking, uzun dokumanlari daha kucuk ve aranabilir parcalara ayirma islemidir.

Neden chunking kullaniyoruz?

- Uzun dokumanin tamamini modele vermek verimsizdir.
- Kullanici sorusu genellikle dokumanin kucuk bir bolumuyle ilgilidir.
- Embedding aramasinda kucuk ve net parcalar daha iyi sonuc verir.
- Ileride cevaplarda kaynak gostermek daha kolay olur.

Bugun yapilanlar:

1. data/documents icindeki dokumanlar okundu.
2. Her dokuman paragraflara ayrildi.
3. Her paragraf bir chunk olarak hazirlandi.
4. Her chunk icin source, chunk_index ve chunk_text bilgileri olusturuldu.

Gun 6 ciktisi:

- src/chunker.py eklendi.
- src/chunking_demo.py eklendi.
- Dokumanlari chunk'lara bolme demosu calisti.

## Gun 7 - Chunk Embedding Uretimi

Bugun gercek dokuman chunk'lari icin embedding uretildi.

Onceki gunlerde yapilanlar:

- Gun 5: Dokumanlar data/documents klasorunden okundu.
- Gun 6: Dokumanlar chunk'lara bolundu.
- Gun 7: Her chunk embedding vektorune cevrildi.

Bu adimin amaci, RAG sisteminin retrieval asamasinda kullanacagi sayisal temsilleri hazirlamaktir.

Embedding neden gerekli?

Bilgisayar metinlerin anlamca yakin olup olmadigini dogrudan anlayamaz. Embedding, metinleri sayisal vektor haline getirir. Daha sonra kullanici sorusunun embedding'i ile dokuman chunk embedding'leri karsilastirilerek en alakali chunk'lar bulunur.

Bugun yapilanlar:

1. src/embedder.py eklendi.
2. Foundry Local embedding modeli ayri bir yardimci sinif icinde kullanildi.
3. Dokumanlar okundu.
4. Dokumanlar chunk'lara bolundu.
5. Her chunk icin embedding uretildi.
6. Embedding boyutu kontrol edildi.
7. Model alias problemi cozuldu. Calisan ana alias: qwen3-embedding-0.6b

Gun 7 sonuc:

- 4 dokuman okundu.
- 16 chunk uretildi.
- 16 chunk icin embedding uretildi.
- Her embedding'in boyutu 1024 olarak dogrulandi.

Gun 7 ciktisi:

- src/embedder.py eklendi.
- src/chunk_embedding_demo.py eklendi.
- Gercek dokuman chunk'lari icin embedding uretimi test edildi.


## Day 8 — SQLite Ingestion Pipeline

### Goal

Combine the document loader, chunker, embedding model, and SQLite database into a complete ingestion pipeline.

### What was implemented

- Added `insert_documents()` to `src/db.py`
- Used `executemany()` to insert multiple chunks with one database transaction
- Added `src/ingest.py`
- Added `src/ingest_demo.py`
- Loaded real text documents from `data/documents/`
- Split the documents into paragraph-based chunks
- Generated a local embedding for every chunk
- Converted embedding vectors into JSON strings
- Stored chunk metadata, text, and embeddings in SQLite
- Read the records back from SQLite
- Verified that the number of stored records matched the generated chunk count
- Verified that a stored embedding could be restored with `json.loads()`

### Test result

- Documents loaded: 4
- Chunks generated: 16
- Records inserted: 16
- Records read from SQLite: 16
- Embedding dimensions: 1024

### Key learning

An ingestion pipeline prepares raw documents for retrieval. It transforms documents into searchable chunks and persists their vector representations so embeddings do not need to be recomputed for every user question.

Embedding vectors are stored as JSON text because the current SQLite schema uses a `TEXT` column. During retrieval, the JSON string can be converted back into a Python list using `json.loads()`.

The database is reset only after embedding generation succeeds. This prevents an embedding error from deleting the previously working database unnecessarily.

### Next step

Implement semantic retrieval by embedding a user query, loading stored embeddings from SQLite, calculating cosine similarity, and returning the top matching chunks.


## Day 9 — Semantic Retrieval Pipeline

### Goal

Implement semantic search over the document chunks and embeddings stored in SQLite.

### What was implemented

- Added `src/retrieval.py`
- Added `src/retrieval_demo.py`
- Implemented JSON embedding deserialization
- Implemented cosine similarity calculation
- Generated an embedding for the user query
- Loaded all stored chunks and embeddings from SQLite
- Compared the query embedding with every stored embedding
- Ranked document chunks by similarity score
- Returned the top matching chunks with source information
- Added validation for empty queries, invalid `top_k` values, missing documents, and incompatible embedding dimensions

### Test result

- Stored chunks: 16
- Query: `How does RAG make answers more reliable?`
- Top result source: `rag_notes.txt`
- Top similarity score: `0.8245`
- Returned chunks: 3

### Key learning

Semantic retrieval compares the meaning of texts rather than relying only on exact keyword matches.

The document embeddings are generated once during ingestion and stored in SQLite. For each new user question, only the query embedding needs to be generated.

For the current small document collection, loading all embeddings and calculating cosine similarity in Python is sufficient. A larger production system would normally use a specialized vector database or a vector search extension.

Retrieval always returns the highest-scoring chunks, even when the query is unrelated to the knowledge base. A future improvement can introduce a minimum similarity threshold so weak results can be rejected.

### Next step

Combine retrieved chunks into a structured context that can be passed to the local language model.


## Day 10 — Context and Prompt Builder

### Goal

Convert semantic retrieval results into structured context and prompts that can later be sent to a local language model.

### What was implemented

- Added `src/context_builder.py`
- Added `src/context_builder_demo.py`
- Added validation for retrieved chunks
- Built source-aware context sections
- Included document filenames and chunk indices
- Created a reusable system prompt
- Created a user prompt containing the context and question
- Kept similarity scores out of the LLM context
- Added validation for empty questions and empty context
- Verified the complete retrieval-to-prompt flow

### Prompt structure

The context includes:

- Source file
- Chunk index
- Chunk text

The system prompt instructs the model to:

- Answer only from the supplied context
- Avoid guessing or inventing information
- Clearly state when the answer is not available
- Respond in the user's language
- Cite sources using file and chunk information

### Test result

Query:

`RAG cevaplari nasil daha guvenilir hale getirir?`

Retrieved chunks:

- `rag_notes.txt` — Chunk 1
- `rag_notes.txt` — Chunk 2
- `rag_notes.txt` — Chunk 4

The generated user prompt successfully contained the complete structured context and the original user question.

### Key learning

Retrieval and generation are separate responsibilities.

The retrieval layer decides which information is relevant. The prompt-building layer decides how that information should be presented to the language model.

A well-structured context helps the model distinguish source metadata, document content, and the user question.

Similarity scores are useful for debugging and ranking, but they are not part of the knowledge itself and therefore do not need to be included in the model prompt.

### Next step

Load a local chat model with Microsoft Foundry Local and generate an answer using the system prompt, retrieved context, and user question.


## Day 11 — Local RAG Answer Generation

### Goal

Connect semantic retrieval and prompt building to a local chat model and generate the first complete document-grounded RAG answer.

### What was implemented

- Added `src/foundry_manager.py`
- Added a shared `FoundryLocalManager` singleton accessor
- Updated `src/embedder.py` to reuse the shared manager
- Added `src/generator.py`
- Added `src/generation_demo.py`
- Loaded a local chat model through Microsoft Foundry Local
- Implemented streaming chat generation
- Safely ignored streaming chunks with empty `choices`
- Collected streamed answer fragments into one final answer
- Added empty prompt and empty response validation
- Simplified the RAG system and user prompts
- Added deterministic source references from retrieval results
- Completed the first end-to-end local RAG generation test

### Singleton issue

The first end-to-end attempt failed because both the embedding and generation layers called `FoundryLocalManager.initialize()` in the same Python process.

Foundry Local uses a singleton manager. Unloading an individual model does not reset the manager.

A shared `get_foundry_manager()` function was added so all AI components reuse the same initialized manager instance.

### Model evaluation

The following chat models were tested:

- `qwen2.5-0.5b`
  - Fast and lightweight
  - Produced repetitive and incorrect Turkish answers
- `qwen2.5-1.5b`
  - Produced more structured text
  - Did not reliably follow the supplied context
- `phi-3.5-mini`
  - Recognized the source context
  - Produced unclear and incomplete answers
- `phi-4-mini`
  - Produced the most coherent grounded answer
  - Followed the context more reliably
  - Selected as the default chat model

### Final configuration

- Embedding model: `qwen3-embedding-0.6b`
- Chat model: `phi-4-mini`
- Temperature: `0.0`
- Maximum output tokens: `220`
- Retrieved chunks: `3`

### Test query

`RAG cevaplari nasil daha guvenilir hale getirir?`

### Test result

The system:

- Retrieved three chunks from `rag_notes.txt`
- Built a structured context
- Generated a local answer with `phi-4-mini`
- Displayed the real retrieval sources
- Unloaded the chat model successfully

### Key learning

A technically working model is not automatically suitable for a specific application.

Model selection must consider:

- Language quality
- Instruction following
- Context grounding
- Output length
- Device performance

Source citations are more reliable when generated by the application from actual retrieval results instead of relying entirely on the language model.

### Next step

Create a reusable RAG service function that accepts a question and returns the generated answer, retrieved chunks, and source references. This service will later be used by the command-line interface.


## Day 12 — Reusable RAG Service Layer

### Goal

Combine retrieval, prompt building, and local answer generation behind one reusable service function.

### What was implemented

- Added `src/rag_service.py`
- Added `src/rag_service_demo.py`
- Added the reusable `answer_question()` function
- Added validation for empty questions
- Added validation for invalid `top_k` values
- Connected semantic retrieval to prompt building
- Connected the generated prompts to the local chat model
- Preserved streaming output through an optional callback
- Returned the generated answer as structured data
- Returned actual retrieval results and source references
- Returned the selected local model alias
- Ensured that the chat model is unloaded with `finally`
- Improved terminal formatting after streaming output

### Service result structure

The service returns:

- `question`
- `answer`
- `source_references`
- `retrieved_chunks`
- `model_alias`

### Test result

Test question:

`RAG cevaplari nasil daha guvenilir hale getirir?`

Result:

- Model: `phi-4-mini`
- Retrieved chunks: 3
- Source references: 3
- Top source: `rag_notes.txt`
- Generated answer length: 246 characters
- Local model unloaded successfully

### Key learning

The service layer separates application logic from presentation logic.

The service is responsible for:

- Retrieval
- Prompt preparation
- Model lifecycle
- Answer generation
- Structured results

The interface is responsible for:

- Reading user input
- Displaying the streamed answer
- Displaying sources and metadata

This separation avoids duplicating the RAG pipeline when adding a CLI, web interface, or automated tests.

### Next step

Build an interactive command-line interface that repeatedly accepts user questions and calls `answer_question()`.


## Day 13 — Interactive Command-Line Interface

### Goal

Build an interactive terminal interface that repeatedly accepts user questions and uses the reusable RAG service.

### What was implemented

- Added `src/cli.py`
- Updated `src/main.py` as the application entry point
- Added a startup welcome message
- Added a SQLite readiness check
- Added repeated user input through a CLI loop
- Connected the CLI to `answer_question()`
- Added streaming answer display
- Added deterministic source display
- Added model and retrieval metadata
- Added empty input validation
- Added exit commands
- Added graceful handling for `Ctrl+C` and end-of-file input
- Added recoverable error handling so one failed question does not close the application

### Supported exit commands

- `exit`
- `quit`
- `q`
- `cikis`
- `çıkış`

### Test result

Question:

`Foundry Local ne ise yarar?`

Generated answer:

`Foundry Local, yapay zeka modellerini kullanicinin kendi cihazinda calistirmayi saglayan bir Microsoft aracidir.`

Retrieved sources:

- `foundry_local_notes.txt` — Chunk 3
- `foundry_local_notes.txt` — Chunk 2
- `foundry_local_notes.txt` — Chunk 1

Configuration:

- SQLite records: 16
- Chat model: `phi-4-mini`
- Retrieved chunks: 3

The application exited successfully with the `q` command.

### Key learning

The user interface should not contain the complete RAG implementation.

The CLI is responsible for:

- Reading input
- Displaying answers
- Displaying sources
- Handling user interaction

The RAG service remains responsible for:

- Retrieval
- Prompt construction
- Model lifecycle
- Answer generation

This separation allows the same service to be reused later by a web interface or automated tests.

### Next step

Improve retrieval safety by adding a minimum similarity threshold and handling questions that are not answered by the local document collection.


## Day 14 — Retrieval Safety and Similarity Threshold

### Goal

Prevent the assistant from generating unsupported answers when the local document collection does not contain sufficiently relevant information.

### What was implemented

- Added `DEFAULT_MIN_SIMILARITY_SCORE`
- Selected an initial experimental threshold of `0.60`
- Added question-level retrieval safety to `answer_question()`
- Added the `answered` and `insufficient_context` result statuses
- Added a deterministic fallback answer
- Prevented the chat model from loading when context is insufficient
- Preserved all top-k candidate chunks when the highest score passes the threshold
- Added candidate chunk information to the service result
- Added highest similarity score and threshold metadata
- Updated the CLI to display retrieval safety information
- Added `src/retrieval_safety_demo.py`
- Tested one answerable and one unanswerable question

### Safety decision

The threshold is applied to the highest retrieval score at the question level.

If the highest score is below the threshold:

- The question is treated as unsupported
- No chunks are used as context
- The chat model is not loaded
- The fallback answer is returned

If the highest score reaches the threshold:

- The question is treated as answerable
- All top-k candidate chunks are retained as context

This approach preserves useful supporting chunks even when their individual scores are slightly below the threshold.

### Test 1 — Unsupported question

Question:

`Jupiter'in kac uydusu vardir?`

Result:

- Highest similarity score: `0.3262`
- Minimum threshold: `0.6000`
- Status: `insufficient_context`
- Chat model: not loaded
- Used chunks: `0`
- Sources: none
- Answer: `Bu bilgi verilen dokumanlarda bulunmuyor.`

### Test 2 — Supported question

Question:

`Foundry Local ne ise yarar?`

Result:

- Highest similarity score: `0.6592`
- Minimum threshold: `0.6000`
- Status: `answered`
- Chat model: `phi-4-mini`
- Candidate chunks: `3`
- Used chunks: `3`
- Sources: three chunks from `foundry_local_notes.txt`

### Key learning

Top-k retrieval always returns results, even for unrelated questions. Therefore, the presence of retrieved chunks alone does not prove that the knowledge base contains the answer.

A similarity threshold provides a basic safety gate before generation.

The current `0.60` value is experimental and should later be evaluated with a larger set of supported and unsupported questions.

### Next step

Create a structured evaluation set containing answerable, unanswerable, and edge-case questions, then measure retrieval and fallback behavior systematically.



## Day 15 — Systematic Retrieval Evaluation

### Goal

Evaluate the retrieval safety threshold with a structured set of answerable, unanswerable, and borderline questions.

### What was implemented

- Added `data/evaluation_questions.json`
- Added `src/evaluation.py`
- Added `src/evaluation_demo.py`
- Added validation for the evaluation dataset
- Loaded the embedding model once for all evaluation questions
- Evaluated retrieval without running the chat model
- Compared predicted statuses with expected statuses
- Checked whether the top source matched the expected document
- Calculated overall, status, and source accuracy
- Calculated true positives, false positives, true negatives, and false negatives
- Added empty-question and invalid-`top_k` validation tests

### Dataset

The dataset contains:

- 8 supported questions
- 4 unsupported questions
- 2 diagnostic borderline questions
- 14 total questions
- 12 questions included in strict accuracy calculations

### Evaluation result

- Passed cases: `12`
- Failed cases: `0`
- Overall accuracy: `100%`
- Status decision accuracy: `100%`
- Top-source accuracy: `100%`
- True positives: `8`
- False negatives: `0`
- True negatives: `4`
- False positives: `0`

### Threshold analysis

Current minimum similarity threshold:

`0.60`

Lowest supported-question score:

`0.6203`

Highest unsupported-question score:

`0.3312`

The current dataset shows a clear separation between supported and unsupported questions. Therefore, the threshold remains at `0.60`.

### Borderline observations

The following short and ambiguous questions were rejected:

- `Sistem tamamen yerel mi calisir?` — `0.4371`
- `Veriler nerede saklanir?` — `0.4133`

These questions relate to the project but do not contain enough semantic detail to cross the current threshold.

Lowering the threshold could improve recall for vague questions but may also increase the risk of unsupported answers.

A future improvement can ask the user to clarify low-confidence questions instead of immediately generating an answer.

### Key learning

Retrieval and generation should be evaluated separately.

This evaluation used only the embedding and retrieval layers. The chat model was not run, so retrieval errors could be measured independently of generation quality.

A perfect result on a small test set does not prove production-level accuracy. The dataset should be expanded over time with more natural, ambiguous, multilingual, and adversarial questions.

### Next step

Persist evaluation results and add broader tests for paraphrases, vague questions, source ranking, and threshold calibration.


## Day 16 — Persistent Evaluation Reporting

### Goal

Persist retrieval evaluation results in a structured, version-controlled JSON report and prepare the project for comparisons across future changes.

### What was implemented

- Added the `reports/` directory
- Added `src/evaluation_report.py`
- Added `src/evaluation_report_demo.py`
- Added report schema versioning
- Added UTC report generation timestamps
- Added evaluation configuration metadata
- Added JSON serialization for individual test cases
- Added supported and unsupported score analysis
- Added score separation margin calculation
- Added failed-case extraction
- Added diagnostic-case extraction
- Added safe report writing through a temporary file
- Added saved-report validation
- Added comparison with the previous report
- Generated `reports/evaluation_report.json`

### Report configuration

- Schema version: `1`
- Embedding model: `qwen3-embedding-0.6b`
- Top-k: `3`
- Minimum similarity threshold: `0.60`

### Latest evaluation result

- Total cases: `14`
- Strict cases: `12`
- Diagnostic cases: `2`
- Passed cases: `12`
- Failed cases: `0`
- Overall accuracy: `100%`
- Status decision accuracy: `100%`
- Top-source accuracy: `100%`
- False positives: `0`
- False negatives: `0`

### Score analysis

- Lowest supported-question score: `0.620312`
- Highest unsupported-question score: `0.331236`
- Separation margin: `0.289075`

The positive separation margin shows that the supported and unsupported questions in the current dataset are clearly separated.

### Previous report comparison

The report generator detected an earlier report and compared the new metrics with it.

All measured differences were zero:

- Overall accuracy difference: `0.0`
- Status accuracy difference: `0.0`
- Source accuracy difference: `0.0`
- False-positive difference: `0`
- False-negative difference: `0`

This confirms that the evaluation result remained stable between the two runs.

### Report persistence decision

The SQLite database remains under `storage/` and is excluded from Git because it is a generated local data store.

The evaluation report is stored under `reports/` and committed to Git because it documents the latest verified behavior of the project.

### Key learning

Terminal output is temporary, while a structured report can be:

- Version controlled
- Compared over time
- Used in documentation
- Reviewed during code changes
- Included in a final project presentation

Writing through a temporary file reduces the risk of leaving a partially written report if the save operation is interrupted.

### Next step

Add generation-quality evaluation for selected questions and record whether the local model produces correct, grounded, concise answers.


## Day 17 — Generation Evaluation and Hybrid Source Ranking

### Goal

Evaluate final RAG answer quality and improve context selection when multiple documents receive similar semantic scores.

### Generation evaluation

A structured generation evaluation dataset was created with:

- 4 supported questions
- 1 unsupported question
- 5 total cases

The evaluation checks:

- Status correctness
- Source correctness
- Required concept coverage
- Answer length
- Model usage
- Fallback correctness
- Unexpected fallback text
- Empty sources for unsupported questions

### Initial findings

The first generation evaluation exposed two problems:

1. Correct paraphrases could fail overly strict keyword checks.
2. A shallow or misleading answer could pass simple keyword checks.

Manual review also found that unrelated chunks from different documents could be mixed into one context.

### Primary-source context selection

The first improvement retrieved a wider candidate pool and selected chunks from the source of the highest semantic result.

This improved the SQLite explanation, but a regression remained:

- Question: `SQLite RAG sisteminde hangi bilgileri saklar?`
- Highest semantic source: `rag_notes.txt`
- Correct source: `sqlite_notes.txt`
- Semantic score difference: approximately `0.001`

Selecting the source of only the highest chunk was therefore too fragile.

### Hybrid source ranking

Candidate chunks are now grouped by source.

For each source, the system calculates:

- Highest semantic similarity score
- Lexical query coverage
- Combined source-selection score

Formula:

    selection_score =
        semantic_score +
        0.05 * lexical_coverage

The source with the highest combined score becomes the primary source.

The best three chunks from that source are used as the final model context.

### SQLite regression example

Raw semantic ranking:

- `rag_notes.txt`: `0.6959`
- `sqlite_notes.txt`: `0.6949`

Hybrid source ranking:

- `sqlite_notes.txt`: `0.7449`
- `rag_notes.txt`: `0.7084`
- `project_overview.txt`: `0.6116`

The selected context became:

- `sqlite_notes.txt - Chunk 3`
- `sqlite_notes.txt - Chunk 1`
- `sqlite_notes.txt - Chunk 2`

The final answer correctly stated that SQLite stores:

- Document chunks
- Source information
- Embedding vectors

### Fallback architecture

Fallback handling was removed from the local model prompt.

The responsibility now belongs entirely to the service layer:

- If the highest semantic score is below `0.60`, the service returns the fallback
- The local chat model is not loaded
- No source references are returned
- The model is only used after retrieval safety succeeds

### Final retrieval result

- Total cases: `14`
- Strict cases: `12`
- Diagnostic cases: `2`
- Passed strict cases: `12`
- Failed strict cases: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- False positives: `0`
- False negatives: `0`

### Final generation result

- Total cases: `5`
- Supported cases: `4`
- Unsupported cases: `1`
- Passed cases: `5`
- Failed cases: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- Concept accuracy: `100%`
- Length accuracy: `100%`
- Clean-answer accuracy: `100%`
- Fallback accuracy: `100%`
- Average answer length: `149.60`

### Key learning

Good retrieval requires more than choosing the single highest-scoring chunk.

When semantic scores are close, query terms and document-level evidence can help identify the correct source.

Retrieving broadly and selecting narrowly provides a more coherent prompt without increasing the number of chunks sent to the local model.

Automated evaluation is useful for detecting regressions, but human review is still necessary for grammar, fluency, factual nuance, and usefulness.

### Next step

Measure retrieval, model-loading, generation, and total response times to identify local performance bottlenecks.


## Day 18 — Performance Measurement and Persistent Sessions

### Goal

Measure the latency of each RAG pipeline stage, identify the actual bottlenecks, and improve repeated-question performance without reducing answer quality.

### Initial baseline

The first end-to-end comparison used:

- One answerable SQLite question
- One unsupported Jupiter question

Initial results:

- Answerable request: approximately `25.83 seconds`
- Unsupported request: approximately `2.05 seconds`

The unsupported question was much faster because the chat model was not loaded and no answer generation was performed.

### Detailed instrumentation

Timing instrumentation was added to the retrieval and service layers.

Measured retrieval stages:

- Database reading
- Embedding model loading
- Query embedding generation
- Embedding model unloading
- Similarity calculation and ranking
- Total retrieval time

Measured service stages:

- Hybrid source ranking
- Context selection
- Prompt construction
- Chat model loading
- Answer generation
- Chat model unloading
- Total service time

### Retrieval findings

A detailed retrieval test produced:

- SQLite reading: `0.0011 seconds`
- Embedding model loading: `5.0078 seconds`
- Query embedding generation: `0.6827 seconds`
- Embedding model unloading: `0.0726 seconds`
- Similarity ranking: `0.0090 seconds`
- Total retrieval: `5.7732 seconds`

The embedding model loading step represented most of the retrieval cost.

SQLite reading, cosine similarity, and source ranking were not meaningful bottlenecks for the current 16-chunk dataset.

### Repeated stateless benchmark

The stateless benchmark contained:

- 3 cases
- 3 repetitions per case
- 9 total runs

Results:

- Passed runs: `9`
- Failed runs: `0`
- Correctness rate: `100%`

Answerable requests:

- Mean: `25.2069 seconds`
- Median: `25.2748 seconds`
- Minimum: `19.5303 seconds`
- Maximum: `30.6632 seconds`

Unsupported requests:

- Mean: `2.7810 seconds`
- Median: `3.0760 seconds`
- Minimum: `2.0381 seconds`
- Maximum: `3.2289 seconds`

Answerable requests were approximately `8.22x` slower than unsupported requests.

### Stateless bottlenecks

Answerable service bottlenecks:

1. Answer generation: `11.8997 seconds`
2. Chat model loading: `8.6434 seconds`
3. Retrieval: `2.4662 seconds`

Retrieval bottlenecks:

1. Embedding model loading: `2.1602 seconds`
2. Query embedding generation: `0.5750 seconds`
3. Embedding model unloading: `0.0940 seconds`

Model lifecycle operations were therefore a major optimization opportunity.

### Persistent model architecture

The project now supports persistent model sessions through `LocalRAGSession`.

Session lifecycle:

    Session start
    → load embedding model once
    → keep embedding model available

    First answerable question
    → lazy-load chat model
    → generate answer
    → keep chat model available

    Later questions
    → reuse embedding model
    → reuse chat model when needed

    Unsupported questions
    → reuse embedding model
    → return safe fallback
    → do not invoke chat model

    Session close
    → unload chat model
    → unload embedding model

### Backward compatibility

The original stateless interface remains available:

    answer_question(question)

When no external model objects are supplied:

- The embedding model is loaded and unloaded inside the request.
- The chat model is loaded and unloaded inside answerable requests.

The persistent session passes external model instances to the same service layer and disables per-request lifecycle management.

### Persistent-session smoke test

The first persistent session test confirmed:

- Embedding and chat models can remain loaded simultaneously.
- The embedding model is reused across every question.
- The chat model is loaded only for the first supported question.
- The chat model is reused for later supported questions.
- Unsupported questions do not invoke generation.
- Both models unload safely at session shutdown.

Measured examples:

First supported question:

- Embedding loading inside request: `0.0000 seconds`
- Chat model loading: `14.2622 seconds`
- Total service time: `26.4498 seconds`

Second supported question:

- Embedding loading: `0.0000 seconds`
- Chat model loading: `0.0000 seconds`
- Total service time: `15.7027 seconds`

Unsupported question:

- Embedding loading: `0.0000 seconds`
- Chat model loading: `0.0000 seconds`
- Generation: `0.0000 seconds`
- Total service time: `0.7406 seconds`

### Persistent-session benchmark

The optimized benchmark used:

- One session startup
- One chat model warm-up request
- 3 cases
- 3 measured repetitions per case
- 9 total measured runs
- One session shutdown

Results:

- Passed runs: `9`
- Failed runs: `0`
- Correctness rate: `100%`
- Answerable model reuse: correct
- Unsupported model behavior: correct

Warm answerable requests:

- Mean: `13.7260 seconds`
- Median: `13.6945 seconds`
- Minimum: `11.8592 seconds`
- Maximum: `15.7938 seconds`

Warm unsupported requests:

- Mean: `0.6959 seconds`
- Median: `0.6877 seconds`
- Minimum: `0.6631 seconds`
- Maximum: `0.7370 seconds`

### Baseline comparison

Answerable requests:

- Baseline median: `25.2748 seconds`
- Optimized median: `13.6945 seconds`
- Saved time: `11.5803 seconds`
- Improvement: `45.82%`
- Speedup: `1.85x`

Unsupported requests:

- Baseline median: `3.0760 seconds`
- Optimized median: `0.6877 seconds`
- Saved time: `2.3883 seconds`
- Improvement: `77.64%`
- Speedup: `4.47x`

### First-user experience

Session startup still has an initial loading cost:

- Session startup: `3.9259 seconds`
- First answer service time: `18.9104 seconds`
- Startup plus first answer: `22.8364 seconds`

The largest benefit therefore appears in the second and later questions.

### Regression results

Retrieval evaluation after optimization:

- Strict cases: `12`
- Passed: `12`
- Failed: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- False positives: `0`
- False negatives: `0`

Generation evaluation after optimization:

- Total cases: `5`
- Passed: `5`
- Failed: `0`
- Overall accuracy: `100%`
- Source accuracy: `100%`
- Concept accuracy: `100%`
- Clean-answer accuracy: `100%`
- Fallback accuracy: `100%`

### Key learning

Local model loading is expensive enough that model lifecycle design has a major effect on interactive performance.

For one-off scripts, stateless lifecycle management remains simple and safe.

For an interactive CLI, keeping models alive across multiple questions significantly reduces latency.

After removing repeated model-loading costs, answer generation becomes the main bottleneck.

### Next optimization candidates

Potential future experiments:

- Compare smaller chat models
- Reduce the maximum generation token limit
- Measure time to first token separately
- Compare answer quality and latency across model aliases
- Cache SQLite documents and deserialized embeddings in memory
- Test whether shorter prompts reduce generation latency


## Day 19 — Generation Latency and TTFT Measurement

### Goal

Measure user-perceived generation latency, compare maximum token configurations, and reduce answer-generation time without reducing retrieval or answer quality.

### Why total generation time was not enough

The previous performance instrumentation measured only the complete generation duration.

For an interactive assistant, two separate timings matter:

1. Time until the first visible response text
2. Time until the complete answer is generated

A user may perceive an application as responsive when the first text arrives quickly, even if the full answer continues streaming afterward.

### New generation metrics

`LocalGenerator` now provides:

    generate_with_metrics()

It returns:

    {
        "answer": "...",
        "metrics": {
            "time_to_first_token_seconds": ...,
            "generation_total_seconds": ...,
            "streaming_seconds": ...,
            "streaming_chunk_count": ...,
            "answer_character_count": ...
        }
    }

The original interface remains available:

    generate()

This preserves backward compatibility for code that only requires the generated answer.

### Time-to-first-token definition

In this implementation, time to first token means the time until the first non-empty streaming text chunk is returned by the Foundry Local SDK.

A streaming chunk may contain:

- One tokenizer token
- Multiple tokenizer tokens
- A word fragment
- One or more complete words

The metric is therefore more precisely a time-to-first-text-chunk measurement.

### Smoke-test result

A persistent-session smoke test produced:

- Retrieval time: `1.0277 seconds`
- Chat model loading: `0.0000 seconds`
- Time to first text chunk: `5.7533 seconds`
- Total generation: `10.9279 seconds`
- Streaming after first chunk: `5.1745 seconds`
- Streaming chunks: `49`
- Answer characters: `198`
- Total service time: `11.9592 seconds`

Validation checks passed:

- TTFT was positive
- Total generation time was greater than or equal to TTFT
- Measured character count matched the answer length
- The legacy `generation_seconds` value matched the new total-generation metric

### Max-token experiment

The same chat model was evaluated with:

- `120` maximum tokens
- `160` maximum tokens
- `220` maximum tokens

The benchmark used four supported questions:

- RAG reliability
- Foundry Local purpose
- SQLite suitability
- Project purpose

Each question was executed twice for every configuration.

Total measured executions:

    3 configurations
    × 4 questions
    × 2 repetitions
    = 24 runs

### Quality checks

Every benchmark run checked:

- Answered status
- Expected primary source
- Required answer concepts
- No unexpected fallback
- Answer-length range
- Clean sentence ending
- Embedding model reuse
- Chat model reuse

### Results for 120 tokens

- Passed: `8/8`
- Quality: `100%`
- TTFT mean: `7.6239 seconds`
- TTFT median: `7.9451 seconds`
- Generation mean: `13.3649 seconds`
- Generation median: `14.3824 seconds`
- Streaming median: `6.1411 seconds`
- Median answer length: `183 characters`

### Results for 160 tokens

- Passed: `8/8`
- Quality: `100%`
- TTFT mean: `5.8690 seconds`
- TTFT median: `5.9535 seconds`
- Generation mean: `10.6564 seconds`
- Generation median: `10.9946 seconds`
- Streaming median: `4.9686 seconds`
- Median answer length: `183 characters`

### Results for 220 tokens

- Passed: `8/8`
- Quality: `100%`
- TTFT mean: `8.1017 seconds`
- TTFT median: `8.3424 seconds`
- Generation mean: `13.8037 seconds`
- Generation median: `14.3730 seconds`
- Streaming median: `6.0970 seconds`
- Median answer length: `183 characters`

### Configuration decision

The default maximum generation limit was reduced from `220` to `160`.

Measured comparison against `220`:

- TTFT median improvement: approximately `28.6%`
- Generation median improvement: approximately `23.5%`
- Quality difference: none in the current tests
- Median answer-length difference: none
- Truncated answers: none detected

`120` was not automatically selected merely because it had the smallest upper limit. The model generated the same answers below all three limits, and `120` was slower in this measurement.

This demonstrates that `max_tokens` is an output ceiling rather than a requested output length. Lowering it does not guarantee proportionally faster inference when the model naturally finishes before reaching the ceiling.

### Measurement limitation

The test used only two repetitions for each case and ran configurations sequentially.

Local inference latency may be influenced by:

- CPU scheduling
- Memory pressure
- Thermal state
- Model runtime caching
- Background applications
- Configuration execution order

The selected value is therefore the best measured candidate, not a universal performance guarantee.

### Generation regression

The standard five-case generation evaluation was rerun after changing the default to `160`.

Results:

- Supported cases: `4`
- Unsupported cases: `1`
- Passed: `5`
- Failed: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- Concept accuracy: `100%`
- Answer-length accuracy: `100%`
- Clean-answer accuracy: `100%`
- Fallback accuracy: `100%`

The unsupported Jupiter question:

- Returned `insufficient_context`
- Did not load the chat model
- Had zero TTFT
- Had zero generation time
- Returned the fixed fallback answer

### Key learning

Generation latency is composed of two meaningful periods:

    Request submitted
    → model processing before first text
    → streaming response completion

Reducing maximum tokens may help, but performance must be measured instead of assumed.

The current main latency component is the time before the first generated text chunk.

### Future experiments

Potential next steps:

- Compare different chat model aliases
- Randomize benchmark configuration order
- Increase repetition count
- Measure tokens per second when token usage becomes available
- Compare shorter and longer prompts
- Measure prompt token count
- Cache deserialized document embeddings in memory
- Evaluate answer quality with a larger question set


## Day 20 — Local Chat Model Comparison

### Goal

Compare multiple Foundry Local chat models under the same retrieval, prompt, generation, and evaluation conditions.

The purpose was not simply to find the fastest model. The selected model also needed to:

- Use the correct retrieved source
- Include the required answer concepts
- Produce a complete answer
- Avoid unsupported fallback behavior
- Reuse persistent model resources correctly
- Pass every quality and safety case

### Models

The benchmark compared:

- `phi-4-mini`
- `phi-3.5-mini`
- `qwen2.5-1.5b`

### Fixed experiment settings

- Embedding model: `qwen3-embedding-0.6b`
- Max tokens: `160`
- Temperature: `0.0`
- Retrieval top-k: `3`
- Similarity threshold: `0.6000`
- Same SQLite database
- Same retrieved context
- Same system and user prompt structure
- Same evaluation questions

### Technical compatibility test

Before the full benchmark, every model was tested independently.

All three models successfully:

- Loaded from the Foundry Local catalog
- Created a chat client
- Produced a streaming response
- Returned generation metrics
- Unloaded safely

Technical compatibility alone was not treated as sufficient evidence of model quality.

### Benchmark design

Each model completed:

- One model load
- One warm-up request
- Four supported questions
- One unsupported question
- Two repetitions of every measured case
- One model unload

Total:

    3 × 5 × 2 = 30 measured runs

### phi-4-mini result

- Passed: `10/10`
- Quality rate: `100%`
- Supported cases: `8/8`
- Unsupported cases: `2/2`
- Load time: `11.0719 seconds`
- TTFT median: `5.7346 seconds`
- Generation median: `10.7710 seconds`
- Service median: `11.3297 seconds`
- Median answer length: `183 characters`

The model produced complete, concise, source-grounded answers for every case.

### phi-3.5-mini result

- Passed: `4/10`
- Quality rate: `40%`
- Supported cases: `2/8`
- Unsupported cases: `2/2`
- Load time: `7.6304 seconds`
- TTFT median: `8.2320 seconds`
- Generation median: `21.2476 seconds`
- Service median: `21.8154 seconds`
- Median answer length: `333 characters`

Failure causes included:

- Responses ending in the middle of a word
- Missing required project concepts
- Repetitive or unclear Turkish
- Longer generation time than `phi-4-mini`

This model was both slower and less reliable for the current RAG prompt.

### qwen2.5-1.5b result

- Passed: `8/10`
- Quality rate: `80%`
- Supported cases: `6/8`
- Unsupported cases: `2/2`
- Load time: `3.7939 seconds`
- TTFT median: `2.9827 seconds`
- Generation median: `6.5016 seconds`
- Service median: `7.0251 seconds`
- Median answer length: `327.5 characters`

The model was substantially faster than both Phi models.

However, both executions of the RAG reliability question failed because:

- The answer became unnecessarily long
- The final generation was truncated
- The answer did not end cleanly
- All required concepts were not present in the completed text

### Unsupported-case interpretation

All models passed the unsupported Jupiter case.

This result does not show that every chat model made the correct safety decision.

The retrieval layer detected insufficient context before generation and skipped the chat model entirely.

Therefore, unsupported-question safety is primarily enforced by the deterministic service layer rather than the selected chat model.

### Final decision

The default model remains:

    phi-4-mini

It was the only model with a `100%` result across:

- Quality
- Source grounding
- Concept coverage
- Complete answers
- Model lifecycle
- Persistent reuse
- Unsupported-question behavior

`qwen2.5-1.5b` was the fastest raw model, but the project does not select a model that fails quality tests.

### Key learning

The fastest model is not necessarily the fastest acceptable model.

Model loading time is important for one-off scripts, but it is amortized in the persistent CLI session.

For an interactive RAG assistant, the most important selection order is:

1. Correctness and source grounding
2. Complete and clean answers
3. Safety behavior
4. Stable model lifecycle
5. TTFT and generation latency

### Future experiments

Potential follow-up work:

- Test `qwen2.5-1.5b` with a stricter concise-answer prompt
- Test model-specific max-token limits
- Compare additional Qwen and Phi model sizes
- Expand the evaluation dataset
- Measure memory usage for each model
- Randomize benchmark model order
- Use more repetitions to reduce timing variance



# Adım 19 — Project notes’a Gün 21’i ekle

`docs/project-notes.md` dosyasının sonuna ekle:

```markdown
## Day 21 — Final Audit and v1.0.0 Release Preparation

### Goal

Validate the complete project before creating the first stable release.

This day focused on release readiness rather than adding a new RAG capability.

### Environment validation

The following runtime settings were confirmed:

- Branch: `main`
- Chat model: `phi-4-mini`
- Maximum generation tokens: `160`
- Temperature: `0.0`
- Working tree initially clean

### Python compilation

All Python files under `src` were compiled together.

Result:

    Python files: 39
    Compile exit code: 0

Generated `__pycache__` directories remained excluded from Git.

### JSON report validation

Seven existing JSON reports were loaded and validated:

- `evaluation_report.json`
- `generation_evaluation_report.json`
- `generation_latency_report.json`
- `model_comparison_report.json`
- `performance_baseline.json`
- `performance_optimized.json`
- `performance_report.json`

Result:

    Valid reports: 7/7
    Schema version: 1
    Validation exit code: 0

### Retrieval regression

The retrieval evaluation was executed again.

Result:

- Strict cases: `12`
- Passed: `12`
- Failed: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- False positives: `0`
- False negatives: `0`
- Score-separation margin: `0.289075`

No retrieval regression was detected.

### Generation regression

The generation evaluation was executed again using `phi-4-mini`.

Result:

- Total cases: `5`
- Passed: `5`
- Failed: `0`
- Status accuracy: `100%`
- Source accuracy: `100%`
- Concept accuracy: `100%`
- Clean-answer accuracy: `100%`
- Fallback accuracy: `100%`

The unsupported Jupiter question did not invoke the chat model and produced zero generation time.

### End-to-end CLI smoke test

The persistent CLI was tested with one supported and one unsupported question.

Supported question:

    Foundry Local ne işe yarar?

Result:

- Status: `answered`
- Primary source: `foundry_local_notes.txt`
- Embedding model reused
- Chat model loaded lazily
- Answer generated with `phi-4-mini`

Unsupported question:

    Jupiter'in kaç uydusu vardır?

Result:

- Status: `insufficient_context`
- No source selected
- Embedding model reused
- Chat model not invoked
- Generation time: `0`
- Deterministic fallback returned

The CLI then closed both local models safely.

### Repository hygiene

The final repository checks confirmed:

- `.venv` is not tracked
- `__pycache__` is not tracked
- Python bytecode is not tracked
- `storage/rag.db` is not tracked
- `.env` files are not tracked
- No common secret or API-key patterns were detected

### Automated final audit

New modules:

- `src/final_audit.py`
- `src/final_audit_demo.py`

Generated reports:

- `reports/final_audit_report.json`
- `reports/final_audit_report.md`

Final result:

    Total checks: 14
    Passed checks: 14
    Failed checks: 0
    Blocking checks: 14/14
    Release ready: true

### Release documentation

The following release documents were prepared:

- `CHANGELOG.md`
- `docs/release-notes-v1.0.0.md`

### Final release decision

The project is eligible for the `v1.0.0` release workflow.

The release tag must only be created after:

1. All Day 21 files are staged
2. The final audit is rerun against the staged repository
3. The audit still reports `14/14`
4. The final commit is pushed to `main`