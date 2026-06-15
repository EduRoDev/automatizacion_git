import logging
from openrouter import OpenRouter
from app.core.config import get_settings

logger = logging.getLogger(__name__)

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

SYSTEM_PROMPT = """Eres un revisor de código experto. Te dan el diff de un \
pull request y debes revisarlo. Enfócate en: bugs potenciales, problemas de \
seguridad, código que pueda romper algo, y malas prácticas claras. Sé conciso \
y concreto. Si el código está bien, dilo brevemente. No inventes problemas \
que no existen. Responde en español."""

async def review_diff(diff: str) -> str:
    settings = get_settings()
    api_key = settings.api_key
    if not api_key:
        logger.error("API key is not set in the environment variables.")
        return "Error: API key is not configured."

    async with OpenRouter (api_key=api_key) as client:
        response = await client.chat.send_async(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Revisa este diff:\n{diff}"}
            ],
        )

    return response.choices[0].message.content
