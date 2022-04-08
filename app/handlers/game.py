import logging
import re
from random import randint

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text

from .. import config
from ..bot import bot, dp
from ..db.db import get_user_by_username
from ..dialogs import Messages
from ..game import *
from ..keyboards import colors, modes


@dp.message_handler(Command('play', ignore_case=True), state="*")
async def start_game(msg: types.Message):
    await msg.answer(Messages.modes, reply_markup=modes.keyboard)
    await Game.choose_game_mode.set()


@dp.message_handler(Text(modes.buttons["friend"]), state=Game.choose_game_mode)
async def friend_game_mode(msg: types.Message, state: FSMContext):
    await msg.answer(Messages.colors, reply_markup=colors.keyboard)
    await Game.choose_color.set()


@dp.message_handler(Text(colors.buttons["white"]), state=Game.choose_color)
async def choose_white(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["white"] = True
    await invite_opponent_reply(msg)


@dp.message_handler(Text(colors.buttons["black"]), state=Game.choose_color)
async def choose_black(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["white"] = False
    await invite_opponent_reply(msg)


@dp.message_handler(Text(colors.buttons["random"]), state=Game.choose_color)
async def choose_random(msg: types.Message, state: FSMContext):
    is_white = bool(randint(0, 1))
    async with state.proxy() as data:
        data["white"] = is_white
    await msg.reply(colors.buttons["white"] if is_white else colors.buttons["black"])
    await invite_opponent_reply(msg)


async def invite_opponent_reply(msg: types.Message):
    bot_name = await bot.get_me()
    await msg.answer(Messages.invite_opponent.format(example=bot_name.mention),
                     reply_markup=types.ReplyKeyboardRemove())
    await Game.invite_opponent.set()


@dp.message_handler(state=Game.invite_opponent)
async def choose_opponent(msg: types.Message, state: FSMContext):
    if not re.match("^@[a-zA-Z0-9_]{1,32}$", msg.text):
        return await msg.reply(Messages.invalid_username)
    user = get_user_by_username(msg.text)
    logging.info(user)
    if user is None:
        return await msg.reply(Messages.user_not_found)
    await msg.answer(str(user))
    state = Dispatcher.get_current().current_state()
    await state.reset_data()
    async with state.proxy() as data:
        data["field"] = FIELD
        data["white"] = True
        await send_field(msg, FIELD, data["white"])
    await msg.answer(Messages.pick_piece)
    await Game.pick_piece.set()


@dp.message_handler(state=Game.pick_piece)
async def pick_piece(msg: types.Message, state: FSMContext):
    data = await state.get_data()

    if data.get("picked"):
        return

    try:
        picked = Coordinate(msg.text)
    except (ValueError, IndexError):
        raise CoordinateError(msg, state, Messages.pick_piece)

    cell = data["field"][picked.x][picked.y]
    if ((data["white"] and 64 < ord(cell) < 90) or
            (not data["white"] and 96 < ord(cell) < 123)):
        data["picked"] = str(picked)
        await state.update_data(picked=data["picked"])
    else:
        raise CoordinateError(msg, state, Messages.pick_piece)

    # logging.info(await call_logic_API(data["picked"], data["field"]))

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text=Messages.cancel_choise, callback_data="cancel_picked"))

    await send_field(msg, data["field"], data["white"],
                     picked=[(picked.x, picked.y)])
    await msg.answer(Messages.picked.format(picked=str(picked)),
                     reply_markup=keyboard)
    await msg.answer(Messages.pick_cell)
    await Game.move_piece.set()


@ dp.message_handler(state=Game.move_piece)
async def move_piece(msg: types.Message, state: FSMContext):
    data = await state.get_data()

    if not data.get("picked"):
        return

    try:
        move = Coordinate(msg.text)
        picked = Coordinate(data.get("picked"))
    except (ValueError, IndexError):
        raise CoordinateError(msg, state, Messages.pick_cell)

    field = data.get("field")
    field[move.x][move.y] = field[picked.x][picked.y]
    field[picked.x][picked.y] = "-"
    data["white"] = not data["white"]
    data["picked"] = False
    await state.update_data(**data)

    await send_field(msg, field, data["white"])
    await msg.answer(Messages.moved.format(picked=str(picked), move=str(move)))
    await msg.answer(Messages.pick_piece)
    await Game.pick_piece.set()


@ dp.callback_query_handler(text="cancel_picked", state=Game.move_piece)
async def cancel_picked(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(picked=False)
    await call.message.answer(Messages.pick_piece)
    await call.answer()
    await Game.pick_piece.set()


@ dp.errors_handler(exception=CoordinateError)
async def coordinate_error_handler(update: types.Update, exception: CoordinateError):
    await exception.msg_object.reply(exception.message)
    await exception.msg_object.answer(exception.answer)
    return True
