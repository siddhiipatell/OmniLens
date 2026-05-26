"""
Audio Processor
───────────────
Transcribes audio using OpenAI Whisper (runs locally, no API cost).
Splits transcript into sentence-level chunks aligned to timestamps.

Each chunk is tagged with:
  - source: original filename
  - timestamp: "MM:SS" of the chunk start
  - type: "transcript"
  - modality: "audio"
"""
import io
import re
import uuid
import tempfile
import os
from typing import List, Dict, Any

import nltk
import whisper

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")  # upgrade to "medium" for better accuracy
    return _whisper_model


def process_audio(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Full audio processing pipeline:
      1. Write bytes to a temp file (Whisper needs a file path)
      2. Transcribe with word-level timestamps
      3. Chunk by sentence boundaries
      4. Tag with timestamp metadata
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=_get_ext(filename)) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = _get_model().transcribe(tmp_path, word_timestamps=True, verbose=False)
    finally:
        os.unlink(tmp_path)

    return _chunk_transcript(result, filename)


def transcribe_bytes(content: bytes) -> str:
    """Lightweight transcription for voice queries — returns raw text only."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = _get_model().transcribe(tmp_path, verbose=False)
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)


def _chunk_transcript(result: dict, filename: str) -> List[Dict[str, Any]]:
    """
    Combine Whisper segments into sentence chunks using NLTK sentence tokenizer.
    Each chunk gets the timestamp of its first word.
    """
    full_text = result["text"]
    # Map character offset → timestamp using Whisper segments
    char_ts_map = _build_char_timestamp_map(result.get("segments", []))

    sentences = nltk.sent_tokenize(_clean_transcript(full_text))

    chunks = []
    cursor = 0
    for sentence in sentences:
        start_char = full_text.find(sentence, cursor)
        if start_char == -1:
            start_char = cursor
        cursor = start_char + len(sentence)

        ts_seconds = char_ts_map.get(start_char, 0)
        chunks.append({
            "id": str(uuid.uuid4()),
            "text": sentence.strip(),
            "source": filename,
            "timestamp": _fmt_timestamp(ts_seconds),
            "type": "transcript",
            "modality": "audio",
        })

    return [c for c in chunks if len(c["text"]) > 20]  # drop very short fragments


def _build_char_timestamp_map(segments: list) -> dict:
    """Build a rough char-offset → seconds map from Whisper segments."""
    mapping = {}
    offset = 0
    for seg in segments:
        text = seg.get("text", "")
        mapping[offset] = seg.get("start", 0)
        offset += len(text)
    return mapping


def _clean_transcript(text: str) -> str:
    """Remove filler words and repeated punctuation."""
    filler = r"\b(um|uh|hmm|like|you know|I mean|basically|literally|right)\b"
    text = re.sub(filler, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _fmt_timestamp(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def _get_ext(filename: str) -> str:
    return os.path.splitext(filename)[1] or ".mp3"
