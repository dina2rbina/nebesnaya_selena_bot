from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

skip_birth_time_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Не знаю / пропустить", callback_data="skip_birth_time")]
    ]
)

confirm_reset_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, сбросить", callback_data="confirm_reset"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel_reset"),
        ]
    ]
)
