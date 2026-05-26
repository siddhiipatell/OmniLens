"""
ChromaDB client
───────────────
Manages ChromaDB connection, collection access, and upsert operations.
"""
import os
from typing import List, Dict, Any
import chromadb

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
_client: chromadb.Client = None


def init_chroma():
    global _client
    _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    print(f"[ChromaDB] Initialised at {CHROMA_PERSIST_DIR}")


def get_client() -> chromadb.Client:
    global _client
    if _client is None:
        init_chroma()
    return _client


def get_collection(name: str):
    return get_client().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    collection: str,
):
    col = get_collection(collection)
    col.upsert(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[{k: v for k, v in c.items() if k not in ("id", "text")} for c in chunks],
    )
