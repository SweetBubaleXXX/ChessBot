import re
from typing import Optional, Union

from ..dialogs import Messages


class Coordinate:
    def __init__(self, coordinate: Union[str, tuple]) -> None:
        try:
            if isinstance(coordinate, str):
                cut_str = re.sub("[^a-h1-8]", "", coordinate.lower())
                trimmed = cut_str[:2]
                y_str, x_str = trimmed
                self.x = int(x_str) - 1
                self.y = ord(y_str) - 97
                if len(cut_str) >= 4:
                    self.next = Coordinate(cut_str[2:4])
            elif isinstance(coordinate, tuple):
                self.x, self.y = coordinate
            if not (0 <= self.x < 8 and 0 <= self.y < 8):
                raise ValueError
        except (ValueError, IndexError):
            raise CoordinateError

    def __str__(self) -> str:
        return "".join([chr(self.y + 97), str(self.x + 1)])

    def __eq__(self, __o: object) -> bool:
        return str(self) == str(__o)

    def __iter__(self):
        self._n = True
        return self

    def __next__(self):
        if self._n == 0:
            self._n += 1
            return self.x
        elif self._n == 1:
            self._n += 1
            return self.y
        else:
            raise StopIteration

    def as_tuple(self) -> tuple:
        return (self.x, self.y)

    def as_list(self) -> list:
        return [self.x, self.y]


class CoordinateError(Exception):
    def __init__(self, answer: Optional[str] = None,
                 message: str = Messages.coordinate_error) -> None:
        self.answer = answer
        self.message = message
        super().__init__(self.message)
