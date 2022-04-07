import logging

from aiogram import executor

from app.bot import dp
from app.handlers import *

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp)
