from aiogram import types

from aiogram.utils.callback_data import CallbackData

from ..dialogs import Messages

promote_pawn_cb = CallbackData("promote_pawn", "piece")

keyboard = types.InlineKeyboardMarkup()

for callback, text in {
    "q": Messages.queen,
    "h": Messages.knight,
    "b": Messages.bishop,
    "r": Messages.rook
}.items():
    keyboard.add(types.InlineKeyboardButton(
        text=text, callback_data=promote_pawn_cb.new(callback))
    )
