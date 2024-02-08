from aiogram.filters.state import State, StatesGroup
from datetime import datetime


class CreateTaskForm(StatesGroup):
    daily: bool = State()
    name: str = State()
    deadline: datetime | None = State()
    reward: str | None = State()


class EditTaskForm(StatesGroup):
    name: str | None = State()
    deadline: datetime | None = State()
    reward: str | None = State()
