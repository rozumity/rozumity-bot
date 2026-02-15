from aiogram import Router, types
from aiogram.filters import CommandStart
from db.requests import add_user

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Hi! I'll be asking you every evening how your day was :)")
