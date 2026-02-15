from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.states import SurveyStates
from db.requests import save_answer, save_note

router = Router()


@router.message(SurveyStates.waiting_for_answer, F.text)
async def handle_daily_answer(message: types.Message, state: FSMContext):
    await save_answer(message.from_user.id, message.text)
    await message.answer("Recorded the report! Have a good evening.")
    await state.clear()


@router.message(Command("note"))
async def cmd_note(message: types.Message, state: FSMContext):
    await state.set_state(SurveyStates.waiting_for_note)
    await message.answer("I'm listening. Describe your feelings and events:")


@router.message(SurveyStates.waiting_for_note, F.text)
async def handle_custom_note(message: types.Message, state: FSMContext):
    await save_note(message.from_user.id, message.text)
    await message.answer("Your thoughts have been saved in a separate notebook. Thank you!")
    await state.clear()
