from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_birth_place = State()
