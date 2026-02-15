from sqlalchemy import select
from .engine import SessionMaker
from .models import User, DailyAnswer, Note


async def add_user(user_id: int, username: str | None):
    async with SessionMaker() as session:
        user = await session.get(User, user_id)
        if not user:
            session.add(User(user_id=user_id, username=username))
            await session.commit()


async def save_answer(user_id: int, text: str):
    async with SessionMaker() as session:
        session.add(DailyAnswer(user_id=user_id, answer_text=text))
        await session.commit()


async def get_all_user_ids():
    async with SessionMaker() as session:
        result = await session.execute(select(User.user_id))
        return result.scalars().all()


async def get_all_answers():
    async with SessionMaker() as session:
        result = await session.execute(select(DailyAnswer.user_id, DailyAnswer.answer_text))
        return result.scalars().all()

async def save_note(user_id: int, text: str):
    async with SessionMaker() as session:
        session.add(Note(user_id=user_id, content=text))
        await session.commit()
