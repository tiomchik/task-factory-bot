from aiogram import F, Router, types

from . import TaskControl
from db import session_maker, get_task_by_id

router = Router()


@router.callback_query(TaskControl.filter(F.action == "mark_as_daily"))
async def mark_as_daily(
    call: types.CallbackQuery, callback_data: TaskControl
) -> None:
    """Marks as daily a task with passed `task_id` in `callback_data`."""
    async with session_maker() as session:
        task = await get_task_by_id(callback_data.task_id, session=session)

        task.daily = True
        task.deadline = None
        task.reward = None

        await session.commit()

    await call.message.answer(
        f"🗓 Задача _{task.name}_ теперь является ежедневной и "
        "будет отображаться в списке /daily."
    )
    # Approximate translation:
    # Task _{task.name }_ is now a daily and will be
    # displayed in the /daily list.


@router.callback_query(TaskControl.filter(F.action == "mark_as_regular"))
async def mark_as_regular(
    call: types.CallbackQuery, callback_data: TaskControl
) -> None:
    """Marks as regular a task with passed `task_id` in `callback_data`."""
    async with session_maker() as session:
        task = await get_task_by_id(callback_data.task_id, session=session)

        task.daily = False

        await session.commit()

    await call.message.answer(
        f"📝 Задача _{task.name}_ перестала быть ежедневной."
    )
    # Approximate translation:
    # Task _{task.name}_ has ceased to be daily.
