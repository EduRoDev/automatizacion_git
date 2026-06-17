import logging
import asyncio
from openrouter import OpenRouter
from app.core.config import get_settings

logger = logging.getLogger(__name__)

MODEL = [
    "openai/gpt-oss-20b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "meta-llama/llama-4-scout:free",
    "openrouter/free",
]

TIMEOUT_SECONDS = 15

SYSTEM_PROMPT = """Eres un revisor de código experto. Recibes el diff de un \
pull request y debes revisarlo buscando: bugs potenciales, problemas de \
seguridad, código que pueda romper algo, y malas prácticas claras.

Respondes ÚNICAMENTE con un array JSON válido, sin texto antes ni después, \
sin bloques de markdown. Cada elemento del array es una observación con \
exactamente estos campos:
- "path": la ruta del archivo (string), tal como aparece en el diff
- "line": el número de línea en la versión NUEVA del archivo (entero)
- "comment": tu observación concreta y breve (string, en español)

Reglas importantes:
- Usa SOLO números de línea que correspondan a líneas agregadas o de \
contexto que aparecen en el diff. Nunca inventes líneas.
- Si el código no tiene problemas, responde con un array vacío: []
- No inventes observaciones para parecer útil. Calidad sobre cantidad.

Ejemplo de respuesta válida:
[{"path": "src/calc.py", "line": 12, "comment": "División sin validar cero"}]"""

async def review_diff(diff_text: str) -> str:
    settings = get_settings()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": diff_text},
    ]

    async with OpenRouter(api_key=settings.api_key) as client:
        for model in MODEL:
            try:
                logger.info("Intentando con el modelo %s...", model)
                response = await asyncio.wait_for(
                    client.chat.send_async(model=model, messages=messages),
                    timeout=TIMEOUT_SECONDS,
                )
                logger.info("El modelo %s respondió", model)
                return response.choices[0].message.content
            except asyncio.TimeoutError:
                logger.warning("El modelo %s superó el timeout de %ss, probando el siguiente",
                               model, TIMEOUT_SECONDS)
            except Exception:
                logger.warning("El modelo %s falló, probando el siguiente", model, exc_info=True)

    logger.error("Todos los modelos fallaron")
    return "[]"
