from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime

from db import db_create_task
from .show_tasks import get_task_list, get_daily_task_list
from utils.states_groups import CreateTaskForm

router = Router()


daily_field = False
@router.message(Command("create"))
async def create_task(message: types.Message, state: FSMContext) -> None:
    """Creates task with the user's data."""
    # Buttons
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Ежедневная"))
    builder.add(types.KeyboardButton(text="Обычная"))

    await state.clear()
    await state.set_state(CreateTaskForm.daily)

    await message.answer(
        "Выберите, это будет ежедневная или обычная задача?\n"
        "Чтобы отменить, в любой момент введите команду /cancel.",
        reply_markup=builder.as_markup(
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    # Approximate translation:
    # Choose, will it be a daily or a regular task?

    @router.message(CreateTaskForm.daily)
    async def daily(message: types.Message, state: FSMContext) -> None:
        data = message.text.lower()
        if data == "ежедневная":
            await state.update_data(daily=True)
            global daily_field
            daily_field = True
        elif data == "обычная":
            await state.update_data(daily=False)
        else:
            await create_task(message, state)
            return

        await state.set_state(CreateTaskForm.name)
        await message.answer(
            "Отлично, теперь введите, что предстоит сделать.",
        )
        # Approximate translation:
        # Great, now enter what needs to be done.

    @router.message(CreateTaskForm.name)
    async def name(message: types.Message, state: FSMContext) -> None:
        await state.update_data(name=message.text)
        await state.set_state(CreateTaskForm.deadline)
        if not daily_field:
            await message.answer(
                "Теперь по желанию укажите "
                "крайний срок выполнения в формате "
                "`год/месяц/день/час/минута`. Нули перед однозначными "
                "числами можно опускать. Например: 2024/2/10/9/0. "
                "(если хотите обойтись без него, отправьте \"-\" "
                "без кавычек)",
            )
            # Approximate translation:
            # Now optionally specify the deadline in the format
            # `year/month/day/hour/minute'. Zeros before single digits can
            # be omitted. For example: 2024/2/10/9/0.
            # (if you want to do without it, send "-" without quotes)
        else:
            task_data = await state.get_data()
            await db_create_task(message, task_data)
            await state.clear()

            await get_daily_task_list(message)

    @router.message(CreateTaskForm.deadline)
    async def deadline(message: types.Message, state: FSMContext) -> None:
        if message.text == "-":
            await state.update_data(deadline=None)
        else:
            # Splitting and converting a string into list of integers
            data = message.text.split("/")
            for i in range(len(data)):
                data[i] = int(data[i])

            try:
                deadline = datetime(*data)
                if deadline < datetime.now():
                    await message.answer(
                        "Вы ввели крайний срок в прошлом времени."
                    )
                    # Approximate translation:
                    # You entered the deadline in the past time.
                    raise TypeError()
            except:
                await message.answer(
                    "Возникла ошибка, но не переживайте, в будущем "
                    "вы сможете редактировать задачу."
                )
                # Approximate translation:
                # An error has occurred, but don't worry,
                # you will be able to edit the task in the future.
            else:
                # Updating data in state
                await state.update_data(deadline=deadline)
        
        await state.set_state(CreateTaskForm.reward)
        await message.answer(
            "У вас будет больше мотивации с наградой в конце. "
            "Поэтому, укажите себе вознаграждение за выполнение "
            "данной задачи. (снова пришлите \"-\" "
            "без кавычек если не желаете назначать себе награду)"
        )

    @router.message(CreateTaskForm.reward)
    async def reward(message: types.Message, state: FSMContext) -> None:
        if message.text == "-":
            await state.update_data(reward=None)
        else:
            await state.update_data(reward=message.text)

        task_data = await state.get_data()

        # Creating task
        await db_create_task(message, task_data)
        await state.clear()

        await get_task_list(message)


@router.callback_query(F.data == "create")
async def callback_create(call: types.CallbackQuery, state: FSMContext) -> None:
    """`create_task` function, but for callback query."""
    await create_task(call.message, state)


@router.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext) -> None:
    """Clears the passed state and stops the execution of
    function from a previous command."""
    await state.clear()
    await message.answer(
        "Отменено.", reply_markup=types.ReplyKeyboardRemove()
    )
    # Approximate translation:
    # Canceled.
