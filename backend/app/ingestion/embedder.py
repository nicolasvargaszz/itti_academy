"""
embedder.py — Genera embeddings y los almacena en ChromaDB.

Descarga el modelo automáticamente la primera vez (~118MB).
Los embeddings se generan en batch UNA sola vez durante la ingesta.
NUNCA llamar este módulo en el loop de requests del usuario.
"""
import chromadb
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "uendi_knowledge"
_BATCH_SIZE = 100


def embed_and_store(chunks: list[dict], chroma_path: str) -> chromadb.Collection:
    """
    Genera embeddings para todos los chunks y los almacena en ChromaDB.
    Recrea la colección desde cero — idempotente.
    """
    if not chunks:
        raise ValueError("Sin chunks — ejecutá el scraper primero.")

    print(f"🤖 Cargando {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)

    print(f"🔢 Embeddings para {len(chunks)} chunks...")
    embeddings = model.encode(
        [c["text"] for c in chunks],
        show_progress_bar=True,
        batch_size=_BATCH_SIZE,
    )

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    for i in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[i : i + _BATCH_SIZE]
        collection.add(
            ids=[c["id"] for c in batch],
            embeddings=embeddings[i : i + _BATCH_SIZE].tolist(),
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"   Batch {i // _BATCH_SIZE + 1}/{-(-len(chunks) // _BATCH_SIZE)} ✓")

    print(f"🎉 {collection.count()} chunks indexados en {chroma_path}")
    return collection
