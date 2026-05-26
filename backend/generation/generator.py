"""
Generator
─────────
Synthesises a final answer from reranked chunks.
The prompt instructs the LLM to cite every claim with [Source N] markers,
which are resolved back to chunk metadata in the response.
"""
import os
from typing import List, Dict, Any
from openai import OpenAI

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
_client = OpenAI()

SYSTEM_PROMPT = """You are OmniLens, an expert document assistant.
Answer the user's question using ONLY the provided source chunks.
For every claim you make, cite it with [Source N] where N is the chunk number.
If the answer requires combining information from multiple sources, do so clearly.
If the chunks don't contain enough information, say so honestly — do not fabricate.
Be concise and precise."""


def generate_answer(query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a citation-aware prompt and generate an answer.
    Returns answer text + structured source references.
    """
    context = _build_context(chunks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {query}\n\n{context}"},
    ]

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1000,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": _format_sources(chunks),
        "model": LLM_MODEL,
    }


def _build_context(chunks: List[Dict[str, Any]]) -> str:
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        meta = _format_meta(chunk)
        lines.append(f"[Source {i}] ({meta})\n{chunk['text']}")
    return "\n\n".join(lines)


def _format_meta(chunk: Dict[str, Any]) -> str:
    modality = chunk.get("modality", "unknown")
    source = chunk.get("source", "")
    if modality == "pdf":
        return f"PDF: {source}, page {chunk.get('page', '?')}"
    elif modality == "image":
        return f"Image: {source}"
    elif modality == "audio":
        return f"Audio: {source}, {chunk.get('timestamp', '?')}"
    return source


def _format_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources = []
    for chunk in chunks:
        entry = {
            "modality": chunk.get("modality"),
            "file": chunk.get("source"),
            "type": chunk.get("type"),
            "chunk": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
        }
        if chunk.get("modality") == "pdf":
            entry["page"] = chunk.get("page")
        elif chunk.get("modality") == "audio":
            entry["timestamp"] = chunk.get("timestamp")
        elif chunk.get("modality") == "image":
            entry["img_path"] = chunk.get("img_path")
        sources.append(entry)
    return sources
