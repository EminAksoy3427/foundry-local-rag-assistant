# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-07-21

### Added

- Local document loading and chunking
- Foundry Local embedding integration
- SQLite document and embedding storage
- Semantic chunk retrieval
- Hybrid source ranking
- Retrieval confidence threshold
- Context and prompt construction
- Local answer generation with `phi-4-mini`
- Source references
- Deterministic unsupported-question fallback
- Persistent RAG sessions
- Lazy chat-model loading
- Streaming generation
- Time-to-first-token metrics
- Retrieval and service performance metrics
- Interactive command-line interface
- Retrieval evaluation dataset and report
- Generation evaluation dataset and report
- Baseline and optimized performance benchmarks
- Max-token latency benchmark
- Local chat-model comparison benchmark
- Automated final release audit
- JSON and Markdown audit reports

### Changed

- Default generation limit optimized from `220` to `160` tokens
- Embedding and chat models are reused in persistent CLI sessions
- Unsupported questions bypass chat-model generation
- Default chat model confirmed as `phi-4-mini` after comparative evaluation

### Validated

- Retrieval strict evaluation: `12/12`
- Generation evaluation: `5/5`
- Model comparison runs: `30`
- Final release audit: `14/14`
- Secret-pattern scan: clean
- Python source compilation: successful

### Known limitations

- Small demonstration knowledge base
- Command-line interface only
- Hardware-dependent local inference latency
- No memory-consumption benchmark
- No native PDF or DOCX ingestion