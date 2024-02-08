from aiogram import F, Router, types
from aiogram.filters import Command

from utils.paginator import get_paginated_tasks

router = Router()


@router.message(Command("tasks"))
async def get_task_list(message: types.Message) -> None:
    """Gets user's task list and send message with them."""
    builder, tasks, owner_id = await get_paginated_tasks(message)

    # Showing task list
    if not tasks:
        await message.answer(
            "Задачи: \n\nЗадачи не найдены. "
            "Кажется, у вас появилось свободное время. :)",
            reply_markup=builder.as_markup()
        )
        # Approximate translation:
        # Tasks: No tasks were found.
        # It seems that you have some free time. :)
    else:
        await message.answer(
            f"Задачи: \n\n{tasks}", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == "return_to_tasks")
async def callback_get_task_list(call: types.CallbackQuery) -> None:
    """`get_task_list` for callbacks."""
    builder, tasks, owner_id = await get_paginated_tasks(
        call.message, owner_id=call.from_user.id
    )

    if not tasks:
        await call.message.edit_text(
            "Задачи: \n\nЗадачи не найдены. "
            "Кажется, у вас появилось свободное время. :)"
        )
    else:
        await call.message.edit_text(f"Задачи: \n\n{tasks}")

    await call.message.edit_reply_markup(
        call.inline_message_id, reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "return_to_daily_tasks")
async def callback_get_task_list(call: types.CallbackQuery) -> None:
    """`get_task_list` for callbacks."""
    builder, tasks, owner_id = await get_paginated_tasks(
        call.message, owner_id=call.from_user.id, daily=True
    )

    if not tasks:
        await call.message.edit_text(
            "Ежедневные задачи: \n\nЕжедневные задачи не найдены. "
            "Кажется, у вас появилось свободное время. :)"
        )
    else:
        await call.message.edit_text(f"Ежедневные задачи: \n\n{tasks}")

    await call.message.edit_reply_markup(
        call.inline_message_id, reply_markup=builder.as_markup()
    )


@router.message(Command("daily"))
async def get_daily_task_list(message: types.Message) -> None:
    """`get_task_list`, but with daily tasks."""
    builder, tasks, owner_id = await get_paginated_tasks(message, daily=True)

    # Showing daily task list
    if not tasks:
        await message.answer(
            "Ежедневные задачи: \n\nЕжедневные задачи не найдены. "
            "Кажется, у вас появилось свободное время. :)",
            reply_markup=builder.as_markup()
        )
        # Approximate translation:
        # Tasks: No daily tasks were found.
        # It seems that you have some free time. :)
    else:
        await message.answer(
            f"Ежедневные задачи: \n\n{tasks}",
            reply_markup=builder.as_markup()
        )
