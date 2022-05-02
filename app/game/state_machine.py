from aiogram.dispatcher.filters.state import State, StatesGroup


class Game(StatesGroup):
    choose_game_mode = State()
    find_random = State()
    searching_opponent = State()
    choose_color = State()
    # set_timer = State()
    invite_opponent = State()
    invitation = State()
    pending_join = State()
    opponents_move = State()
    pick_piece = State()
    move_piece = State()
