import io
from os import path
from typing import Optional

from PIL import Image

from . import config

PATH = path.dirname(__file__)


class Render:
    def __init__(self, size: Optional[int] = None, theme: Optional[int] = None) -> None:
        if size in config.SIZES:
            self.size = size
        else:
            self.size = config.SIZES[0]
        self.theme = theme if theme in config.THEMES else config.THEMES[0]

        self.board_sizes = config.BOARD_SIZES[str(self.size)]
        self.board = Image.open(path.join(PATH, "src", self.theme, str(
            self.size), config.BOARDS["board"])).convert("RGBA")
        self.board_black = Image.open(path.join(PATH, "src", self.theme, str(
            self.size), config.BOARDS["board_black"])).convert("RGBA")
        self.pieces = {}
        self.__load_cells_from_files()

    def __load_cells_from_files(self):
        for attr, value in config.CELLS.items():
            setattr(self, attr, {})
            attribute = getattr(self, attr)
            for key, filename in value.items():
                attribute[key] = Image.open(
                    path.join(PATH, "src", self.theme, str(self.size), filename))

    def render(self, field: list, white: bool = True, **kwargs) -> bytes:
        """
            picked: list[Iterable[int]] | None,
            move: list[Iterable[int]] | None,
            beat: list[Iterable[int]] | None,
            check: list[Iterable[int]] | None
        """
        board_copy = self.board.copy() if white else self.board_black.copy()
        width, border = self.board_sizes
        for key, value in kwargs.items():
            if value is None: continue
            for y, x in value:
                if white:
                    y = 7 - y
                else:
                    x = 7 - x
                position = (border + x * width, border + y * width)
                board_copy.paste(self.cells[key], position, self.cells[key])
        for y, row in enumerate(field[::(-1)**int(white)]):
            for x, piece in enumerate(row[::(-1)**int(not white)]):
                if piece == "-":
                    continue
                piece_img = self.pieces.get(piece)
                position = (border + x * width + (width - piece_img.width) // 2,
                            border + y * width)
                board_copy.paste(piece_img, position, piece_img)
        byte_arr = io.BytesIO()
        board_copy.convert("RGB").save(byte_arr, format="PNG")
        return byte_arr.getvalue()
