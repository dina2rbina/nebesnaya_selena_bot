import logging

import aiohttp

from bot.config import settings
from bot.prompts.selena import SELENA_SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=60)


class OpenRouterError(Exception):
    """Ошибка при обращении к OpenRouter API."""


async def generate_horoscope(
    name: str,
    birth_date: str,
    birth_time: str | None,
    birth_place: str,
) -> str:
    user_prompt = build_user_prompt(name, birth_date, birth_time, birth_place)
    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": SELENA_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    logger.info("Requesting horoscope for %r via model %s", name, settings.openrouter_model)

    try:
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            async with session.post(OPENROUTER_URL, json=payload, headers=headers) as response:
                if response.status != 200:
                    body = await response.text()
                    logger.error(
                        "OpenRouter returned HTTP %s: %s", response.status, body[:500]
                    )
                    raise OpenRouterError(f"HTTP {response.status}")

                data = await response.json()

    except aiohttp.ServerTimeoutError as e:
        logger.error("OpenRouter request timed out: %s", e)
        raise OpenRouterError("timeout") from e
    except aiohttp.ClientError as e:
        logger.error("OpenRouter network error: %s", e)
        raise OpenRouterError("network") from e

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        logger.error("Unexpected OpenRouter response structure: %s | data=%s", e, data)
        raise OpenRouterError("bad_response") from e

    logger.info("Horoscope generated successfully for %r (%d chars)", name, len(text))
    return text.strip()
