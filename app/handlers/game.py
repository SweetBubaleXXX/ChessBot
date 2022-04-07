import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text

from .. import config
from ..bot import bot, dp
from ..dialogs import Messages
from ..game import (Coordinate, CoordinateError, Game, call_logic_API,
                    send_field)
from ..game.field import FIELD


@dp.message_handler(Command('play', ignore_case=True), state="*")
async def start_game(msg: types.Message):
    state = Dispatcher.get_current().current_state()
    await state.reset_data()
    async with state.proxy() as data:
        field = FIELD
        data["field"] = field
        data["white"] = True
        await send_field(msg, field, data["white"])
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
