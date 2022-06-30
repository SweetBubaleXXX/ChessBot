from typing import NamedTuple

class UserModel(NamedTuple):
    id: int
    username: str
    wins: int
    losses: int