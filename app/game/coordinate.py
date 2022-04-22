import re
from typing import Union

from ..dialogs import Messages


class Coordinate:
    def __init__(self, coordinate: Union[str, tuple]) -> None:
        try:
            if isinstance(coordinate, str):
                cut_str = re.sub("[^a-h1-8]", "", coordinate.lower())
                self.picked = cut_str[:2]
                y_str, x_str = self.picked
                self.x = int(x_str) - 1
                self.y = ord(y_str) - 97
            elif isinstance(coordinate, tuple):
                self.x, self.y = coordinate
            if not (0 <= self.x < 8 and 0 <= self.y < 8):
                raise ValueError
        except (ValueError, IndexError):
            raise CoordinateError

    def as_tuple(self) -> tuple:
        return (self.x, self.y)

    def __str__(self) -> str:
        return self.picked

    def __eq__(self, __o: object) -> bool:
        return self.picked == __o.picked


class CoordinateError(Exception):
    def __init__(self, answer: Union[str, None] = None,
                 message: str = Messages.coordinate_error) -> None:
        self.answer = answer
        self.message = message
        super().__init__(self.message)
