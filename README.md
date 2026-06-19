# Uendi RAG — Sistema de Conocimiento para Chatbot Bancario

> Proyecto académico desarrollado para el curso de Inteligencia Artificial Generativa — ITTI Academy.
> Propuesta técnica para evolucionar a **Uendi**, el chatbot del **Banco Ueno (Paraguay)**, hacia una arquitectura RAG.

---

## ¿Qué problema resuelve?

Uendi, como muchos chatbots bancarios, tiene el conocimiento "hardcodeado" en el modelo. Cada vez que el banco lanza un producto nuevo, cambia una tasa o actualiza una condición, alguien tiene que reconfigurar el bot manualmente.

Este proyecto implementa un sistema **RAG (Retrieval-Augmented Generation)** que:

1. **Scrapea** automáticamente el centro de ayuda oficial (`ayuda.ueno.com.py`)
2. **Indexa** los artículos en una base de datos vectorial
3. **Responde** preguntas inyectando solo los fragmentos relevantes en el prompt del LLM

Cuando el banco actualiza su documentación, basta con re-correr la ingesta — sin reentrenar el modelo.

---

## Demo

```
Usuario: ¿Qué es la tarjeta de débito virtual?
Uendi:   La tarjeta virtual de ueno es una tarjeta de débito Mastercard
         internacional alojada en tu celular dentro de la app ueno. Está
         ligada a tu Caja de ahorro...
         Fuente: ¿Qué es una tarjeta de débito virtual? - ayuda.ueno.com.py
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     PIPELINE DE INGESTA                      │
│                   (se corre una sola vez)                    │
│                                                             │
│  ayuda.ueno.com.py  →  scraper  →  chunker  →  embedder    │
│       (561 artículos)    (BS4)    (1500 chars)  (ST local)  │
│                                        ↓                    │
│                                   ChromaDB                  │
│                                  (597 chunks)               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE DE CONSULTA                      │
│                    (en cada request)                        │
│                                                             │
│  Usuario → query embedding → ChromaDB search → top-4 chunks │
│                                    ↓                        │
│              build_context() → Groq API (Llama 3.1) → resp  │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

### AI / LLM Stack

| Componente | Tecnología | Costo |
|---|---|---|
| Embeddings | `sentence-transformers` — `paraphrase-multilingual-MiniLM-L12-v2` | $0 (local, CPU) |
| Vector DB | ChromaDB embedded | $0 (in-process) |
| LLM | Groq API — `llama-3.1-8b-instant` | $0 (free tier) |
| LLM alternativo | Google AI Studio — Gemini 1.5 Flash | $0 (free tier) |

El modelo de embeddings corre 100% en CPU sin API key. Soporte nativo en español.

### Backend / MVP
- **Python 3.12**
- **Streamlit** — UI del MVP (zero config)
- **FastAPI** — scaffold para la versión de producción
- **BeautifulSoup4 + requests** — scraper web

### Frontend (scaffold)
- **Next.js 14** App Router, TypeScript
- **Tailwind CSS + shadcn/ui**

### Infraestructura
- **Docker + Docker Compose** — deployment reproducible
- **ChromaDB** → migración a **Qdrant** para producción

---

## Desarrollo Asistido por IA — Claude Code

Este proyecto fue desarrollado íntegramente con **Claude Code Pro** (modelo `claude-sonnet-4-6`) como asistente de desarrollo.

### ¿Qué es Claude Code?

[Claude Code](https://claude.ai/code) es el CLI oficial de Anthropic. Funciona como un agente de software que puede leer, escribir y ejecutar código directamente en tu entorno, con acceso al sistema de archivos, terminal y herramientas de desarrollo.

### Skills (Slash Commands) utilizados

| Skill | Descripción | Uso en este proyecto |
|---|---|---|
| `/init` | Analiza el codebase y genera `CLAUDE.md` con documentación | Generó la documentación inicial del proyecto y arquitectura |
| `/model` | Configura el modelo de Claude | Configuró `claude-sonnet-4-6` con esfuerzo `max` |
| `/run` | Lanza la app y verifica que funciona en el browser | Verificó que Streamlit levantaba correctamente en `:8501` |
| `/code-review` | Revisa el diff en busca de bugs y mejoras | Revisión de seguridad del pipeline RAG |

### Herramientas internas de Claude Code usadas

- **`Bash`** — ejecutar pip, python, git, curl desde el agente
- **`Read / Write / Edit`** — crear y modificar todos los archivos del proyecto
- **`Monitor`** — observar el proceso de ingesta corriendo en background (570 artículos, ~15 min)
- **`Agent (Explore)`** — exploración del codebase para entender la estructura antes de editar

### MCP (Model Context Protocol)

Este proyecto utilizó el servidor MCP de **Google Drive** (`mcp__claude_ai_Google_Drive`) para acceder al documento de especificación del proyecto (`uendi.md`) almacenado en Google Docs. El MCP permitió que Claude Code leyera el documento directamente sin necesidad de descargarlo manualmente.

**¿Qué es MCP?** Model Context Protocol es el estándar abierto de Anthropic que permite conectar modelos de IA con fuentes de datos externas (Google Drive, GitHub, bases de datos, APIs) de forma segura y estandarizada.

### Workflow real de desarrollo con Claude Code

```
1. /init → generó CLAUDE.md con arquitectura y reglas del proyecto
2. Claude leyó uendi.md via Google Drive MCP para entender el contexto
3. Claude escribió mvp/ingest.py con el scraper de 3 niveles
4. Monitor tool → observó los 570 artículos siendo indexados en tiempo real
5. Claude debuggeó incompatibilidad groq==0.9.0 + httpx>=0.28 y la resolvió
6. Claude refactorizó rag.py para usar @st.cache_resource (Streamlit)
7. /run → verificó que la app levantaba y respondía en el browser
```

---

## Estructura del Proyecto

```
uendi-rag/
├── mvp/                    # MVP funcional (Streamlit)
│   ├── ingest.py           # Pipeline: scraping → chunking → embeddings → ChromaDB
│   ├── rag.py              # Motor RAG: RAGEngine class con retrieve/generate/ask
│   ├── app.py              # UI Streamlit
│   └── requirements.txt
│
├── backend/                # Scaffold FastAPI (producción)
│   └── app/
│       ├── ingestion/      # scraper, chunker, embedder, loader
│       ├── retrieval/      # retriever, reranker, augmenter
│       └── generation/     # generator, guardrails
│
├── frontend/               # Scaffold Next.js 14 (producción)
│   └── src/
│       └── components/
│           ├── chat/       # ChatInterface, MessageBubble, SourceCitation
│           └── admin/      # AdminPanel
│
├── scripts/                # Utilidades standalone
├── data/                   # Generado localmente — NO en git
│   ├── scraped/            # ueno_articles.json (561 artículos)
│   └── chroma_db/          # ChromaDB persistente (597 chunks)
│
├── Dockerfile
├── docker-compose.yml
├── docker-entrypoint.sh
├── .env.example
├── CLAUDE.md               # Instrucciones para Claude Code
└── design-system.md        # Tokens de diseño (colores, tipografía, componentes)
```

---

## Instalación y Uso Local

### Prerequisitos
- Python 3.12+
- Una API key gratuita de [Groq](https://console.groq.com) (100k tokens/día)

### Setup

```bash
# 1. Clonar el repositorio
git clone https://github.com/nicolasvargaszz/itti_academy.git
cd itti_academy

