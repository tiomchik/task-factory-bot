from aiogram.filters.callback_data import CallbackData


class TaskControl(CallbackData, prefix="taskcontrol"):
    action: str
    task_id: int


class EditTask(CallbackData, prefix="edittask"):
    field: str
    task_id: int
