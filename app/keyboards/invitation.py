from aiogram import types

keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True)
buttons = {
    "accept": "✅ Принять ✅",
    "decline": "🚫 Отклонить 🚫"
}
keyboard.row(buttons["accept"])
keyboard.row(buttons["decline"])
