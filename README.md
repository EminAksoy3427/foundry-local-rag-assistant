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