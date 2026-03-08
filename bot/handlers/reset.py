from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.onboarding import confirm_reset_kb
from bot.services.user_service import delete_user, get_user_by_telegram_id

router = Router(name="reset")


@router.message(Command("reset"))
async def cmd_reset(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)

    if not user:
        await message.answer(
            "У меня нет твоих данных — сбрасывать нечего 🌙\n"
            "Напиши /start чтобы создать профиль."
        )
        return

    await message.answer(
        f"Ты хочешь удалить свой профиль?\n\n"
        f"Имя: {user.name}\n"
        f"Дата рождения: {user.birth_date}\n"
        f"Место рождения: {user.birth_place}\n\n"
        f"После сброса данные будут удалены безвозвратно.",
        reply_markup=confirm_reset_kb,
    )


@router.callback_query(F.data == "confirm_reset")
async def confirm_reset(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    deleted = await delete_user(session, callback.from_user.id)
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)

    if deleted:
        await callback.message.answer(
            "Профиль удалён 🌑\n\n"
            "Если захочешь вернуться — напиши /start, и мы начнём заново."
        )
    else:
        await callback.message.answer("Профиль не найден — возможно, уже был удалён.")

    await callback.answer()


@router.callback_query(F.data == "cancel_reset")
async def cancel_reset(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Отмена. Твой профиль в сохранности ✨")
    await callback.answer()
