import logging

from aiogram import Dispatcher, executor

from app.bot import dp
from app.handlers import *


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, on_shutdown=shutdown)
