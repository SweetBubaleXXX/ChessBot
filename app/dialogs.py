class Messages:
    greeting: str = "Здравствуйте, <b>{name}</b>!!!"
    modes: str = "Выберите режим игры:"
    colors: str = "За кого играть?"
    invite_opponent: str = "Отправьте контакт (например {example})"
    invalid_username: str = "Неправильное имя пользователя"
    user_not_found: str = "Пользователь с таким именем не найден"
    user_busy: str = "Пользователь сейчас находится в игре"
    invitation: str = "Приглашение в игру от <i>{name}</i>"
    pending_join: str = "Ждём ответ от пользователя"
    pending_move: str = "Ход соперника..."
    pick_piece: str = "Выберите фигуру:"
    pick_cell: str = "Выберите куда ходить:"
    picked: str = "<b>{picked}</b> → ..."
    moved: str = "<b>{picked}</b> → <u><b>{move}</b></u>"
    coordinate_error: str = "Неверная координата"
    cancel_choise: str = "🚫 Отметить выбор 🚫"
