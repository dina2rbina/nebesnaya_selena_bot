import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database import close_db, engine
from bot.handlers import register_all_handlers

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    # Проверяем подключение к БД
    async with engine.connect() as conn:
        await conn.run_sync(lambda _: None)
    logger.info("Database connection OK")

    me = await bot.get_me()
    logger.info("Bot started: @%s (id=%s)", me.username, me.id)


async def on_shutdown(bot: Bot) -> None:
    await close_db()
    logger.info("Bot stopped")


async def run_health_server() -> None:
    """Minimal HTTP server so Railway web service health check passes."""
    port = int(os.environ.get("PORT", 8080))

    async def health(request: web.Request) -> web.Response:
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server listening on port %d", port)


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    register_all_handlers(dp)

    await run_health_server()

    logger.info("Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
