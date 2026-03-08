from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import get_user_by_telegram_id

router = Router(name="profile")


@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)

    if not user:
        await message.answer(
            "У меня пока нет твоих данных.\n\n"
            "Напиши /start — и мы познакомимся 🌙"
        )
        return

    time_str = user.birth_time if user.birth_time else "не указано"
    await message.answer(
        f"✨ Твой астрологический профиль:\n\n"
        f"Имя: {user.name}\n"
        f"Дата рождения: {user.birth_date}\n"
        f"Время рождения: {time_str}\n"
        f"Место рождения: {user.birth_place}\n\n"
        f"Напиши /horoscope — и я составлю твой персональный гороскоп."
    )
