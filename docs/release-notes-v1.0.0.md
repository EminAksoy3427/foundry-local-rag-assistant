# Foundry Local RAG Assistant v1.0.0

## Overview

Foundry Local RAG Assistant is a fully local document question-answering application built with Microsoft Foundry Local, Python, and SQLite.

The application retrieves relevant document chunks, validates retrieval confidence, builds grounded prompts, and generates answers with a local language model.

No cloud-based language model API is required during normal operation.

## Core features

- Fully local embedding generation
- Fully local language-model inference
- SQLite-backed document and vector storage
- Document loading and chunking
- Semantic retrieval
- Hybrid source ranking
- Context construction
- Source-grounded answer generation
- Source references in responses
- Minimum-similarity safety threshold
- Deterministic fallback for unsupported questions
- Persistent embedding and chat-model sessions
- Lazy chat-model loading
- Streaming answer generation
- Time-to-first-token measurement
- Retrieval and generation performance metrics
- Command-line interface
- Automated evaluation and benchmark reports

## Default models

- Embedding model: `qwen3-embedding-0.6b`
- Chat model: `phi-4-mini`
- Maximum generation tokens: `160`
- Temperature: `0.0`

## Retrieval configuration

- Top-k context chunks: `3`
- Minimum similarity threshold: `0.6000`
- Database: SQLite
- Local database path: `storage/rag.db`

The local database is excluded from Git and must be generated through the ingestion workflow.

## Evaluation results

### Retrieval evaluation

- Strict cases: `12`
- Passed cases: `12`
- Failed cases: `0`
- Overall accuracy: `100%`
- Status accuracy: `100%`
- Source accuracy: `100%`
- False positives: `0`
- False negatives: `0`
- Supported/unsupported score separation margin: `0.289075`

### Generation evaluation

- Total cases: `5`
- Passed cases: `5`
- Failed cases: `0`
- Overall accuracy: `100%`
- Source accuracy: `100%`
- Concept accuracy: `100%`
- Clean-answer accuracy: `100%`
- Fallback accuracy: `100%`

### Model comparison

Three local chat models were compared:

| Model | Quality rate | Median TTFT | Median generation |
|---|---:|---:|---:|
| `phi-4-mini` | `100%` | `5.7346 s` | `10.7710 s` |
| `qwen2.5-1.5b` | `80%` | `2.9827 s` | `6.5016 s` |
| `phi-3.5-mini` | `40%` | `8.2320 s` | `21.2476 s` |

`phi-4-mini` remains the default because it was the only model that passed every quality, grounding, completion, lifecycle, and safety check.

### Persistent-session performance

Persistent model sessions reduced repeated loading overhead.

Measured improvements included:

- Answerable-query median service time improvement: approximately `45.82%`
- Unsupported-query median service time improvement: approximately `77.64%`
- Answerable-query speedup: approximately `1.85x`
- Unsupported-query speedup: approximately `4.47x`

## Safety behavior

When the highest retrieval score is below the configured threshold:

- No context is passed to the chat model
- The chat model is not loaded or invoked
- No source reference is returned
- A deterministic fallback response is used

Default fallback response:

> Bu bilgi verilen dokumanlarda bulunmuyor.

## Final audit

The `v1.0.0` release candidate passed all final audit checks:

- JSON reports: valid
- Python compilation: successful
- Retrieval regression: passed
- Generation regression: passed
- Model selection: validated
- Token configuration: validated
- Persistent model reuse: validated
- Required project files: present
- Forbidden tracked files: none
- Secret-pattern scan: clean
- Runtime configuration: correct

Final result:

    14/14 blocking checks passed
    Release ready: true

Audit reports:

- `reports/final_audit_report.json`
- `reports/final_audit_report.md`

## Running the project

Create and activate the virtual environment, install the dependencies, ingest the documents, and start the CLI.

```powershell
python -m src.ingest_demo
python -m src.cli