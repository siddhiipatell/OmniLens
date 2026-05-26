# OmniLens 🔍

> Ask anything about your documents, images, and recordings — in text or voice.

OmniLens is a production-grade multi-modal RAG (Retrieval-Augmented Generation) system that ingests **PDFs**, **images**, and **audio files**, indexes them in a unified vector store, and answers natural language queries with precise source citations across all three modalities.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-orange.svg)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-purple.svg)](https://trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What it does

| You provide | OmniLens does |
|---|---|
| A PDF research paper | Extracts text + tables, chunks semantically, indexes with page metadata |
| An image (chart, diagram, photo) | Generates a rich vision caption via GPT-4V / LLaVA, indexes the description |
| An audio recording / podcast | Transcribes via Whisper, chunks by sentence, indexes with timestamps |
| A natural language query (typed or spoken) | Retrieves relevant chunks across all modalities, reranks, generates a cited answer |

**Example query:** *"What does the Q3 revenue chart show, and how does the CFO comment on it in the earnings call recording?"*
→ OmniLens pulls the image caption (chart) + the audio transcript chunk (CFO comment) and synthesises a single cited answer.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    Frontend                      │
│         Streamlit UI  /  Next.js (v2)            │
│   Upload  │  Voice Query  │  Text Query  │ Answer│
└──────┬────┴───────┬────────┴──────┬──────┴───────┘
       │            │               │
       ▼            ▼               ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                     │
│                                                  │
│  ┌─────────────┐  ┌────────────┐  ┌──────────┐  │
│  │PDF Processor│  │Img Processor│  │Audio Proc│  │
│  │PyMuPDF +    │  │GPT-4V /    │  │Whisper + │  │
│  │Unstructured │  │LLaVA       │  │NLTK      │  │
│  └──────┬──────┘  └─────┬──────┘  └────┬─────┘  │
│         └───────────────┼──────────────┘        │
│                         ▼                        │
│              ┌──────────────────┐                │
│              │  Embedding Engine │               │
│              │  text-embedding-  │               │
│              │  3-small / BGE-M3 │               │
│              └────────┬─────────┘               │
│                       │                          │
│         ┌─────────────┼──────────────┐           │
│         ▼             ▼              ▼           │
│    ┌─────────┐  ┌──────────┐  ┌──────────┐      │
│    │ChromaDB │  │ Metadata │  │File Store│      │
│    │ Vectors │  │  Store   │  │(S3/local)│      │
│    └─────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for full system diagrams.

---

## Project structure

```
omnilens/
├── backend/
│   ├── main.py                   # FastAPI app entrypoint
│   ├── routers/
│   │   ├── ingest.py             # /ingest endpoints (PDF, image, audio)
│   │   └── query.py              # /query endpoint
│   ├── processors/
│   │   ├── pdf_processor.py      # PyMuPDF + Unstructured extraction
│   │   ├── image_processor.py    # GPT-4V / LLaVA captioning
│   │   └── audio_processor.py    # Whisper ASR + chunking
│   ├── retrieval/
│   │   ├── embedder.py           # Embedding wrapper
│   │   ├── retriever.py          # Hybrid dense + BM25 search
│   │   └── reranker.py           # Cross-encoder reranking
│   ├── generation/
│   │   └── generator.py          # LLM answer synthesis + citation
│   └── vectorstore/
│       └── chroma_client.py      # ChromaDB connection + upsert helpers
│
├── frontend/
│   └── app.py                    # Streamlit UI
│
├── docs/
│   ├── architecture.md           # System diagrams (ingestion + query pipelines)
│   ├── ingestion_pipeline.md     # Detailed ingestion flow
│   └── query_pipeline.md         # Detailed query flow
│
├── tests/
│   ├── test_pdf_processor.py
│   ├── test_image_processor.py
│   ├── test_audio_processor.py
│   └── test_retrieval.py
│
├── scripts/
│   └── ingest_sample_data.py     # Quick-start: ingest sample files
│
├── sample_data/                  # Sample PDF, image, audio for testing
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- [ffmpeg](https://ffmpeg.org/download.html) (required by Whisper)
- OpenAI API key (or Ollama running locally for free models)

### 1. Clone and install

```bash
git clone https://github.com/yourusername/omnilens.git
cd omnilens
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Start the frontend

```bash
streamlit run frontend/app.py
```

### 5. Ingest sample data

```bash
python scripts/ingest_sample_data.py
```

Then open `http://localhost:8501` and start asking questions.

---

## API reference

### Ingest a file

```http
POST /ingest
Content-Type: multipart/form-data

file: <your file>          # PDF, PNG/JPG, MP3/WAV/M4A
collection: my_collection  # optional, default: "default"
```

**Response:**
```json
{
  "status": "success",
  "chunks_indexed": 42,
  "modality": "pdf",
  "collection": "my_collection"
}
```

### Query

```http
POST /query
Content-Type: application/json

{
  "query": "What revenue growth did the CFO highlight?",
  "collection": "my_collection",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "The CFO highlighted 23% YoY revenue growth...",
  "sources": [
    {
      "modality": "audio",
      "file": "earnings_call.mp3",
      "timestamp": "00:14:32",
      "chunk": "...we saw 23 percent year-over-year growth..."
    },
    {
      "modality": "pdf",
      "file": "annual_report.pdf",
      "page": 12,
      "chunk": "Revenue increased from $4.2B to $5.2B..."
    }
  ]
}
```

### Voice query

```http
POST /query/voice
Content-Type: multipart/form-data

audio: <recorded audio>
collection: my_collection
```

Transcribes the audio via Whisper, then runs the same query pipeline.

---

## Configuration

All config lives in `.env`:

```env
# LLM
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o                        # or claude-3-5-sonnet-20241022

# Vision (for image captioning)
VISION_MODEL=gpt-4o                     # or use LOCAL_VISION=true for LLaVA via Ollama
LOCAL_VISION=false
OLLAMA_BASE_URL=http://localhost:11434

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small  # or BAAI/bge-m3 for local

# Vector store
CHROMA_PERSIST_DIR=./chroma_db

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Retrieval
TOP_K=10
RERANK_TOP_K=3
```

---

## Modality support matrix

| File type | Extensions | Processor | Notes |
|---|---|---|---|
| PDF | `.pdf` | PyMuPDF + Unstructured | Tables preserved as structured text |
| Image | `.png .jpg .jpeg .webp` | GPT-4V / LLaVA | Vision caption stored as text chunk |
| Audio | `.mp3 .wav .m4a .ogg` | Whisper | Word-level timestamps stored |

---

## Roadmap

- [x] PDF ingestion with table extraction
- [x] Image captioning via GPT-4V
- [x] Audio transcription via Whisper
- [x] Hybrid retrieval (dense + BM25)
- [x] Cross-encoder reranking
- [x] Cited answer generation
- [ ] Video support (extract keyframes + audio track)
- [ ] Multi-collection support with access control
- [ ] Streaming answers via SSE
- [ ] LangSmith tracing integration
- [ ] Next.js frontend (v2)

---

## Built with

- [LangChain](https://langchain.com) — chunking, embedding, retrieval orchestration
- [ChromaDB](https://trychroma.com) — vector store
- [OpenAI Whisper](https://github.com/openai/whisper) — audio transcription
- [Unstructured.io](https://unstructured.io) — PDF table extraction
- [FastAPI](https://fastapi.tiangolo.com) — backend API
- [Streamlit](https://streamlit.io) — frontend UI

---

## License

MIT © Siddhi Patel
