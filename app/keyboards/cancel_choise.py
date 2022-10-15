from aiogram import types

from ..dialogs import Messages

keyboard = types.InlineKeyboardMarkup()
keyboard.add(types.InlineKeyboardButton(
    text=Messages.cancel_choise, callback_data="cancel_picked"
))
