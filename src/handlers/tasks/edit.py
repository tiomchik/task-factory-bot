from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

from . import TaskControl, EditTask
from db import session_maker, get_task_by_id
from utils.states_groups import EditTaskForm
from .show_task import ShowTask

router = Router()


task_id = 0
@router.callback_query(TaskControl.filter(F.action == "edit"))
async def edit(call: types.CallbackQuery, callback_data: TaskControl) -> None:
    """Edits a field of task with passed `task_id` in `callback_data`."""
    global task_id
    task_id = callback_data.task_id

    name_btn = types.InlineKeyboardButton(
        text="📝 Цель",
        callback_data=EditTask(field="name", task_id=task_id).pack()
    )
    deadline_btn = types.InlineKeyboardButton(
        text="🕓 Крайний срок",
        callback_data=EditTask(field="deadline", task_id=task_id).pack()
    )
    reward_btn = types.InlineKeyboardButton(
        text="🏆 Награду",
        callback_data=EditTask(field="reward", task_id=task_id).pack()
    )

    builder = InlineKeyboardBuilder()
    builder.row(name_btn, deadline_btn, reward_btn, width=1)

    await call.message.answer(
        "Какое поле вы желаете изменить?",
        reply_markup=builder.as_markup()
    )
    # Approximate translation:
    # Which field do you want to change?


@router.callback_query(EditTask.filter())
async def get_field(
    call: types.CallbackQuery, callback_data: EditTask, state: FSMContext
) -> None:
    """Retrieves a field selected by user and sets state according
    to the selected one."""
    await state.clear()

    if callback_data.field == "name":
        await state.set_state(EditTaskForm.name)
    elif callback_data.field == "deadline":
        await state.set_state(EditTaskForm.deadline)
    elif callback_data.field == "reward":
        await state.set_state(EditTaskForm.reward)

    await call.message.answer("Хорошо, теперь введите новое значение.")
    # Approximate translation:
    # OK, now enter the new value.

    if callback_data.field == "deadline":
        await call.message.answer("Формат: `год/месяц/день/час/минута`.")
        # Approximate translation:
        # Format: `year/month/day/hour/minute`.
    if callback_data.field != "name":
        await call.message.answer(
            "Отправьте \"-\" без кавычек для опустошения поля."
        )
        # Approximate translation:
        # Send "-" without quotes to empty the field.


async def task_is_edited(
    message: types.Message, state: FSMContext, edited_task_id: int
) -> None:
    """Sends the message saying that the a task has been successfully edited
    and clears the passed `state`."""
    builder = InlineKeyboardBuilder()
    show_edited_task_btn = types.InlineKeyboardButton(
        text="📝 Перейти к отредактированной задаче",
        callback_data=ShowTask(id=edited_task_id).pack()
    )
    task_list_btn = types.InlineKeyboardButton(
        text="📋 Список задач", callback_data="return_to_tasks"
    )

    builder.row(show_edited_task_btn, task_list_btn, width=1)

    await message.answer(
        "✅ Задача успешно отредактирована!", reply_markup=builder.as_markup()
    )
    # Approximate translation:
    # The task has been successfully edited!

    await state.clear()


@router.message(EditTaskForm.name)
async def edit_name(message: types.Message, state: FSMContext) -> None:
    """Edits the name field."""
    async with session_maker() as session:
        task = await get_task_by_id(task_id, session=session)
        task.name = message.text

        await session.commit()

    await task_is_edited(message, state, edited_task_id=task_id)


@router.message(EditTaskForm.deadline)
async def edit_deadline(message: types.Message, state: FSMContext) -> None:
    """Edits the deadline field."""
    if message.text == "-":
        deadline = None
    else:
        data = message.text.split("/")
        for i in range(len(data)):
            data[i] = int(data[i])

        deadline = datetime(*data)
        if deadline < datetime.now():
            await message.answer(
                "Вы ввели крайний срок в прошлом времени."
            )
            # Approximate translation:
            # You entered the deadline in the past time.
            return

    async with session_maker() as session:
        task = await get_task_by_id(task_id, session=session)
        task.deadline = deadline

        await session.commit()

    await task_is_edited(message, state, edited_task_id=task_id)


@router.message(EditTaskForm.reward)
async def edit_reward(message: types.Message, state: FSMContext) -> None:
    """Edits the reward field."""
    async with session_maker() as session:
        task = await get_task_by_id(task_id, session=session)

        if message.text == "-":
            task.reward = None
        else:
            task.reward = message.text

        await session.commit()

    await task_is_edited(message, state, edited_task_id=task_id)
