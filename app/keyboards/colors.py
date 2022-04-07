from aiogram import types

keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True)
buttons = {
    "white": "🏳️ За белых 🏳️",
    "black": "🏴 За черных 🏴",
    "random": "🎲 Рандом 🎲"
}
keyboard.row(buttons["white"], buttons["black"])
keyboard.row(buttons["random"])
