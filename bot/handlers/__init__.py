from aiogram import Dispatcher

from bot.handlers import horoscope, onboarding, profile, reset, start
from bot.middlewares.db import DbSessionMiddleware


def register_all_handlers(dp: Dispatcher) -> None:
    dp.update.outer_middleware(DbSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(onboarding.router)
    dp.include_router(profile.router)
    dp.include_router(horoscope.router)
    dp.include_router(reset.router)
