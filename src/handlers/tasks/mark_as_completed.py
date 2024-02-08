from aiogram import F, Router, types
from datetime import datetime

from . import TaskControl
from db import session_maker, get_task_by_id

router = Router()


@router.callback_query(TaskControl.filter(F.action == "mark_as_completed"))
async def mark_as_completed(
    call: types.CallbackQuery, callback_data: TaskControl
) -> None:
    """Marks as completed a task with passed `task_id` in `callback_data`."""
    async with session_maker() as session:
        task = await get_task_by_id(callback_data.task_id, session=session)

        task.completed = True
        task.completed_date = datetime.utcnow()

        await session.commit()

    # Formatting fields
    reward = ""
    if task.reward:
        reward = f"Теперь вы можете наградить себя: \n\n🏆 {task.reward}"
        # Approximate translation:
        # Now you can reward yourself: \n\n🏆 {task.reward}

    await call.message.answer(f"✅ Задача _{task.name}_ выполнена! {reward}")
    # Approximate translation:
    # Task __{task.name} completed!


@router.callback_query(TaskControl.filter(F.action == "mark_as_incompleted"))
async def mark_as_incompleted(
    call: types.CallbackQuery, callback_data: TaskControl
) -> None:
    """Marks as incompleted a task with passed `task_id` in `callback_data`.
    """
    async with session_maker() as session:
        task = await get_task_by_id(callback_data.task_id, session=session)

        task.completed = False
        task.completed_date = None

        await session.commit()

    await call.message.answer(
        f"❌ Задача _{task.name}_ теперь является не выполненной."
    )
    # Approximate translation:
    # Task _{task.name }_ is now incomplete.
