#!/bin/bash
set -e

# Si no existe ChromaDB, correr la ingesta automáticamente en el primer arranque
if [ ! -d "/app/data/chroma_db" ]; then
    echo "================================================"
    echo "  Primera vez: corriendo pipeline de ingesta..."
    echo "  Esto tarda ~15 min (scraping + embeddings)"
    echo "================================================"
    python mvp/ingest.py
fi

echo "Iniciando Uendi RAG en http://0.0.0.0:8501"
exec streamlit run mvp/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true
