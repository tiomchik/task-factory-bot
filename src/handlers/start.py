from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from .tasks.create import create_task
from db import session_maker, User

router = Router()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext) -> None:
    """`/start`"""
    # Creating a new user
    async with session_maker() as session:
        stmt = select(User).where(User.id==message.from_user.id)
        previous_user = await session.execute(stmt)

        if not previous_user.all():
            user = User(id=message.from_user.id)
            session.add(user)
            await session.commit()

    # Message
    await message.answer(
        "Привет! Данный бот может помочь вам создать список задач"
        " и отслеживать их выполнение. Давайте создадим вашу "
        "первую задачу: \n\n",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # Approximate translation:
    # Hi! This bot can help you create a list of tasks and track their 
    # completion.
    # Let's create a your first task:
    await create_task(message, state)
