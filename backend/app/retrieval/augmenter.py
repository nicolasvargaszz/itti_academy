"""
augmenter.py — Construye el bloque de contexto para el prompt del LLM.

El formato [Documento N] con título, categoría, URL y contenido
permite que el LLM cite fuentes correctamente (regla 4 del system prompt).
"""


def build_context(chunks: list[dict]) -> str:
    """Formatea los chunks recuperados como contexto para el LLM."""
    if not chunks:
        return "No se encontraron documentos relevantes."
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        parts.append(
            f"[Documento {i}]\n"
            f"Título: {meta['title']}\n"
            f"Categoría: {meta['category']}\n"
            f"URL: {meta['source_url']}\n"
            f"Contenido:\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)
