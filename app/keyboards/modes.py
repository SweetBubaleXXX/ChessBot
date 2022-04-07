from aiogram import types

keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True)
buttons = {
    "random": "🎲 Рандомый оппонент 🎲",
    "friend": "📬 Игра с другом 📬"
}
keyboard.row(buttons["random"])
keyboard.row(buttons["friend"])
