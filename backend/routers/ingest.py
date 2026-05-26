import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.processors.pdf_processor import process_pdf
from backend.processors.image_processor import process_image
from backend.processors.audio_processor import process_audio
from backend.retrieval.embedder import embed_chunks
from backend.vectorstore.chroma_client import upsert_chunks

router = APIRouter()

SUPPORTED = {
    "pdf": [".pdf"],
    "image": [".png", ".jpg", ".jpeg", ".webp"],
    "audio": [".mp3", ".wav", ".m4a", ".ogg"],
}

def detect_modality(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    for modality, exts in SUPPORTED.items():
        if ext in exts:
            return modality
    raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")


@router.post("/")
async def ingest_file(
    file: UploadFile = File(...),
    collection: str = Form(default="omnilens_default"),
):
    """
    Ingest a PDF, image, or audio file into the vector store.
    Automatically detects modality from file extension.
    """
    modality = detect_modality(file.filename)
    content = await file.read()

    if modality == "pdf":
        chunks = process_pdf(content, filename=file.filename)
    elif modality == "image":
        chunks = await process_image(content, filename=file.filename)
    elif modality == "audio":
        chunks = process_audio(content, filename=file.filename)

    embeddings = embed_chunks([c["text"] for c in chunks])
    upsert_chunks(chunks, embeddings, collection=collection)

    return {
        "status": "success",
        "modality": modality,
        "file": file.filename,
        "chunks_indexed": len(chunks),
        "collection": collection,
    }
