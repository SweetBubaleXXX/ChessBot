import logging

from aiogram import Dispatcher, executor

from app.bot import dp
from app.handlers import *

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d):\n\t%(message)s"


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=_log_format)
    executor.start_polling(dp, on_shutdown=shutdown)
