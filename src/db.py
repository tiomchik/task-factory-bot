from typing import Any

from aiogram import types
from datetime import datetime
from sqlalchemy import (
    TIMESTAMP, Boolean, Column, ForeignKey, Integer, Result,
    String, select, ReturnsRows
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import (
    AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession
)

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, unique=True, primary_key=True, autoincrement=False)


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String)
    deadline = Column(TIMESTAMP, nullable=True)
    reward = Column(String, nullable=True)
    daily = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    creation_date = Column(TIMESTAMP, default=datetime.utcnow)
    completed_date = Column(TIMESTAMP, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    owner = relationship("User")


async def prepare_database() -> None:
    """Creates tables in database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def execute(
    stmt: ReturnsRows, session: AsyncSession | None = None
) -> Result[tuple[Task]]:
    """Executes passed stmt in creatable or passed session and
    returns the rsult."""
    if session:
        result = await session.execute(stmt)
    else:
        async with session_maker() as session:
            result = await session.execute(stmt)

    return result


async def db_create_task(
    message: types.Message, task_data: dict[str, Any]
) -> None:
    """Creates a new task with passed `task_data` in db 
    and sends success message."""
    task = Task(
        **task_data, owner_id=message.from_user.id
    )
    async with session_maker() as session:
        session.add(task)
        await session.commit()

    await message.answer("Превосходно, задача создана!")


async def get_task_by_id(
    id: int, session: AsyncSession | None = None
) -> Task | None:
    """Gets a task by passed id."""
    stmt = select(Task).where(Task.id == id)

    task = await execute(stmt, session)

    return task.scalars().first()


async def get_daily_or_regular_tasks(
    owner_id: int, daily: bool = False, session: AsyncSession | None = None
):
    """Returns a sequence of tasks with the passed `daily` filter."""
    stmt = select(Task).where(
        Task.owner_id == owner_id, Task.daily == daily
    ).order_by(Task.creation_date.desc())

    tasks = await execute(stmt, session)

    return tasks.scalars().all()
