FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema para sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY mvp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descargar el modelo de embeddings durante el build
# (evita la descarga de 118MB en el primer arranque del contenedor)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copiar código fuente
COPY mvp/ ./mvp/

# Copiar entrypoint
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

EXPOSE 8501

ENV ANONYMIZED_TELEMETRY=False
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./docker-entrypoint.sh"]
