import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text

from ..db import db
from ..bot import bot, dp
from ..dialogs import Messages

CANCEL_COMMANDS = ["cancel", "exit", "stop", "отмена", "стоп"]


@dp.message_handler(commands="start")
async def start(msg: types.Message):
    user_id = msg.from_user.id
    username = msg.from_user.mention
    full_name = msg.from_user.full_name
    db.append_user(user_id, username)
    user = db.get_user_by_username("@sweetBubaleXXX")
    logging.info(user)
    await msg.answer(Messages.greeting.format(name=full_name))


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True), state="*")
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True), state="*")
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