# 2. Crear entorno virtual
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r mvp/requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GROQ_API_KEY

# 5. Correr ingesta (primera vez — ~15 min)
python mvp/ingest.py

# 6. Iniciar la UI
streamlit run mvp/app.py
```

Abrir **http://localhost:8501**

---

## Deployment con Docker

### Opción A — Inicio automático (recomendado)

Si no existe `data/chroma_db/`, el contenedor corre la ingesta automáticamente al primer arranque.

```bash
cp .env.example .env
# Agregar GROQ_API_KEY en .env

docker compose up app
```

La primera vez tarda ~15 min (scraping + embeddings). Las siguientes son instantáneas.

### Opción B — Ingesta manual + app separados

```bash
# Paso 1: correr solo la ingesta
docker compose --profile ingest up ingest

# Paso 2: iniciar la app (ya tiene datos)
docker compose up app
```

### Variables de entorno requeridas

```bash
# .env
GROQ_API_KEY=gsk_...          # console.groq.com — gratis
CHROMA_PATH=./data/chroma_db
SCRAPED_DATA_PATH=./data/scraped/ueno_articles.json
```

---

## Datos técnicos del MVP

| Métrica | Valor |
|---|---|
| Artículos scrapeados | 561 |
| Chunks indexados | 597 |
| Dimensión de embeddings | 768 |
| Modelo de embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Tamaño del modelo | ~118 MB |
| Chunk size | 1500 chars (~375 tokens) |
| Chunk overlap | 200 chars (~50 tokens) |
| Cosine similarity threshold | < 0.7 |
| Chunks por query (top-k) | 4 |
| Historial de conversación | últimos 6 turnos |

---

## Contexto Académico

Este proyecto es la implementación práctica de una propuesta técnica académica que responde a:

> *¿Cómo puede un banco resolver el problema de desactualización de su chatbot sin reentrenar el LLM cada vez que cambia un producto?*

La respuesta es RAG: en lugar de "memorizar" el conocimiento en los pesos del modelo, se mantiene una base de documentos actualizada y se inyecta el contexto relevante en cada consulta.

Ver `uendi.md` para el documento técnico completo (fundamentos teóricos, análisis de riesgos, roadmap de producción).

---

## Roadmap

- [x] MVP funcional con Streamlit
- [x] Scraper de 3 niveles para `ayuda.ueno.com.py`
- [x] Pipeline de ingesta completo
- [x] Motor RAG con ChromaDB + Groq
- [x] Deployment con Docker
- [ ] Backend FastAPI con endpoints `/chat` y `/admin`
- [ ] UI Next.js 14 con design system completo
- [ ] Migración a Qdrant para producción
- [ ] Reranker semántico (cross-encoder)
- [ ] Búsqueda híbrida (densa + dispersa BM25)
- [ ] Panel de administración para re-ingestar sin reiniciar
