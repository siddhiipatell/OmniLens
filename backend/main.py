from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import ingest, query
from backend.vectorstore.chroma_client import init_chroma

app = FastAPI(
    title="OmniLens",
    description="Multi-modal RAG — ask anything about your PDFs, images, and recordings.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_chroma()

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/query", tags=["Query"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "OmniLens"}
