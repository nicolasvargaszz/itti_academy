"""
rag.py — Motor RAG: Retrieval + Augmentation + Generation
"""
from pathlib import Path
import os
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent
CHROMA_PATH = str(_ROOT / "data" / "chroma_db")
COLLECTION_NAME = "uendi_knowledge"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """Eres Uendi, el asistente virtual del Banco Ueno de Paraguay.

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE usando la información de los documentos de contexto proporcionados.
2. Si la información no está en el contexto, di exactamente: "No tengo información sobre eso en este momento. Te recomiendo contactar a nuestro equipo o visitar ayuda.ueno.com.py"
3. NUNCA inventes tasas de interés, montos, plazos ni condiciones.
4. Cita siempre la fuente al final de tu respuesta con el formato: "Fuente: [título] - [URL]"
5. Responde en español paraguayo, de manera amigable y concisa.
6. Si el usuario saluda, responde amigablemente antes de ofrecer ayuda."""


class RAGEngine:
    """Motor RAG: carga modelos una sola vez y expone ask()."""

    def __init__(self):
        self.embed_model = SentenceTransformer(EMBED_MODEL)
        chroma = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = chroma.get_collection(COLLECTION_NAME)
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chunk_count(self) -> int:
        """Retorna la cantidad de chunks indexados."""
        return self.collection.count()

    def retrieve(self, query: str, n_results: int = 4) -> list[dict]:
        """Busca los chunks más relevantes para la pregunta."""
        query_embedding = self.embed_model.encode([query])[0].tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if dist < 0.7:
                chunks.append({"text": doc, "metadata": meta, "score": 1 - dist})
        return chunks

    def build_context(self, chunks: list[dict]) -> str:
        """Construye el bloque de contexto para el prompt."""
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
                f"Contenido:\n{chunk['text']}\n"
            )
        return "\n---\n".join(parts)

    def generate(self, query: str, context: str, history: list[dict] | None = None) -> str:
        """Genera respuesta usando Groq (Llama 3.1)."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history[-6:])
        messages.append({
            "role": "user",
            "content": f"CONTEXTO DE DOCUMENTOS:\n{context}\n\nPREGUNTA DEL USUARIO:\n{query}",
        })
        response = self.groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=800,
        )
        return response.choices[0].message.content

    def ask(self, query: str, history: list[dict] | None = None) -> tuple[str, list[dict]]:
        """Función principal: pregunta → (respuesta, chunks_usados)."""
        chunks = self.retrieve(query)
        context = self.build_context(chunks)
        answer = self.generate(query, context, history)
        return answer, chunks
