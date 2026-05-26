"""
Embedder
────────
Thin wrapper around OpenAI text-embedding-3-small.
Swap EMBEDDING_MODEL in .env for a local model (BAAI/bge-m3 via sentence-transformers).
"""
import os
from typing import List
from openai import OpenAI

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
_client = OpenAI()


def embed_chunks(texts: List[str]) -> List[List[float]]:
    """Batch-embed a list of text strings. Returns a list of embedding vectors."""
    if not texts:
        return []
    response = _client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return embed_chunks([query])[0]
