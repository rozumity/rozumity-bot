from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.states import SurveyStates
from db.requests import save_answer, save_note
from db.requests import get_user_notes, get_user_answers

router = Router()

# --- 1. COMMANDS (Highest Priority) ---

@router.message(Command("note"))
async def cmd_note(message: types.Message, state: FSMContext):
    # This handler must be above any generic message handlers
    await state.set_state(SurveyStates.waiting_for_note)
    await message.answer("I'm listening. Describe your feelings and events:")


@router.message(Command("my_notes"))
async def view_notes(message: types.Message):
    notes = await get_user_notes(message.from_user.id)
    if not notes:
        return await message.answer("Заметок пока нет.")
    
    note = notes[0]
    date_str = note.created_at.strftime("%d.%m.%Y %H:%M")
    text = f"📝 <b>Заметка (из /note)</b>\n📅 {date_str}\n\n{note.content}"
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_pagination_keyboard(0, len(notes), "note"))


@router.message(Command("my_answers"))
async def view_answers(message: types.Message):
    answers = await get_user_answers(message.from_user.id)
    if not answers:
        return await message.answer("Отчетов пока нет.")
    
    ans = answers[0]
    date_str = ans.created_at.strftime("%d.%m.%Y")
    text = f"📊 <b>Evening Report for </b>\n📅 {date_str}\n\n{ans.answer_text}"
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_pagination_keyboard(0, len(answers), "ans"))

# --- 2. FSM STATE HANDLERS (Waiting for specific input) ---

@router.message(SurveyStates.waiting_for_note, F.text)
async def handle_custom_note(message: types.Message, state: FSMContext):
    await save_note(message.from_user.id, message.text)
    await message.answer("Your thoughts have been saved in a separate notebook. Thank you!")
    await state.clear()


@router.message(SurveyStates.waiting_for_answer, F.text)
async def handle_daily_answer(message: types.Message, state: FSMContext):
    # This now only triggers IF the bot asked "How was your day?"
    await save_answer(message.from_user.id, message.text)
    await message.answer("Recorded the report! Have a good evening.")
    await state.clear()

# --- 3. PAGINATION & HELPERS ---

def get_pagination_keyboard(index: int, total: int, type_prefix: str):
    builder = InlineKeyboardBuilder()
    if index > 0:
        builder.button(text="⬅️ Back", callback_data=f"{type_prefix}:{index - 1}")
    else:
        builder.button(text="❌", callback_data="ignore")

    builder.button(text=f"{index + 1} / {total}", callback_data="ignore")

    if index < total - 1:
        builder.button(text="Next ➡️", callback_data=f"{type_prefix}:{index + 1}")
    else:
        builder.button(text="❌", callback_data="ignore")

    builder.adjust(3)
    return builder.as_markup()


@router.callback_query(F.data.startswith("note:") | F.data.startswith("ans:"))
async def process_pagination(callback: types.CallbackQuery):
    prefix, index = callback.data.split(":")
    index = int(index)
    user_id = callback.from_user.id

    if prefix == "note":
        data = await get_user_notes(user_id)
        title = "📝 <b>Note</b>"
    else:
        data = await get_user_answers(user_id)
        title = "📊 <b>Evening Report</b>"

    item = data[index]
    date_str = item.created_at.strftime("%d.%m.%Y %H:%M")
    content = item.content if prefix == "note" else item.answer_text
    new_text = f"{title}\n📅 {date_str}\n\n{content}"

    try:
        await callback.message.edit_text(new_text, parse_mode="HTML", reply_markup=get_pagination_keyboard(index, len(data), prefix))
    except Exception:
        await callback.answer()


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: types.CallbackQuery):
    await callback.answer()
