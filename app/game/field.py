from typing import List, Optional

from .coordinate import Coordinate

START_FIELD = [
    ["R", "H", "B", "Q", "K", "B", "H", "R"],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["r", "h", "b", "q", "k", "b", "h", "r"]
]


class Field():
    def __init__(self, field_list: List[List[str]] = START_FIELD) -> None:
        self.field = field_list

    def at(self, coordinate: Coordinate) -> str:
        return self.field[coordinate.x][coordinate.y]

    def find_king(self, is_white: bool) -> Optional[Coordinate]:
        for x, row in enumerate(self.field):
            for y, piece in enumerate(row):
                coordinate = Coordinate((x, y))
                if piece.lower() == "k" and self.is_own_piece(coordinate, is_white):
                    return coordinate
        return None

    def is_own_piece(self, coordinate: Coordinate, is_white: bool) -> bool:
        return self.at(coordinate).isalpha() and is_white == self.at(coordinate).isupper()
