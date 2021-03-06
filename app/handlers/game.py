import logging
import re
from random import randint

import aioredis
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.callback_data import CallbackData

from .. import bot_config
from ..bot import bot, dp
from ..db import db
from ..dialogs import Messages
from ..game import (FIELD, Coordinate, CoordinateError, Game, logic_API,
                    parse_response, send_field)
from ..keyboards import colors, invitation, modes

change_pawn_cb = CallbackData("piece")


@dp.message_handler(Command('play', ignore_case=True))
async def start_game(msg: types.Message):
    await msg.answer(Messages.modes, reply_markup=modes.keyboard)
    await Game.choose_game_mode.set()
    if msg.from_user.mention.startswith("@"):
        db.update_username(msg.from_user.id, msg.from_user.mention)


@dp.message_handler(Text(modes.buttons["random"]), state=Game.choose_game_mode)
async def random_game_mode(msg: types.Message, state: FSMContext):
    redis = aioredis.from_url(bot_config.REDIS_URL, decode_responses=True)

    rand_user_id = await redis.srandmember("pending_users")
    if rand_user_id is None:
        await redis.sadd("pending_users", msg.from_user.id)
        await msg.answer(Messages.searching_opponent,
                         reply_markup=types.ReplyKeyboardRemove())
        return await Game.searching_opponent.set()
    await redis.srem("pending_users", rand_user_id)

    opponent = db.get_user_by_id(int(rand_user_id))
    my_username = db.get_user_by_id(msg.from_user.id).username
    opponent_state = dp.current_state(chat=int(rand_user_id),
                                      user=int(rand_user_id))
    is_white = bool(randint(0, 1))
    await state.update_data(field=FIELD,
                            white=is_white,
                            opponent=int(rand_user_id))
    await opponent_state.update_data(field=FIELD,
                                     white=not(is_white),
                                     opponent=msg.from_user.id)

    await msg.answer(Messages.opponent_found.format(username=opponent.username))
    await send_field(msg.from_user.id, FIELD, is_white)
    await bot.send_message(rand_user_id,
                           Messages.opponent_found.format(username=my_username))
    await send_field(rand_user_id, FIELD, not(is_white))
    if is_white:
        await bot.send_message(rand_user_id, Messages.pending_move)
        await opponent_state.set_state(Game.opponents_move)
        await msg.answer(Messages.pick_piece)
        await Game.pick_piece.set()
    else:
        await bot.send_message(rand_user_id, Messages.pick_piece)
        await opponent_state.set_state(Game.pick_piece)
        await msg.answer(Messages.pending_move)
        await Game.opponents_move.set()
    await redis.close()


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
    if not re.match("^@[a-zA-Z0-9_]{1,32}$|^[0-9]{1,12}$", msg.text):
        return await msg.reply(Messages.invalid_username)

    user = db.get_user_by_username(msg.text)
    logging.info(f"User found: {user}")

    if user is None:
        return await msg.reply(Messages.user_not_found)
    if user.id == msg.from_user.id:
        return await msg.reply(Messages.invalid_username)
    user_data = await state.get_data()
    opponent_id = user.id
    opponent_state = dp.current_state(chat=opponent_id, user=opponent_id)

    async with opponent_state.proxy() as opponent_data:
        if opponent_data.get("opponent"):
            return await msg.reply(Messages.user_busy)
        opponent_data["field"] = FIELD
        opponent_data["opponent"] = msg.from_user.id
        opponent_data["white"] = not(user_data["white"])
        await opponent_state.set_state(Game.invitation)

    sender = db.get_user_by_id(msg.from_id)
    sender_username = sender and sender.username or str(msg.from_user.id)

    await state.update_data(opponent=opponent_id, field=FIELD)
    await bot.send_message(opponent_id,
                           Messages.invitation.format(
                               name=msg.from_user.full_name,
                               username=sender_username),
                           reply_markup=invitation.keyboard)
    await msg.answer(Messages.pending_join)
    await Game.pending_join.set()


@dp.message_handler(state=Game.pending_join)
async def is_waiting_for_join(msg: types.Message, state: FSMContext):
    await msg.reply(Messages.pending_join)


