import io
from os import path
from typing import Optional

from PIL import Image

PATH = path.dirname(__file__)
SIZES = [1100]
BOARD_SIZES = {
    "1100": (128, 38)  # Cell size, border size
}
BOARDS = {
    "board": "board.png",
    "board_black": "board-reverse.png",
}
CELLS = {
    "pieces": {
        "R": "wr.png",
        "H": "wh.png",
        "B": "wb.png",
        "Q": "wq.png",
        "K": "wk.png",
        "P": "wp.png",
        "r": "br.png",
        "h": "bh.png",
        "b": "bb.png",
        "q": "bq.png",
        "k": "bk.png",
        "p": "bp.png"
    },
    "cells": {
        "picked": "green.png",
        "move": "dot.png",
        "beat": "yellow.png",
        "check": "red.png"
    }
}


class Render:
    def __init__(self, size: Optional[int] = None) -> None:
        if size in SIZES:
            self.size = size
        else:
            self.size = SIZES[0]
        self.board_sizes = BOARD_SIZES[str(self.size)]
        self.board = Image.open(path.join(PATH, "src", str(
            self.size), BOARDS["board"])).convert("RGBA")
        self.board_black = Image.open(path.join(PATH, "src", str(
            self.size), BOARDS["board_black"])).convert("RGBA")
        self.pieces = {}
        self.__load_cells_from_files()

    def __load_cells_from_files(self):
        for attr, value in CELLS.items():
            setattr(self, attr, {})
            attribute = getattr(self, attr)
            for key, filename in value.items():
                attribute[key] = Image.open(
                    path.join(PATH, "src", str(self.size), filename))

    def render(self, field: list, white: bool = True, **kwargs) -> bytes:
        """
            picked: list[tuple] | None,
            move: list[tuple] | None,
            beat: list[tuple] | None,
            check: list[tuple] | None
        """
        board_copy = self.board.copy() if white else self.board_black.copy()
        width, border = self.board_sizes
        for key, value in kwargs.items():
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
