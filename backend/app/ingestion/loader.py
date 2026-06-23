"""
loader.py — Abre la colección ChromaDB existente en modo lectura.

Se llama una sola vez al arrancar uvicorn; la colección se reutiliza
en todos los requests sin reconectar.
"""
import chromadb

COLLECTION_NAME = "uendi_knowledge"


def load_collection(chroma_path: str) -> chromadb.Collection:
    """
    Abre la colección ya indexada.
    Lanza ValueError si no existe — hay que ejecutar ingest.py primero.
    """
    client = chromadb.PersistentClient(path=chroma_path)
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        raise ValueError(
            f"Colección '{COLLECTION_NAME}' no encontrada en {chroma_path}. "
            "Ejecutá: python mvp/ingest.py"
        )
