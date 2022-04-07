import re

from aiogram import types
from aiogram.dispatcher import FSMContext


class Coordinate:
    def __init__(self, coordinate: str) -> None:
        cut_str = re.sub("[^a-h1-8]", "", coordinate.lower())
        self.picked = cut_str[:2]
        y_str, x_str = self.picked
        self.x = int(x_str) - 1
        self.y = ord(y_str) - 97
        if not (0 <= self.x < 8 and 0 <= self.y < 8):
            raise ValueError

    def __str__(self) -> str:
        return self.picked

    def __eq__(self, __o: object) -> bool:
        return self.picked == __o.picked


class CoordinateError(Exception):
    def __init__(self, msg_object: types.Message, state: FSMContext = None,
                 answer: str = None, message: str = "Неверная координата") -> None:
        self.msg_object = msg_object
        self.state = state
        self.answer = answer
        self.message = message
        super().__init__(self.message)
