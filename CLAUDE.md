# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexto del Proyecto
Sistema RAG para el chatbot Uendi del Banco Ueno (Paraguay).
Permite que Uendi responda con información actualizada sobre productos bancarios
sin necesidad de reentrenar el LLM.

## Estado Actual del Código
- **MVP funcional:** `mvp/` — contiene el pipeline completo operativo (ingest + rag + UI Streamlit)
- **Backend (`backend/app/`):** módulos stub vacíos (scraper.py, chunker.py, loader.py, embedder.py, retriever.py, reranker.py, augmenter.py, generator.py, guardrails.py). La lógica de referencia está en `mvp/ingest.py` y `mvp/rag.py`.
- **Scripts (`scripts/`):** stubs vacíos — la lógica vive en `mvp/ingest.py`
- **Frontend (`frontend/`):** estructura Next.js scaffolded, UI aún no implementada

## Arquitectura
- **Backend:** FastAPI (Python 3.11+) en `/backend` → aún por implementar
- **Frontend:** Next.js 14 App Router en `/frontend` → aún por implementar
- **MVP:** Streamlit en `/mvp` → funcional hoy
- **Vector DB:** ChromaDB embedded (`./data/chroma_db`) → Qdrant para producción
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` via sentence-transformers (118MB, descarga automática, CPU)
- **LLM:** Groq API — `llama-3.1-8b-instant`; fallback: Gemini 1.5 Flash (Google AI Studio)
- **Cosine similarity threshold:** `< 0.7` (chunks por encima se descartan en retrieval)

## Flujo de Datos (MVP)
```
scrape() → chunk_articles() → embed_and_store()   ← ejecutar UNA SOLA VEZ (ingest.py)
                                                  ↓
                                            ChromaDB (data/chroma_db/)
                                                  ↓
ask_uendi(query) → retrieve() → build_context() → generate()   ← en cada request
```
- Chunk size: 1500 chars (~375 tokens), overlap: 200 chars (~50 tokens)
- Embeddings generados en batch al ingestar; NUNCA recalcularlos por request
- Historial de conversación: últimos 6 turnos pasados a Groq

## Comandos

### MVP (entrada principal)
```bash
# 1. Instalar dependencias
pip install -r mvp/requirements.txt

# 2. Copiar y completar variables de entorno
cp .env.example .env

# 3. Correr ingesta (primera vez, o cuando haya contenido nuevo)
python mvp/ingest.py

# 4. Iniciar UI
streamlit run mvp/app.py
```

### Backend FastAPI
```bash
cd backend && uvicorn app.main:app --reload
```

### Frontend Next.js
```bash
cd frontend && npm run dev
```

### Tests
```bash
# Backend (pytest, desde la raíz)
cd backend && pytest

# Un solo test
cd backend && pytest tests/test_chunker.py -v
```

## Reglas Críticas
1. NUNCA mezclar código de backend en el directorio frontend y viceversa
2. SIEMPRE escribir tests para el pipeline de ingestion (chunker, embedder, loader)
3. Los embeddings se generan UNA SOLA VEZ en ingestion, no en cada query
4. Toda función pública debe tener docstring en español
5. Variables de entorno SIEMPRE en .env (nunca hardcodear API keys)
6. El scraper debe respetar robots.txt y rate limiting (1 req/seg mínimo — `DELAY = 1.5` en ingest.py)
7. NUNCA llamar a APIs de pago en el loop de cada request del usuario
8. NUNCA usar la API de Anthropic en runtime (solo Claude Code para desarrollo)

## Variables de Entorno (.env)
```
GROQ_API_KEY=gsk_...          # console.groq.com — gratis
GOOGLE_API_KEY=...            # alternativa: aistudio.google.com — gratis
CHROMA_PATH=./data/chroma_db
SCRAPED_DATA_PATH=./data/scraped/ueno_articles.json
NEXT_PUBLIC_API_URL=http://localhost:8000   # frontend
```

## Frontend — Design System
Ver `design-system.md` para tokens completos. Resumen:
- **Colores:** primary `#F97316` (naranja), bg `#FAFAF9`, text `#18181B`
- **Tipografía:** Space Grotesk (headings), Inter (body), JetBrains Mono (código)
- **Prohibido:** azules/violetas, gradientes, glassmorphism, `backdrop-filter blur`
- **Border-radius:** botones 4px, bubbles 12px, cards 8px
- Todo componente debe implementar los 7 estados del checklist: default, hover, focus, loading, vacío, error, disabled

## API del Backend (diseño objetivo)
- `POST /api/v1/chat` → `{ query: string, history: Message[] }`
- `GET /api/v1/admin/documents`
- `GET /health`
