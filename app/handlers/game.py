import logging
import re
from random import randint

import aioredis
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text

from .. import bot_config
from ..bot import bot, dp
from ..db import db
from ..dialogs import Messages
from ..game import (START_FIELD, Coordinate, CoordinateError, Field, Game,
                    logic_API, parse_coordinate_response, send_field)
from ..keyboards import cancel_choise, colors, invitation, modes, promote_pawn


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
    player = db.get_user_by_id(msg.from_user.id)
    if opponent is None or player is None:
        await redis.sadd("pending_users", msg.from_user.id)
        await msg.answer(Messages.searching_opponent,
                         reply_markup=types.ReplyKeyboardRemove())
        return await Game.searching_opponent.set()
    opponent_state = dp.current_state(chat=int(rand_user_id),
                                      user=int(rand_user_id))
    is_white = bool(randint(0, 1))
    await state.update_data(field=START_FIELD,
                            is_white=is_white,
                            opponent_id=int(rand_user_id))
    await opponent_state.update_data(field=START_FIELD,
                                     is_white=not (is_white),
                                     opponent_id=msg.from_user.id)

    await msg.answer(Messages.opponent_found.format(username=opponent.username))
    await send_field(msg.from_user.id, START_FIELD, is_white)
    await bot.send_message(rand_user_id,
                           Messages.opponent_found.format(username=player.username))
    await send_field(rand_user_id, START_FIELD, not is_white)
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
    async with state.proxy() as player_data:
        player_data["is_white"] = True
    await invite_opponent_reply(msg)


@dp.message_handler(Text(colors.buttons["black"]), state=Game.choose_color)
async def choose_black(msg: types.Message, state: FSMContext):
    async with state.proxy() as player_data:
        player_data["is_white"] = False
    await invite_opponent_reply(msg)


