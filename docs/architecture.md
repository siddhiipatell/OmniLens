# OmniLens — Architecture

## Overview

OmniLens is a three-layer system: a frontend UI, a FastAPI backend, and a ChromaDB vector store. The backend handles two distinct workflows — **ingestion** (offline) and **querying** (online).

---

## Ingestion pipeline

```
User uploads file
       │
       ▼
┌─────────────────┐
│ Modality router │  ← detects file type from extension
└────────┬────────┘
         │
   ┌─────┴──────┬────────────┐
   ▼            ▼            ▼
[PDF]        [Image]      [Audio]
   │            │            │
PyMuPDF     GPT-4V /     Whisper
   +        LLaVA           ASR
Unstructured  │            │
   │        Caption →    Transcript →
Text +      text chunk   sentence chunks
table chunks    │            │
   │            │            │
   └─────┬──────┴────────────┘
         ▼
  All chunks tagged with:
  { modality, source, page/timestamp/img_path, type }
         │
         ▼
  Embedding engine
  (text-embedding-3-small)
         │
         ▼
    ChromaDB upsert
    + metadata store
```

### Key design decisions

**Why caption images instead of embedding them directly?**
Text embeddings are far more mature and better supported than multi-modal embeddings. By converting images to rich text captions, all three modalities share one embedding space and one retrieval system — no extra image index to maintain.

**Why table chunks stay unsplit?**
Splitting a table mid-row destroys its meaning. Each table is stored as one chunk, even if it exceeds the target chunk size.

**Why sentence-level audio chunks?**
Sentence boundaries are semantically meaningful split points. Splitting mid-sentence at a fixed token count creates chunks that are harder to retrieve and harder to read as citations.

---

## Query pipeline

```
User query (text or voice)
          │
          ├─ voice? → Whisper transcription
          │
          ▼
   Query rewriting (optional)
   LLM paraphrase for better retrieval
          │
          ▼
   Embed query
   (same model as ingestion)
          │
     ┌────┴────┐
     ▼         ▼
  Dense       BM25
  search    keyword
  (Chroma)  search
     │         │
     └────┬────┘
          ▼
  Reciprocal Rank Fusion
  (combines both rankings)
          │
          ▼
  Cross-encoder reranking
  (ms-marco-MiniLM, top-3)
          │
          ▼
  LLM generation
  (GPT-4o / Claude)
  with [Source N] citations
          │
          ▼
  Answer + structured sources
  { modality, file, page/timestamp, chunk_text }
```

### Key design decisions

**Why hybrid retrieval?**
Dense vector search excels at semantic similarity but misses exact keyword matches ("Section 3.2", "Q3 FY24", proper nouns). BM25 excels at keywords but misses paraphrased queries. RRF fusion captures the best of both.

**Why a cross-encoder reranker?**
Bi-encoder embeddings (used for initial retrieval) score query and document independently — they're fast but imprecise. A cross-encoder sees the query and document together, producing much more accurate relevance scores. The two-stage approach keeps latency manageable: retrieve 10 cheaply, rerank 10 expensively, send top 3 to the LLM.

**Why temperature=0.1 for generation?**
The task is factual Q&A with citations. Low temperature reduces hallucination and keeps the LLM grounded in the provided chunks.

---

## Data model

Each indexed chunk has this shape in ChromaDB:

```json
{
  "id": "uuid",
  "text": "chunk content...",
  "source": "filename.pdf",
  "modality": "pdf | image | audio",
  "type": "text | table | image_caption | transcript",
  "page": 12,           // pdf only
  "timestamp": "02:34", // audio only
  "img_path": "...",    // image only
}
```

---

## Component dependency map

```
frontend/app.py
    └── POST /ingest  → routers/ingest.py
            ├── processors/pdf_processor.py
            ├── processors/image_processor.py
            └── processors/audio_processor.py
                    └── retrieval/embedder.py
                            └── vectorstore/chroma_client.py

    └── POST /query   → routers/query.py
            ├── retrieval/embedder.py
            ├── retrieval/retriever.py  (hybrid search)
            ├── retrieval/reranker.py   (cross-encoder)
            └── generation/generator.py (LLM + citations)
```