@dp.message_handler(Text(invitation.buttons["accept"]), state=Game.invitation)
async def accept_invitation(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        opponent_state = dp.current_state(chat=data["opponent"],
                                          user=data["opponent"])
        await send_field(msg.from_user.id, FIELD, data["white"])
        await send_field(data["opponent"], FIELD, not(data["white"]))
        if data.get("white"):
            await bot.send_message(data["opponent"], Messages.pending_move)
            await opponent_state.set_state(Game.opponents_move)
            await msg.answer(Messages.pick_piece)
            await msg.answer(Messages.coordinate_example)
            await Game.pick_piece.set()
        else:
            await bot.send_message(data["opponent"], Messages.pick_piece)
            await opponent_state.set_state(Game.pick_piece)
            await msg.answer(Messages.pending_move)
            await Game.opponents_move.set()


@dp.message_handler(Text(invitation.buttons["decline"]), state=Game.invitation)
async def decline_invitation(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    opponent_state = dp.current_state(chat=user_data["opponent"],
                                      user=user_data["opponent"])
    await opponent_state.finish()
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(user_data["opponent"], Messages.invitation_canceled)


@dp.message_handler(state=Game.pick_piece)
async def pick_piece(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get("picked"):
        return

    picked = Coordinate(msg.text)
    cell = user_data["field"][picked.x][picked.y]
    if cell.isalpha() and user_data["white"] == cell.isupper():
        user_data["picked"] = str(picked)
    else:
        raise CoordinateError(Messages.pick_piece)

    try:
        response = await logic_API.pick(user_data["picked"], user_data["field"])
    except Exception as e:
        logging.error(f"Error in logic API - {e}")
        raise CoordinateError(answer=e,
                              message="SERVER ERROR: ???????????? ?? ??????????????")
    if not response:
        logging.error("No response from logic API server")
    logging.info(f"Response from logic API server:\n{response}")

    can_move = parse_response(response.get("canMoveTo"))
    can_beat = parse_response(response.get("canBeat"))
    will_check = parse_response(response.get("Checks"))
    will_mate = parse_response(response.get("Mates"))

    if not any((can_move, can_beat, will_check, will_mate)):
        raise CoordinateError(message=Messages.no_moves)
    await state.update_data(picked=user_data["picked"],
                            can_move=can_move,
                            can_beat=can_beat,
                            will_check=will_check,
                            will_mate=will_mate)

    logging.info(f"{can_move=}\n{can_beat=}\n{will_check=}\n{will_mate=}")

    if hasattr(picked, "next"):
        await Game.move_piece.set()
        msg.text = str(picked.next)
        return await move_piece(msg, state)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text=Messages.cancel_choise, callback_data="cancel_picked"))

    await send_field(msg.from_user.id, user_data["field"], user_data["white"],
                     picked=[picked.as_tuple()],
                     move=can_move,
                     beat=can_beat)
    await msg.answer(Messages.picked.format(picked=str(picked)),
                     reply_markup=keyboard)
    await msg.answer(Messages.pick_cell)
    await Game.move_piece.set()


@dp.message_handler(state=Game.move_piece)
async def move_piece(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if not user_data.get("picked"):
        return

    try:
        move = Coordinate(msg.text)
        picked = Coordinate(user_data.get("picked"))
    except CoordinateError:
        raise CoordinateError(Messages.pick_cell)

    field = user_data.get("field")

    if (bot_config.GOD_MODE or
        any(move.as_list() in line for line in [user_data["can_move"],
                                                user_data["can_beat"],
                                                user_data["will_check"],
                                                user_data["will_mate"]])):
        if field[picked.x][picked.y].lower() in "kr":
            user_data["castling"] = False
        field[move.x][move.y] = field[picked.x][picked.y]
        field[picked.x][picked.y] = "-"
        if (picked.x == 0 and field[move.x][move.y] == "p" or
                picked.x == 7 and field[move.x][move.y] == "P"):
            keyboard = types.InlineKeyboardMarkup()
            for callback, text in {
                "q": Messages.queen,
                "h": Messages.knight,
                "b": Messages.bishop,
                "r": Messages.rook
            }.items():
                keyboard.add(types.InlineKeyboardButton(
                    text=text, callback_data=change_pawn_cb.new(callback)))
            await msg.answer(Messages.change_pawn, reply_markup=keyboard)
            await state.update_data(picked=str(move))
            return await Game.change_pawn.set()
    elif (field[move.x][move.y].isalpha() and
          user_data["white"] == field[move.x][move.y].isupper()):
        await state.update_data(picked=False)
        msg.text = str(move)
        return await pick_piece(msg, state)
    else:
        raise CoordinateError()
    user_data["picked"] = False
    await state.update_data(**user_data)

    check = move.as_list() in user_data["will_check"]
    mate = move.as_list() in user_data["will_mate"]

    king_pos = []
    if check or mate:
        for y, row in enumerate(user_data["field"]):
            for x, piece in enumerate(row):
                if user_data["white"] and piece.islower() and piece.lower() == "k":
                    king_pos.append([y, x])
                    break
            else:
                continue
            break

    await send_field(msg.from_user.id, field, user_data["white"], check=king_pos)
    await msg.answer(Messages.moved.format(picked=str(picked), move=str(move)))
    if mate:
        await msg.answer(Messages.mate)
        await state.finish()
        db.increase_wins(msg.from_id)
    else:
        await msg.answer(Messages.pending_move)
        await Game.opponents_move.set()

    opponent_state = dp.current_state(chat=user_data["opponent"],
                                      user=user_data["opponent"])
    await opponent_state.update_data(field=field)
    await send_field(user_data["opponent"], field, not(user_data["white"]), check=king_pos)
    await bot.send_message(user_data["opponent"],
                           Messages.moved.format(picked=str(picked), move=str(move)))
    if mate:
        await bot.send_message(user_data["opponent"], Messages.mate)
        await opponent_state.finish()
        return db.increase_losses(user_data["opponent"])
    elif check:
        await bot.send_message(user_data["opponent"], Messages.check)
    await bot.send_message(user_data["opponent"], Messages.pick_piece)
    await opponent_state.set_state(Game.pick_piece)


@dp.callback_query_handler(text="cancel_picked", state=Game.move_piece)
async def cancel_picked(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(picked=False)
    await Game.pick_piece.set()
    await call.message.answer(Messages.pick_piece)
    await call.answer()


# @dp.callback_query_handler(change_pawn_cb.filter(), state=Game.change_pawn)
# async def change_pawn(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     user_data = await state.get_data()
#     field = user_data["field"]
#     picked = Coordinate(user_data["picked"])
#     if user_data["white"]:
#         piece = callback_data["piece"].upper()
#     else:
#         piece = callback_data["piece"]
#     field[picked.x][picked.y] = piece
#     await state.update_data(field=field)
#     await Game.move_piece.set()
#     await call.answer()
#     return await move_piece(msg, state)


@dp.errors_handler(exception=CoordinateError)
async def coordinate_error_handler(update: types.Update, exception: CoordinateError):
    await update.message.reply(exception.message)
    if exception.answer:
        await update.message.answer(exception.answer)
    return True
