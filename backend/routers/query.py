from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from backend.retrieval.embedder import embed_query
from backend.retrieval.retriever import hybrid_retrieve
from backend.retrieval.reranker import rerank
from backend.generation.generator import generate_answer
from backend.processors.audio_processor import transcribe_bytes

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    collection: str = "omnilens_default"
    top_k: int = 5


@router.post("/")
async def query_text(req: QueryRequest):
    """
    Answer a text query using multi-modal RAG.
    Returns an answer with cited source chunks.
    """
    query_embedding = embed_query(req.query)
    candidates = hybrid_retrieve(req.query, query_embedding, collection=req.collection, top_k=10)
    top_chunks = rerank(req.query, candidates, top_k=req.top_k)
    result = generate_answer(req.query, top_chunks)
    return result


@router.post("/voice")
async def query_voice(
    audio: UploadFile = File(...),
    collection: str = Form(default="omnilens_default"),
    top_k: int = Form(default=5),
):
    """
    Transcribe a voice query via Whisper, then run the same RAG pipeline.
    """
    content = await audio.read()
    transcript = transcribe_bytes(content)

    query_embedding = embed_query(transcript)
    candidates = hybrid_retrieve(transcript, query_embedding, collection=collection, top_k=10)
    top_chunks = rerank(transcript, candidates, top_k=top_k)
    result = generate_answer(transcript, top_chunks)

    result["transcribed_query"] = transcript
    return result
