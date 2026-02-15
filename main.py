import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN
from db.engine import init_db
from handlers import start, survey
from utils.scheduler import ask_users_job

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # DB
    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Routers
    dp.include_routers(start.router, survey.router)

    # Shedulers
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(ask_users_job, "cron", hour=21, minute=0, args=[bot, dp])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
