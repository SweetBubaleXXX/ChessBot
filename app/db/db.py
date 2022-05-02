import sqlite3
from os import path
from typing import Union

from ..bot_config import DB_PATH

PATH = path.dirname(__file__)
SCHEMAS = {
    "create_table_users": "create_table_users.sql",
    "insert_user": "insert_user.sql",
    "get_user_by_id": "get_user_by_id.sql",
    "get_user_by_username": "get_user_by_username.sql"
}

for key, filename in SCHEMAS.items():
    with open(path.join(PATH, filename), "r") as f:
        SCHEMAS[key] = f.read()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def create_table_users():
    cursor.executescript(SCHEMAS["create_table_users"])


def append_user(id: int, username: str):
    cursor.execute(SCHEMAS["insert_user"], (id, username))
    conn.commit()


def get_user_by_id(id: int) -> Union[tuple, None]:
    cursor.execute(SCHEMAS["get_user_by_id"], (id,))
    return cursor.fetchone()


def get_user_by_username(username: str) -> Union[tuple, None]:
    cursor.execute(SCHEMAS["get_user_by_username"], (username,))
    return cursor.fetchone()
