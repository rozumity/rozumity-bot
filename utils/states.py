from aiogram.fsm.state import StatesGroup, State


class SurveyStates(StatesGroup):
    waiting_for_answer = State()
    waiting_for_note = State()
