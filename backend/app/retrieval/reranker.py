"""
reranker.py — Reordenamiento de chunks por relevancia.

Implementación actual: ordena por score coseno descendente.
Extensión futura: cross-encoder con sentence-transformers/ms-marco-MiniLM.
"""


def rerank(chunks: list[dict], top_k: int = 3) -> list[dict]:
    """
    Reordena chunks por score y retorna los top_k.
    Score = 1 - distancia_coseno (mayor es más relevante).
    """
    return sorted(chunks, key=lambda c: c["score"], reverse=True)[:top_k]
