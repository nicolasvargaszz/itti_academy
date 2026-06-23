"""
generator.py — Generación de respuestas usando Groq (Llama 3.1).

Historial: últimos 6 turnos para mantener contexto conversacional.
Temperature 0.1: respuestas consistentes y factuales para banca.
NUNCA llamar a APIs de pago en el loop de requests — solo Groq (gratuito).
"""
import os

from groq import Groq

GROQ_MODEL = "llama-3.1-8b-instant"

_SYSTEM_PROMPT = """Eres Uendi, el asistente virtual del Banco Ueno de Paraguay.

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE usando la información de los documentos de contexto proporcionados.
2. Si la información no está en el contexto, di exactamente: "No tengo información sobre eso en este momento. Te recomiendo contactar a nuestro equipo o visitar ayuda.ueno.com.py"
3. NUNCA inventes tasas de interés, montos, plazos ni condiciones.
4. Cita siempre la fuente al final con el formato: "Fuente: [título] - [URL]"
5. Responde en español paraguayo, de manera amigable y concisa.
6. Si el usuario saluda, responde amigablemente antes de ofrecer ayuda."""


class Generator:
    """Wrapper de Groq API. Se instancia una sola vez al arrancar el servidor."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY no está configurada en .env")
        self._client = Groq(api_key=api_key)

    def generate(self, query: str, context: str, history: list[dict] | None = None) -> str:
        """
        Genera respuesta basada en el contexto recuperado.
        history: lista de {role: 'user'|'assistant', content: str}
        """
        messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]
        if history:
            messages.extend(history[-6:])
        messages.append({
            "role": "user",
            "content": f"CONTEXTO DE DOCUMENTOS:\n{context}\n\nPREGUNTA DEL USUARIO:\n{query}",
        })
        response = self._client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,  # type: ignore[arg-type]
            temperature=0.1,
            max_tokens=800,
        )
        return response.choices[0].message.content or ""
