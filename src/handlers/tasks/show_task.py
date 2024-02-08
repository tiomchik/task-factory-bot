from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

from db import get_task_by_id
from . import TaskControl

router = Router()


class ShowTask(CallbackData, prefix="showtask"):
    id: int


@router.callback_query(ShowTask.filter())
async def show_task(
    call: types.CallbackQuery, callback_data: ShowTask
) -> None:
    """Shows a task with passed id."""
    task = await get_task_by_id(callback_data.id)

    # Formatting strings and making buttons
    daily_btn = types.InlineKeyboardButton(
        text="🗓 Сделать ежедневной",
        callback_data=TaskControl(
            action="mark_as_daily", task_id=task.id
        ).pack()
    )
    return_to_tasks = "return_to_tasks"
    if task.daily:
        daily_btn = types.InlineKeyboardButton(
            text="📝 Сделать обычной",
            callback_data=TaskControl(
                action="mark_as_regular", task_id=task.id
            ).pack()
        )
        return_to_tasks = "return_to_daily_tasks"

    if task.completed:
        completed = ("✅ Выполнено "
            f"{task.completed_date.strftime('%d-%m-%Y %H:%M')}\n")
        completed_btn = types.InlineKeyboardButton(
            text="❌ Не выполнено",
            callback_data=TaskControl(
                action="mark_as_incompleted", task_id=task.id
            ).pack()
        )
    else:
        completed = "❌ Не выполнено\n"
        completed_btn = types.InlineKeyboardButton(
            text="✅ Выполнено", callback_data=TaskControl(
                action="mark_as_completed", task_id=task.id
            ).pack()
        )

    deadline = ""
    if task.deadline:
        now = datetime.utcnow()
        remaining: int = task.deadline - now

        # Declination of remaining days for comfortable reading in Russian
        state = ""
        if remaining.days < 0:
            state = "истёк! "
        elif remaining.days == 0:
            state = "поторопитесь, осталось меньше суток! "
        elif remaining.days == 7:
            state = "осталась неделя. "
        elif remaining.days < 7:
            if remaining.days == 1:
                state = f"поторопитесь, остался {remaining.days} день! "
            elif 1 < remaining.days < 5:
                state = f"осталось {remaining.days} дня/суток. "
            else:
                state = f"осталось {remaining.days} дней/суток. "

        deadline = (f"Крайний срок: 🕓 *{state}*"
        f"{task.deadline.strftime('%d-%m-%Y %H:%M')}\n")

    reward = ""
    if task.reward:
        reward = f"Награда за выполнение: 🏆 {task.reward}"

    # Buttons
    edit_btn = types.InlineKeyboardButton(
        text="✏️ Редактировать",
        callback_data=TaskControl(action="edit", task_id=task.id).pack()
    )
    delete_btn = types.InlineKeyboardButton(
        text="🗑 Удалить",
        callback_data=TaskControl(action="delete", task_id=task.id).pack()
    )
    return_btn = types.InlineKeyboardButton(
        text="⬅️ Вернуться к списку задач", callback_data=return_to_tasks
    )

    builder = InlineKeyboardBuilder()
    builder.row(completed_btn, daily_btn, width=1)
    builder.row(edit_btn, delete_btn)
    builder.row(return_btn)

    await call.message.edit_text(
        f"Задача: *{task.name}*\nСостояние: {completed}"
        f"{deadline}{reward}"
    )
    await call.message.edit_reply_markup(
        call.inline_message_id, reply_markup=builder.as_markup()
    )
