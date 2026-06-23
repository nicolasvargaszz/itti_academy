"""
retriever.py — Búsqueda semántica contra ChromaDB.

Carga el modelo de embeddings UNA SOLA VEZ en __init__.
Threshold 0.7: descarta chunks con distancia coseno >= 0.7.
"""
import chromadb
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
_DISTANCE_THRESHOLD = 0.7


class Retriever:
    """Encapsula el modelo de embeddings y la colección ChromaDB."""

    def __init__(self, collection: chromadb.Collection) -> None:
        self._model = SentenceTransformer(EMBED_MODEL)
        self._collection = collection

    @property
    def chunk_count(self) -> int:
        """Número total de chunks indexados."""
        return self._collection.count()

    def retrieve(self, query: str, n_results: int = 4) -> list[dict]:
        """
        Retorna los chunks más relevantes para la query.
        Filtra por distancia coseno < 0.7 para evitar contexto irrelevante.
        """
        embedding = self._model.encode([query])[0].tolist()
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if dist < _DISTANCE_THRESHOLD:
                chunks.append({
                    "text": doc,
                    "metadata": meta,
                    "score": round(1 - dist, 4),
                })
        return chunks
