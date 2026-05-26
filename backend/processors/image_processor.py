"""
Image Processor
───────────────
Generates a rich natural-language caption for each uploaded image
using GPT-4V (default) or LLaVA via Ollama (local, free).

The caption is stored as a text chunk so the embedding + retrieval
pipeline handles images identically to text — no separate image index.

Each chunk is tagged with:
  - source: original filename
  - img_path: path to stored original image (for citation display)
  - type: "image_caption"
  - modality: "image"
"""
import base64
import uuid
import os
from typing import List, Dict, Any

import httpx
from openai import OpenAI

LOCAL_VISION = os.getenv("LOCAL_VISION", "false").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:13b")
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o")

CAPTION_PROMPT = """You are an expert at analyzing and describing images in the context of document understanding.

Describe this image in precise detail. Your description will be used to answer questions, so be thorough:

1. If it is a CHART or GRAPH: identify the chart type, all axis labels, data series names, key data points, trends, and any title or legend text.
2. If it is a DIAGRAM or FLOWCHART: describe all components, labels, arrows, and the relationships between elements.
3. If it is a TABLE: transcribe the headers and all cell values in a structured format.
4. If it is a PHOTO or ILLUSTRATION: describe the subject, setting, objects, people, and any visible text.

Be specific with numbers, names, and values. Do not say "the chart shows" — directly state what the data is."""


async def process_image(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Generate a vision caption and return as a single indexable chunk.
    """
    b64 = base64.b64encode(content).decode("utf-8")

    if LOCAL_VISION:
        caption = await _caption_with_ollama(b64)
    else:
        caption = await _caption_with_gpt4v(b64)

    return [{
        "id": str(uuid.uuid4()),
        "text": caption,
        "source": filename,
        "img_path": filename,   # resolved to storage path in production
        "type": "image_caption",
        "modality": "image",
    }]


async def _caption_with_gpt4v(b64: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": CAPTION_PROMPT},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}",
                    "detail": "high",
                }},
            ],
        }],
        max_tokens=1000,
    )
    return response.choices[0].message.content


async def _caption_with_ollama(b64: str) -> str:
    """LLaVA via Ollama — runs fully locally, no API cost."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_VISION_MODEL,
                "prompt": CAPTION_PROMPT,
                "images": [b64],
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["response"]
