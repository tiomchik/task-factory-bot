import asyncio
import logging

from config import dp, bot
from db import prepare_database

# Routers
from handlers.start import router as start_router
from handlers.tasks.create import router as create_router
from handlers.tasks.show_task import router as show_task_router
from handlers.tasks.show_tasks import router as show_tasks_router
from handlers.tasks.mark_as_completed import router as mark_completed_router
from handlers.tasks.mark_as_daily import router as mark_daily_router
from handlers.tasks.edit import router as edit_router
from handlers.tasks.delete import router as delete_router
from handlers.tasks.all_completed import router as all_completed_router
from utils.paginator import router as paginator_router


async def main() -> None:
    """Main function."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )

    dp.include_routers(
        start_router,
        # CRUD routers
        create_router, show_task_router,
        show_tasks_router, paginator_router,
        edit_router, delete_router,
        # Other task routers
        mark_completed_router, mark_daily_router, all_completed_router
    )

    await prepare_database()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
