"""
main.py — FastAPI app: entrypoint del backend Uendi.

Rutas expuestas:
  GET  /health                    → estado del servidor y conteo de chunks
  POST /api/v1/chat               → consulta al motor RAG
  GET  /api/v1/admin/documents    → metadata de documentos indexados

Modelos (embedding + ChromaDB) se cargan UNA SOLA VEZ en lifespan.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .generation.generator import Generator
from .generation.guardrails import validate_query
from .ingestion.loader import load_collection
from .retrieval.augmenter import build_context
from .retrieval.retriever import Retriever
from .retrieval.reranker import rerank

load_dotenv()

_ROOT = Path(__file__).parent.parent.parent  # raíz del repo
CHROMA_PATH = os.getenv("CHROMA_PATH", str(_ROOT / "data" / "chroma_db"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# Singletons inicializados en lifespan
_retriever: Retriever | None = None
_generator: Generator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga modelos al arrancar; libera al apagar."""
    global _retriever, _generator
    collection = load_collection(CHROMA_PATH)
    _retriever = Retriever(collection)
    _generator = Generator()
    print(f"✅ Backend listo — {_retriever.chunk_count} chunks indexados")
    yield
    _retriever = None
    _generator = None


app = FastAPI(
    title="Uendi RAG API",
    description="Backend del asistente Uendi — Banco Ueno Paraguay",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Schemas ──────────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    history: list[Message] = []


class Source(BaseModel):
    title: str
    url: str
    doc_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


# ─── Rutas ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Verifica que el servidor esté levantado y la DB indexada."""
    count = _retriever.chunk_count if _retriever else 0
    return {"status": "ok", "chunks_indexed": count}


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Procesa una pregunta del usuario con el pipeline RAG completo:
    validate → retrieve → rerank → augment → generate
    """
    if not _retriever or not _generator:
        raise HTTPException(status_code=503, detail="Servidor no inicializado.")

    validate_query(req.query)

    history = [{"role": m.role, "content": m.content} for m in req.history]
    chunks = _retriever.retrieve(req.query)
    ranked = rerank(chunks, top_k=3)
    context = build_context(ranked)
    answer = _generator.generate(req.query, context, history)

    sources = [
        Source(
            title=c["metadata"]["title"],
            url=c["metadata"]["source_url"],
            doc_id=c["metadata"].get("source_url", ""),
        )
        for c in ranked[:2]
    ]

    return ChatResponse(answer=answer, sources=sources)


@app.get("/api/v1/admin/documents")
def get_documents():
    """Retorna la cantidad de chunks indexados en ChromaDB."""
    if not _retriever:
        raise HTTPException(status_code=503, detail="Servidor no inicializado.")
    return {"chunks_indexed": _retriever.chunk_count}
