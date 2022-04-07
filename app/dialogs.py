from dataclasses import dataclass


@dataclass
class Messages:
    greeting: str = "Здравствуйте, <b>{name}</b>!!!"
    modes: str = "Выберите режим игры:"
    colors: str = "За кого играть?"
    invite_opponent: str = "Отправьте контакт (например {example})"
    pick_piece: str = "Выберите фигуру:"
    pick_cell: str = "Выберите куда ходить:"
    picked: str = "<b>{picked}</b> → ..."
    moved: str = "<b>{picked}</b> → <u><b>{move}</b></u>"
    cancel_choise: str = "🚫 Отметить выбор 🚫"
