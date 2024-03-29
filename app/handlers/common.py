import logging

import aioredis
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text

from ..bot import bot, dp
from ..bot_config import REDIS_URL
from ..db import db
from ..dialogs import Messages
from ..game import Game

CANCEL_COMMANDS = ["cancel", "exit", "close",
                   "fuckyou", "stop", "отмена", "стоп"]

states_for_cancel_game = [Game.pick_piece, Game.move_piece, Game.promote_pawn,
                          Game.opponents_move, Game.pending_join, Game.invitation]


@dp.message_handler(CommandStart())
async def start(msg: types.Message):
    user_id = msg.from_user.id
    username = msg.from_user.mention
    full_name = msg.from_user.full_name
    if not username.startswith("@"):
        logging.info(f"New user: {' - '.join((str(full_name), str(user_id)))}")
        db.insert_user(user_id, user_id)
        await msg.answer(Messages.greeting_id.format(id=user_id))
    db.insert_user(user_id, username)
    logging.info(f"New user: {username}")
    await msg.answer(Messages.greeting.format(name=full_name))


@dp.message_handler(Command("nickname", ignore_case=True), state="*")
async def get_my_nickname(msg: types.Message, state: FSMContext):
    user = db.get_user_by_id(msg.from_user.id)
    if user is None:
        return
    await msg.reply(user.username)


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True),
                    state=states_for_cancel_game)
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True),
                    state=states_for_cancel_game)
async def cancel_game(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("opponent_id"):
        await bot.send_message(user_data["opponent_id"], Messages.game_canceled,
                               reply_markup=types.ReplyKeyboardRemove())
        opponent_state = dp.current_state(chat=user_data["opponent_id"],
                                          user=user_data["opponent_id"])
        await opponent_state.finish()
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True),
                    state=Game.searching_opponent)
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True),
                    state=Game.searching_opponent)
async def cancel_invitation(msg: types.Message, state: FSMContext):
    redis = aioredis.from_url(REDIS_URL)
    await redis.srem("pending_users", msg.from_user.id)
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())
    await redis.close()


@dp.message_handler(Command(CANCEL_COMMANDS, ignore_case=True), state="*")
@dp.message_handler(Text(equals=CANCEL_COMMANDS, ignore_case=True), state="*")
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())
