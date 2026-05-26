"""
Retriever
─────────
Hybrid retrieval: dense vector search (ChromaDB) + BM25 keyword search,
fused via Reciprocal Rank Fusion (RRF).

RRF score = Σ 1 / (k + rank_i)  where k=60 (standard constant)
"""
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from backend.vectorstore.chroma_client import get_collection

RRF_K = 60


def hybrid_retrieve(
    query: str,
    query_embedding: List[float],
    collection: str,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    1. Dense retrieval via ChromaDB cosine similarity
    2. BM25 keyword retrieval over the same collection
    3. Fuse rankings with RRF
    """
    col = get_collection(collection)
    all_docs = col.get(include=["documents", "metadatas"])

    documents = all_docs["documents"]
    metadatas = all_docs["metadatas"]
    ids = all_docs["ids"]

    if not documents:
        return []

    # --- Dense retrieval ---
    dense_results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k * 2, len(documents)),
        include=["documents", "metadatas", "distances"],
    )
    dense_ids = dense_results["ids"][0]

    # --- BM25 keyword retrieval ---
    tokenised_corpus = [doc.lower().split() for doc in documents]
    bm25 = BM25Okapi(tokenised_corpus)
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_ranked = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
    bm25_ids = [ids[i] for i in bm25_ranked[: top_k * 2]]

    # --- Reciprocal Rank Fusion ---
    rrf_scores: Dict[str, float] = {}
    for rank, doc_id in enumerate(dense_ids):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)
    for rank, doc_id in enumerate(bm25_ids):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)

    sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]

    # Build result dicts
    id_to_doc = {ids[i]: {"text": documents[i], **metadatas[i]} for i in range(len(ids))}
    return [id_to_doc[doc_id] for doc_id in sorted_ids if doc_id in id_to_doc]
