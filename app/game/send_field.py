from aiogram import types

from ..bot import bot
from ..render import Render

field_render = Render()


async def send_field(msg: types.Message, field: list, white: bool, **kwargs):
    byteImg = field_render.render(field, white, **kwargs)
    await bot.send_photo(msg.from_user.id, byteImg)
