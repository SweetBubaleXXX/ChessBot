from typing import Union

from .coordinate import Coordinate


def parse_response(arr: Union[list, tuple], str_value: str):
    if not str_value:
        return
    splited_value = str_value.split(" ")
    if not splited_value[-1]:
        splited_value.pop()
    for cell in splited_value:
        arr.append(Coordinate(cell).as_list())