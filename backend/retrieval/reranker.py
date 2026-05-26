"""
Reranker
────────
Cross-encoder reranking using ms-marco-MiniLM-L-6-v2.
Runs on CPU — fast enough for top-10 candidate reranking (~100ms).
"""
import os
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Score each (query, chunk) pair with a cross-encoder and return top_k.
    """
    if not candidates:
        return []

    model = _get_reranker()
    pairs = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    scored = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    top = [chunk for _, chunk in scored[:top_k]]

    # Attach rerank score for transparency
    for i, (score, chunk) in enumerate(scored[:top_k]):
        top[i] = {**chunk, "rerank_score": float(score)}

    return top
