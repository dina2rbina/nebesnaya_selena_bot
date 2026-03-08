import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.openrouter_service import OpenRouterError, generate_horoscope
from bot.services.user_service import get_user_by_telegram_id
from bot.states.onboarding import OnboardingStates

logger = logging.getLogger(__name__)

router = Router(name="horoscope")

_ERROR_MESSAGES = {
    "timeout": "Звёзды молчат дольше обычного — сервис не отвечает. Попробуй через несколько минут 🌙",
    "network": "Кажется, что-то мешает нашей связи. Попробуй ещё раз чуть позже ✨",
    "bad_response": "Получила странный ответ от звёзд. Попробуй ещё раз 🌟",
}
_ERROR_DEFAULT = "Что-то пошло не так при составлении гороскопа. Попробуй позже 🌙"


@router.message(Command("horoscope"))
async def cmd_horoscope(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)

    if not user:
        await message.answer(
            "Чтобы составить твой персональный гороскоп, мне нужно сначала познакомиться с тобой.\n\n"
            "Напиши /start — и мы начнём 🌙"
        )
        await state.set_state(OnboardingStates.waiting_for_name)
        return

    await message.answer(
        f"Читаю твою карту, {user.name}...\n"
        f"Это займёт около минуты ✨"
    )
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        horoscope_text = await generate_horoscope(
            name=user.name,
            birth_date=user.birth_date,
            birth_time=user.birth_time,
            birth_place=user.birth_place,
        )
    except OpenRouterError as e:
        error_key = str(e)
        error_msg = _ERROR_MESSAGES.get(error_key, _ERROR_DEFAULT)
        logger.warning("OpenRouterError for user %s: %s", message.from_user.id, error_key)
        await message.answer(error_msg)
        return

    await message.answer(horoscope_text)
