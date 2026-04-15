import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv

from bot.mail_loop import mail_loop

load_dotenv(find_dotenv())

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("errors.log"),
        logging.StreamHandler()
    ]
)

CHAT_ID = os.getenv("CHAT_ID")
THREAD_ID = os.getenv("THREAD_ID")

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()

async def main():
    asyncio.create_task(mail_loop(bot, CHAT_ID, THREAD_ID))
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
