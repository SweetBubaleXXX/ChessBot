import argparse
import logging

from aiogram import Dispatcher, executor

from app.bot import dp
from app.handlers import *
from app import bot_config

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d):\n\t%(message)s\n"

parser = argparse.ArgumentParser(description="Chess TG bot instance.")
parser.add_argument("-g", "--godmode", action="store_true",
                    help="prevent checking move position")
parser.add_argument("-l", "--loglevel", type=str,
                    choices=["INFO", "WARNING", "ERROR"], default="INFO")
args = parser.parse_args()

bot_config.GOD_MODE = args.godmode

loglevel = {
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR
}.get(args.loglevel)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    logging.basicConfig(level=loglevel, format=_log_format)
    executor.start_polling(dp, on_shutdown=shutdown)
