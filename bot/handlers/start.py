from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import get_user_by_telegram_id
from bot.states.onboarding import OnboardingStates

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    user = await get_user_by_telegram_id(session, message.from_user.id)

    if user:
        await message.answer(
            f"С возвращением, {user.name} ✨\n\n"
            f"Я помню тебя — твоя натальная карта хранится у меня.\n\n"
            f"Напиши /horoscope — и я составлю для тебя персональный гороскоп.\n"
            f"Или /profile — чтобы посмотреть сохранённые данные."
        )
        return

    await message.answer(
        "Привет. Я — Селена, твой персональный астролог.\n\n"
        "Я не даю обезличенных прогнозов — я работаю с твоей натальной картой.\n"
        "Для этого мне нужно узнать тебя немного ближе.\n\n"
        "Как тебя зовут?"
    )
    await state.set_state(OnboardingStates.waiting_for_name)
