from aiogram import F, Router, types
from datetime import datetime
from sqlalchemy import select

from db import session_maker, Task, get_daily_or_regular_tasks

router = Router()


@router.callback_query(F.data == "all_completed")
async def all_completed(call: types.CallbackQuery) -> None:
    """Marks all daily tasks as completed."""
    async with session_maker() as session:
        tasks = await get_daily_or_regular_tasks(
            call.from_user.id, daily=True, session=session
        )

        completed_date = datetime.utcnow()
        for task in tasks:
            task.completed = True
            task.completed_date = completed_date

        await session.commit()

    await call.message.answer("✅ Все ежедневные задачи выполнены!")
    # Approximate translation:
    # All daily tasks are completed!


@router.callback_query(F.data == "all_incompleted")
async def all_incompleted(call: types.CallbackQuery) -> None:
    """Marks all daily tasks as incompleted."""
    async with session_maker() as session:
        tasks = await get_daily_or_regular_tasks(
            call.from_user.id, daily=True, session=session
        )

        for task in tasks:
            task.completed = False
            task.completed_date = None

        await session.commit()

    await call.message.answer(
        "❌ Все ежедневные задачи больше не являются завершёнными."
    )
    # Approximate translation:
    # All daily tasks are no longer completed.

