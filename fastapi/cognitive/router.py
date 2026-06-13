"""
Cognitive Router — fallback chain OFFICINA

Cadena: Vertex AI -> Groq -> NVIDIA -> OpenRouter -> Ollama

TODO (cuando schema BD cristalizado):
  Leer nodos contextual_type=system al arrancar.
  Construir chain dinamicamente desde BD via config.py.
  Migracion acotada a este modulo + config.py.
"""
import logging
from typing import Callable, Awaitable

from cognitive.providers import vertex, groq, nvidia, openrouter, ollama

logger = logging.getLogger(__name__)

# Cadena ordenada por calidad descendente
# Provisional — migrar a nodos system en BD
_CHAIN: list[tuple[str, Callable]] = [
    ("vertex",      vertex.complete),
    ("groq",        groq.complete),
    ("nvidia",      nvidia.complete),
    ("openrouter",  openrouter.complete),
    ("ollama",      ollama.complete),
]


async def complete(messages: list[dict], **kwargs) -> dict:
    """
    Intenta cada provider en orden.
    Retorna {provider, text} o lanza RuntimeError si todos fallan.
    """
    last_error: Exception | None = None
    for name, fn in _CHAIN:
        try:
            logger.info(f"[router] trying {name}")
            text = await fn(messages, **kwargs)
            logger.info(f"[router] success {name}")
            return {"provider": name, "text": text}
        except Exception as e:
            logger.warning(f"[router] {name} failed: {e}")
            last_error = e
            continue
    raise RuntimeError(f"All providers failed. Last error: {last_error}")
