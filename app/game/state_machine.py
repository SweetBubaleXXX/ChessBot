from aiogram.dispatcher.filters.state import State, StatesGroup


class Game(StatesGroup):
    choose_game_mode = State()
    choose_color = State()
    # set_timer = State()
    invite_opponent = State()
    wait_for_opponent = State()
    pick_piece = State()
    move_piece = State()
