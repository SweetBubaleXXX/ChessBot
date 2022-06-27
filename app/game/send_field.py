from typing import Union

from aiogram import types

from ..bot import bot
from ..render import Render

field_render = Render()


async def send_field(id: Union[int, str], field: list, white: bool, **kwargs):
    byteImg = field_render.render(field, white, **kwargs)
    await bot.send_photo(id, byteImg, reply_markup=types.ReplyKeyboardRemove())
