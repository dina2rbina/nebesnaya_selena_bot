import re
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.onboarding import skip_birth_time_kb
from bot.services.user_service import create_user
from bot.states.onboarding import OnboardingStates

router = Router(name="onboarding")

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def _validate_date(text: str) -> bool:
    if not DATE_RE.match(text):
        return False
    try:
        datetime.strptime(text, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def _validate_time(text: str) -> bool:
    if not TIME_RE.match(text):
        return False
    try:
        datetime.strptime(text, "%H:%M")
        return True
    except ValueError:
        return False


# ── Шаг 1: имя ────────────────────────────────────────────────────────────────

@router.message(OnboardingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Пожалуйста, напиши своё имя.")
        return
    if len(name) > 100:
        await message.answer("Имя слишком длинное. Напиши покороче.")
        return

    await state.update_data(name=name)
    await state.set_state(OnboardingStates.waiting_for_birth_date)
    await message.answer(
        f"Красивое имя, {name} 🌙\n\n"
        f"Теперь скажи мне: когда ты родилась?\n"
        f"Напиши дату в формате ДД.ММ.ГГГГ\n"
        f"Например: 15.04.1990"
    )


# ── Шаг 2: дата рождения ───────────────────────────────────────────────────────

@router.message(OnboardingStates.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not _validate_date(text):
        await message.answer(
            "Не могу распознать дату. Напиши в формате ДД.ММ.ГГГГ\n"
            "Например: 15.04.1990"
        )
        return

    await state.update_data(birth_date=text)
    await state.set_state(OnboardingStates.waiting_for_birth_time)
    await message.answer(
        f"Записала: {text} ✨\n\n"
        f"Ты знаешь время своего рождения?\n"
        f"Оно помогает точнее определить асцендент и дома.\n\n"
        f"Напиши в формате ЧЧ:ММ (например: 14:35)\n"
        f"Или нажми кнопку, если не знаешь.",
        reply_markup=skip_birth_time_kb,
    )


# ── Шаг 3: время рождения (текст) ─────────────────────────────────────────────

@router.message(OnboardingStates.waiting_for_birth_time)
async def process_birth_time(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not _validate_time(text):
        await message.answer(
            "Не могу распознать время. Напиши в формате ЧЧ:ММ\n"
            "Например: 14:35\n\n"
            "Или нажми кнопку «Не знаю / пропустить».",
            reply_markup=skip_birth_time_kb,
        )
        return

    await state.update_data(birth_time=text)
    await state.set_state(OnboardingStates.waiting_for_birth_place)
    await message.answer(
        f"Отлично, {text} — это важная деталь 🕐\n\n"
        f"И последнее: в каком городе ты родилась?\n"
        f"Напиши название города (и страну, если хочешь точнее)."
    )


# ── Шаг 3: время рождения (кнопка «пропустить») ───────────────────────────────

@router.callback_query(F.data == "skip_birth_time", OnboardingStates.waiting_for_birth_time)
async def skip_birth_time(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(birth_time=None)
    await state.set_state(OnboardingStates.waiting_for_birth_place)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Хорошо, обойдёмся без точного времени.\n\n"
        "И последнее: в каком городе ты родилась?\n"
        "Напиши название города (и страну, если хочешь точнее)."
    )
    await callback.answer()


# ── Шаг 4: место рождения → сохранение ───────────────────────────────────────

@router.message(OnboardingStates.waiting_for_birth_place)
async def process_birth_place(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    place = (message.text or "").strip()
    if not place:
        await message.answer("Напиши название города.")
        return
    if len(place) > 200:
        await message.answer("Название слишком длинное. Напиши покороче.")
        return

    data = await state.get_data()
    await create_user(
        session=session,
        telegram_id=message.from_user.id,
        name=data["name"],
        birth_date=data["birth_date"],
        birth_time=data.get("birth_time"),
        birth_place=place,
    )
    await state.clear()

    time_str = data.get("birth_time") or "не указано"
    await message.answer(
        f"Я записала всё, что нужно 🌟\n\n"
        f"Имя: {data['name']}\n"
        f"Дата рождения: {data['birth_date']}\n"
        f"Время рождения: {time_str}\n"
        f"Место рождения: {place}\n\n"
        f"Теперь я могу составить твой персональный гороскоп.\n"
        f"Напиши /horoscope — и я начну ✨"
    )
