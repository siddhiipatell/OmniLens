"""
PDF Processor
─────────────
Extracts text and tables from PDFs using PyMuPDF for fast text
extraction and Unstructured.io for table-aware parsing.

Each chunk is tagged with:
  - source: original filename
  - page: 1-indexed page number
  - type: "text" | "table"
  - modality: "pdf"
"""
import io
import uuid
from typing import List, Dict, Any

import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.pdf import partition_pdf

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def process_pdf(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Full PDF processing pipeline:
      1. Extract text per page via PyMuPDF (fast, preserves layout)
      2. Extract tables via Unstructured (structure-aware)
      3. Semantic chunking with overlap
      4. Tag each chunk with source metadata
    """
    text_chunks = _extract_text_chunks(content, filename)
    table_chunks = _extract_table_chunks(content, filename)
    return text_chunks + table_chunks


def _extract_text_chunks(content: bytes, filename: str) -> List[Dict[str, Any]]:
    chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    doc = fitz.open(stream=content, filetype="pdf")
    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text("text").strip()
        if not page_text:
            continue

        splits = splitter.split_text(page_text)
        for split in splits:
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": split,
                "source": filename,
                "page": page_num,
                "type": "text",
                "modality": "pdf",
            })

    doc.close()
    return chunks


def _extract_table_chunks(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Uses Unstructured to extract tables as structured text.
    Each table becomes a single chunk (tables should not be split mid-row).
    """
    chunks = []
    try:
        elements = partition_pdf(file=io.BytesIO(content), strategy="hi_res")
        for el in elements:
            if el.category == "Table":
                table_text = str(el)
                page_num = el.metadata.page_number if el.metadata else 0
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": f"[TABLE from page {page_num}]\n{table_text}",
                    "source": filename,
                    "page": page_num,
                    "type": "table",
                    "modality": "pdf",
                })
    except Exception as e:
        # Gracefully degrade — table extraction can fail on some PDFs
        print(f"[pdf_processor] Table extraction failed for {filename}: {e}")

    return chunks
