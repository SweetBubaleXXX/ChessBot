from .coordinate import Coordinate


def parse_response(str_value: str) -> list:
    out_arr = []
    if not str_value:
        return out_arr
    splited_value = str_value.split(" ")
    if not splited_value[-1]:
        splited_value.pop()
    for cell in splited_value:
        out_arr.append(Coordinate(cell).as_list())
    return out_arr
