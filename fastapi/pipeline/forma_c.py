import logging

from cognitive import router as cognitive_router

logger = logging.getLogger(__name__)


FORMA_C_SYSTEM_PROMPT = """
Eres Forma C dentro de OFFICINA.

Tarea:
Reescribe el mensaje del operador en una instrucción clara, breve y operacional.

Reglas:
- No respondas la tarea.
- No agregues hechos nuevos.
- No inventes contexto.
- Conserva el idioma del operador.
- Si el mensaje ya es claro, devuélvelo casi igual.
- Devuelve solo el texto aclarado.
""".strip()


async def clarify_task(message: str) -> str:
    clean = (message or "").strip()
    if not clean:
        return ""

    messages = [
        {"role": "system", "content": FORMA_C_SYSTEM_PROMPT},
        {"role": "user", "content": clean},
    ]

    try:
        result = await cognitive_router.complete(messages)
        clarified = (result.get("text") or "").strip()
        if clarified:
            return clarified
    except Exception as e:
        logger.error(f"[forma_c] clarification failed: {e}")

    return clean
