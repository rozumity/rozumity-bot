from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from db.requests import get_all_user_ids
from utils.states import SurveyStates

async def ask_users_job(bot, dp):
    user_ids = await get_all_user_ids()
    for uid in user_ids:
        try:
            state_context = FSMContext(
                storage=dp.storage,
                key=StorageKey(chat_id=uid, user_id=uid, bot_id=bot.id)
            )
            await state_context.set_state(SurveyStates.waiting_for_answer)
            await bot.send_message(uid, "How was your day? I'm waiting for your report!")
        except Exception as e:
            print(f"Failed to send message: {uid}: {e}")
