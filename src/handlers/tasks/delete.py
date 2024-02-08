from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import TaskControl
from db import session_maker, get_task_by_id
from .show_task import ShowTask

router = Router()


@router.callback_query(TaskControl.filter(F.action == "delete"))
async def delete_task(
    call: types.CallbackQuery, callback_data: TaskControl
) -> None:
    """Re-asks user about deleting task and deletes it according to answer."""
    builder = InlineKeyboardBuilder()
    yes_btn = types.InlineKeyboardButton(
        text="✅ Да", callback_data=TaskControl(
            action="confirmed_delete", task_id=callback_data.task_id
        ).pack()
    )
    no_btn = types.InlineKeyboardButton(
        text="❌ Нет", callback_data=ShowTask(id=callback_data.task_id).pack()
    )
    builder.row(yes_btn, no_btn)

    await call.message.answer(
        "Вы уверены что хотите удалить данную задачу?",
        reply_markup=builder.as_markup()
    )
    # Approximate translation:
    # Are you sure to delete this task?


@router.callback_query(TaskControl.filter(F.action == "confirmed_delete"))
async def confirmed_delete_task(
    call: types.CallbackQuery, callback_data: TaskControl
) -> None:
    """Deletes the task after confirmation."""
    async with session_maker() as session:
        task = await get_task_by_id(callback_data.task_id, session=session)

        await session.delete(task)
        await session.commit()

    await call.message.edit_text("✅ Задача успешно удалена!")
    # Approximate translation:
    # The task was successfully deleted!
