from typing import Union

from .coordinate import Coordinate, CoordinateError
from .field import FIELD


class Player:
    def __init__(self, field: list = FIELD, picked: Union[str, None] = None, white: bool = True) -> None:
        self.field = field
        self.white = white
        self.picked = None
        if picked is not None:
            self.picked = Coordinate(picked)
            cell = field[self.picked.x][self.picked.y]
            if not ((white and 64 < ord(cell) < 90) or
                    (not white and 96 < ord(cell) < 123)):
                raise CoordinateError

    def right_pick(self, cell: str) -> bool:
        pass

    def pick(self, picked: Union[str, Coordinate]):
        pass
