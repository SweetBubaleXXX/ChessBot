from .coordinate import Coordinate


def parse_response(str_value: str) -> list:
    out_arr = []
    if not str_value:
        return out_arr
    splited_values = str_value.split(" ")
    if not splited_values[-1]:
        splited_values.pop()
    for cell in splited_values:
        out_arr.append(tuple(Coordinate(cell)))
    return out_arr
