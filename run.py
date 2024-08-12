import asyncio
from aiogram import Bot, Dispatcher

from handlers import router
from config import API_TOKEN


bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Starting the bot!")
    asyncio.run(main())
    print("Finishing the bot!")
