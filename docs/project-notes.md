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