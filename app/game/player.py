from typing import Union

from aiogram.dispatcher import FSMContext

from ..bot import dp
from ..game import Field, Coordinate


class Player:
    def __init__(self, id: Union[str, int]):
        self._id = id

    @property
    def id(self) -> Union[str, int]:
        return self._id

    @property
    async def field(self) -> Field:
        state_data = await self._get_state_data()
        return Field(state_data["field"])

    @field.setter
    async def field(self, value: Field):
        state = self._get_state()
        await state.update_data(field=value.field)

    @property
    async def picked(self) -> Union[Coordinate, bool]:
        state_data = await self._get_state_data()
        coordinate = state_data["picked"]
        if isinstance(coordinate, bool):
            return coordinate
        return Coordinate(coordinate)

    @picked.setter
    async def picked(self, value: Union[Coordinate, bool]):
        state = self._get_state()
        if isinstance(value, bool):
            return await state.update_data(picked=value)
        await state.update_data(picked=str(value))

    @property
    async def opponent(self) -> "Player":
        state_data = await self._get_state_data()
        return Player(state_data["opponent_id"])

    async def _get_state_data(self) -> dict:
        state = self._get_state()
        return await state.get_data()

    def _get_state(self) -> FSMContext:
        return  dp.current_state(chat=self._id, user=self._id)
