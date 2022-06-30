import sqlite3
from os import path
from typing import Union

from ..bot_config import DB_PATH
from .user_model import UserModel

PATH = path.dirname(__file__)
SCHEMAS = {
    "create_table_users": "create_table_users.sql",
    "insert_user": "insert_user.sql",
    "update_username": "update_username.sql",
    "get_user_by_id": "get_user_by_id.sql",
    "get_user_by_username": "get_user_by_username.sql",
    "increase_wins": "increase_wins.sql",
    "increase_losses": "increase_losses.sql"
}

for key, filename in SCHEMAS.items():
    with open(path.join(PATH, filename), "r") as f:
        SCHEMAS[key] = f.read()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def create_table_users():
    cursor.executescript(SCHEMAS["create_table_users"])


def insert_user(id: int, username: str):
    cursor.execute(SCHEMAS["insert_user"], (id, username))
    conn.commit()


def update_username(id: int, username: str):
    cursor.execute(SCHEMAS["update_username"], (username, id))
    conn.commit()


def get_user_by_id(id: int) -> Union[UserModel, None]:
    cursor.execute(SCHEMAS["get_user_by_id"], (id,))
    db_output = cursor.fetchone()
    return db_output and UserModel(*db_output)


def get_user_by_username(username: str) -> Union[UserModel, None]:
    cursor.execute(SCHEMAS["get_user_by_username"], (username,))
    db_output = cursor.fetchone()
    return db_output and UserModel(*db_output)


def increase_wins(id: int):
    cursor.execute(SCHEMAS["increase_wins"], (id,))
    conn.commit()


def increase_losses(id: int):
    cursor.execute(SCHEMAS["increase_losses"], (id,))
    conn.commit()