from typing import Union

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from .models import Player, Settings, Base
from ..bot_config import DB_PATH

engine = create_async_engine(DB_PATH)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def create_table_users():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def insert_user(id: int, username: str):
    async with async_session() as session:
        async with session.begin():
            session.add(Player(id=id, username=username))


def update_username(id: int, username: str): ...


def get_user_by_id(id: int) -> Union[Player, None]: ...


def get_user_by_username(username: str) -> Union[Player, None]: ...


def increase_wins(id: int): ...


def increase_losses(id: int): ...