@dp.message_handler(Text(colors.buttons["random"]), state=Game.choose_color)
async def choose_random(msg: types.Message, state: FSMContext):
    is_white = bool(randint(0, 1))
    async with state.proxy() as player_data:
        player_data["is_white"] = is_white
    await msg.reply(colors.buttons["is_white"] if is_white else colors.buttons["black"])
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

    opponent = db.get_user_by_username(msg.text)
    logging.info(f"User found: {opponent}")

    if opponent is None:
        return await msg.reply(Messages.user_not_found)
    if opponent.id == msg.from_user.id:
        return await msg.reply(Messages.invalid_username)
    player_data = await state.get_data()
    opponent_state = dp.current_state(chat=opponent.id, user=opponent.id)

    async with opponent_state.proxy() as opponent_data:
        if opponent_data.get("opponent_id"):
            return await msg.reply(Messages.user_busy)
        opponent_data["field"] = START_FIELD
        opponent_data["opponent_id"] = msg.from_user.id
        opponent_data["is_white"] = not (player_data["is_white"])
        await opponent_state.set_state(Game.invitation)

    sender = db.get_user_by_id(msg.from_id)
    sender_username = sender and sender.username or str(msg.from_user.id)

    await state.update_data(opponent_id=opponent.id, field=START_FIELD)
    await bot.send_message(opponent.id,
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
    async with state.proxy() as player_data:
        opponent_state = dp.current_state(chat=player_data["opponent_id"],
                                          user=player_data["opponent_id"])
        await send_field(msg.from_user.id, START_FIELD, player_data["is_white"])
        await send_field(player_data["opponent_id"], START_FIELD, not (player_data["is_white"]))
        if player_data.get("is_white"):
            await bot.send_message(player_data["opponent_id"], Messages.pending_move)
            await opponent_state.set_state(Game.opponents_move)
            await msg.answer(Messages.pick_piece)
            await msg.answer(Messages.coordinate_example)
            await Game.pick_piece.set()
        else:
            await bot.send_message(player_data["opponent_id"], Messages.pick_piece)
            await opponent_state.set_state(Game.pick_piece)
            await msg.answer(Messages.pending_move)
            await Game.opponents_move.set()


@dp.message_handler(Text(invitation.buttons["decline"]), state=Game.invitation)
async def decline_invitation(msg: types.Message, state: FSMContext):
    player_data = await state.get_data()
    opponent_state = dp.current_state(chat=player_data["opponent_id"],
                                      user=player_data["opponent_id"])
    await opponent_state.finish()
    await state.finish()
    await msg.reply(Messages.on_exit, reply_markup=types.ReplyKeyboardRemove())
    await bot.send_message(player_data["opponent_id"], Messages.invitation_canceled)


@dp.message_handler(state=Game.pick_piece)
async def pick_piece(msg: types.Message, state: FSMContext):
    player_data = await state.get_data()

    if player_data.get("picked"):
        return

    picked = Coordinate(msg.text)
    field = Field(player_data["field"])
    if field.is_own_piece(picked, player_data["is_white"]):
        player_data["picked"] = str(picked)
    else:
        raise CoordinateError(Messages.pick_piece)

    response = await logic_API.pick(player_data["picked"])
    if not response:
        return await msg.answer("Server error")
    logging.debug(f"Response from logic API server:\n{response}")

    can_move = parse_coordinate_response(response.get("wcim"))
    can_beat = parse_coordinate_response(response.get("wcib"))

    if not any((can_move, can_beat)):
        raise CoordinateError(message=Messages.no_moves)
    await state.update_data(picked=player_data["picked"],
                            can_move=can_move+can_beat)

    logging.debug(f"{can_move=}\n{can_beat=}\n")

    if picked.next:
        await Game.move_piece.set()
        msg.text = str(picked.next)
        return await move_piece(msg, state)

    await send_field(msg.from_user.id, player_data["field"], player_data["is_white"],
                     picked=[tuple(picked)],
                     move=can_move,
                     beat=can_beat)
    await msg.answer(Messages.picked.format(picked=str(picked)),
                     reply_markup=cancel_choise.keyboard)
    await msg.answer(Messages.pick_cell)
    await Game.move_piece.set()


@dp.message_handler(state=Game.move_piece)
async def move_piece(msg: types.Message, state: FSMContext):
    player_data = await state.get_data()

    if not player_data.get("picked"):
        return

    try:
        move = Coordinate(msg.text)
        picked = Coordinate(player_data.get("picked"))
    except CoordinateError:
        raise CoordinateError(Messages.pick_cell)

    field = Field(player_data["field"])

    if (bot_config.GOD_MODE or tuple(move) in player_data["can_move"]):
        response = await logic_API.move(str(move))
        if not response:
            return await msg.answer("Server error")
        if response.promoting:
            await msg.answer(Messages.promote_pawn, reply_markup=promote_pawn.keyboard)
            await state.update_data(picked=str(move))
            return await Game.promote_pawn.set()
    elif field.is_own_piece(move, player_data["is_white"]):
        await state.update_data(picked=False)
        msg.text = str(move)
        return await pick_piece(msg, state)
    else:
        raise CoordinateError
    await state.update_data(picked=False, field=response.field)

    return await handle_move_response(msg, state, response, str(picked), str(move))


@dp.callback_query_handler(promote_pawn.promote_pawn_cb.filter(), state=Game.promote_pawn)
async def promote_pawn_callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    player_data = await state.get_data()
    picked = player_data["picked"]

    response = await logic_API.promote(callback_data["piece"])
    if not response:
        return await call.message.answer("Server error")
    await state.update_data(picked=False, field=response.field)

    return await handle_move_response(
        call.message, state, response, picked, callback_data["piece"])


@dp.callback_query_handler(text="cancel_picked", state=Game.move_piece)
async def cancel_picked_callback(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(picked=False)
    await Game.pick_piece.set()
    await call.message.answer(Messages.pick_piece)
    await call.answer()


@dp.errors_handler(exception=CoordinateError)
async def coordinate_error_handler(update: types.Update, exception: CoordinateError):
    await update.message.reply(exception.message)
    if exception.answer:
        await update.message.answer(exception.answer)
    return True


async def handle_move_response(
    msg: types.Message,
    state: FSMContext,
    response: logic_API.MoveResponse,
    picked: str,
    move: str
):
    player_data = await state.get_data()

    field = Field(response.field)

    king_pos = []
    if response.check or response.mate:
        king_coordinate = field.find_king(player_data["is_white"])
        if king_coordinate:
            king_pos.append(tuple(king_coordinate))

    await send_field(msg.from_user.id, field.field,
                     player_data["is_white"], check=king_pos)
    await msg.answer(Messages.moved.format(picked=str(picked), move=str(move)))
    opponent_state = dp.current_state(chat=player_data["opponent_id"],
                                      user=player_data["opponent_id"])
    await opponent_state.update_data(field=field.field)
    await send_field(player_data["opponent_id"], field.field,
                     not (player_data["is_white"]), check=king_pos)
    await bot.send_message(player_data["opponent_id"],
                           Messages.moved.format(picked=str(picked), move=str(move)))
    if response.mate:
        await msg.answer(Messages.mate)
        await bot.send_message(player_data["opponent_id"], Messages.mate)
        await state.finish()
        await opponent_state.finish()
        db.increase_wins(msg.from_id)
        return db.increase_losses(player_data["opponent_id"])
    elif response.check:
        await bot.send_message(player_data["opponent_id"], Messages.check)
    await msg.answer(Messages.pending_move)
    await Game.opponents_move.set()
    await bot.send_message(player_data["opponent_id"], Messages.pick_piece)
    await opponent_state.set_state(Game.pick_piece)
