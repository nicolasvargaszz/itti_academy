"""
guardrails.py — Validación de entrada antes de llamar al LLM.

Evita prompts vacíos, excesivamente largos o con patrones de prompt injection.
Rápido y sin dependencias externas — no agrega latencia perceptible.
"""
from fastapi import HTTPException

_MAX_QUERY_LEN = 500
_MIN_QUERY_LEN = 2

_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "jailbreak",
]


def validate_query(query: str) -> None:
    """
    Valida la query del usuario.
    Lanza HTTPException 400 si no cumple las reglas.
    """
    stripped = query.strip()

    if len(stripped) < _MIN_QUERY_LEN:
        raise HTTPException(status_code=400, detail="La consulta es demasiado corta.")

    if len(stripped) > _MAX_QUERY_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"La consulta supera los {_MAX_QUERY_LEN} caracteres permitidos.",
        )

    lower = stripped.lower()
    for pattern in _INJECTION_PATTERNS:
        if pattern in lower:
            raise HTTPException(
                status_code=400,
                detail="Consulta no permitida.",
            )
