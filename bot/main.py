import asyncio
import sys

from aiogram import Bot, Dispatcher

from bot.config import BOT_TOKEN
from bot.db import init_db
from bot.handlers.admin import router as admin_router
from bot.handlers.user import router as user_router


async def main() -> None:
    if not BOT_TOKEN:
        print("ERROR: Set CHINAGUARD_BOT_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Admin router first so admin commands take priority
    dp.include_router(admin_router)
    dp.include_router(user_router)

    print("ChinaGuard bot started. Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
