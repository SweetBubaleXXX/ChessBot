import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text

from ..bot import bot, dp
from ..db import db
from ..dialogs import Messages
from ..game import Game

CANCEL_COMMANDS = ["cancel", "exit", "close",
                   "fuckyou", "stop", "отмена", "стоп"]


@dp.message_handler(CommandStart())
async def start(msg: types.Message):
    user_id = msg.from_user.id
    username = msg.from_user.mention
    full_name = msg.from_user.full_name
    db.append_user(user_id, username)
    logging.info(username)
    await msg.answer(Messages.greeting.format(name=full_name))


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True),
                    state=[Game.pick_piece, Game.move_piece, Game.opponents_move])
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True),
                    state=[Game.pick_piece, Game.move_piece, Game.opponents_move])
async def cancel_game(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("opponent"):
        await bot.send_message(user_data["opponent"], Messages.game_canceled,
                               reply_markup=types.ReplyKeyboardRemove())
        opponent_state = dp.current_state(chat=user_data["opponent"],
                                          user=user_data["opponent"])
        await opponent_state.finish()
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True),
                    state=[Game.pending_join, Game.invitation])
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True),
                    state=[Game.pending_join, Game.invitation])
async def cancel_invitation(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("opponent"):
        opponent_state = dp.current_state(chat=user_data["opponent"],
                                          user=user_data["opponent"])
        await opponent_state.finish()
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True), state="*")
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True), state="*")
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())
