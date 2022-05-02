from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from .bot_config import TOKEN, REDIS_CONF

bot = Bot(token=TOKEN,
          parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=RedisStorage2(**REDIS_CONF))
