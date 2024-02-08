from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from db import Task, get_daily_or_regular_tasks
from handlers.tasks.show_task import ShowTask

router = Router()


class Pagination(CallbackData, prefix="pag", arbitrary_types_allowed=True):
    action: str
    page: int
    owner_id: int
    daily: bool


async def get_paginated_tasks(
    message: types.Message, page: int = 0,
    owner_id: int = None, daily: bool = False
) -> tuple[InlineKeyboardBuilder, str, int]:
    """Returns tuple with `InlineKeyboardBuilder` with paginated
    tasks, string of this tasks and their `owner_id`."""
    # Getting user's tasks
    owner_id = owner_id or message.from_user.id

    tasks = await get_daily_or_regular_tasks(owner_id, daily=daily)

    builder = InlineKeyboardBuilder()
    limit = 5
    start_offset = int(page * limit)
    end_offset = start_offset + limit

    # Adding create task and mark all as completed buttons
    if page == 0:
        builder.row(types.InlineKeyboardButton(
            text="➕ Создать задачу", callback_data="create"
        ))

        if daily:
            for task in tasks:
                if not task.completed:
                    builder.row(types.InlineKeyboardButton(
                        text="✅ Пометить все выполненными",
                        callback_data="all_completed"
                    ))
                    break
            else:
                builder.row(types.InlineKeyboardButton(
                    text="❌ Пометить все невыполненными",
                    callback_data="all_incompleted"
                ))

    result = ""
    for task in tasks[start_offset:end_offset]:
        completed = "✅" if task.completed else "❌"
        line = f"{completed}{tasks.index(task) + 1}. {task.name}"
        builder.row(types.InlineKeyboardButton(
            text=(f"{line}..." if len(line) > 50 else line),
            callback_data=ShowTask(id=task.id).pack()
        ))
        result += line + "\n"

    if not result:
        return (builder, result, owner_id)

    # Navigation
    buttons_row = []
    if page > 0:
        buttons_row.append(types.InlineKeyboardButton(
            text="⬅️",
            callback_data=Pagination(
                action="prev", page=page - 1, owner_id=owner_id, daily=daily
            ).pack()
        ))
    if end_offset < len(tasks):
        buttons_row.append(types.InlineKeyboardButton(
            text="➡️",
            callback_data=Pagination(
                action="next", page=page + 1, owner_id=owner_id, daily=daily
            ).pack()
        ))
    else:
        buttons_row.append(types.InlineKeyboardButton(
            text="➡️", callback_data=Pagination(
                action="next", page=0, owner_id=owner_id, daily=daily
            ).pack()
        ))
    builder.row(*buttons_row)

    return (builder, result, owner_id)


@router.callback_query(Pagination.filter())
async def navigate(
    call: types.CallbackQuery, callback_data: Pagination
) -> None:
    """Edites reply markup according passed `callback_data`."""
    paginator, tasks, owner_id = await get_paginated_tasks(
        call.message, callback_data.page, callback_data.owner_id,
        callback_data.daily
    )

    if callback_data.daily:
        await call.message.edit_text(
            f"Ежедневные задачи: \n\n{tasks}",
            inline_message_id=call.inline_message_id
        )
    else:
        await call.message.edit_text(
            f"Задачи: \n\n{tasks}", inline_message_id=call.inline_message_id
        )

    await call.message.edit_reply_markup(
        call.inline_message_id,
        reply_markup=paginator.as_markup()
    )
