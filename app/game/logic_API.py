import json
import logging
from typing import List, Tuple, Type, Optional
from urllib.parse import urljoin

import aiohttp
from pydantic import BaseModel, Field, ValidationError, validator

from ..bot_config import API_URL
from ..game import parse_coordinate_response


class PickResponse(BaseModel):
    can_move: List[Tuple[int]] = Field(..., alias="wcim")
    can_beat: List[Tuple[int]] = Field(..., alias="wcib")

    @validator("can_move", "can_beat")
    def parse_coordinates(cls, v):
        if not isinstance(v, str):
            raise ValueError
        return parse_coordinate_response(v)


class MoveResponse(BaseModel):
    check: bool = Field(..., alias="isCheck")
    mate: bool = Field(..., alias="isMate")
    field: List[List[str]] = ...
    promoting: bool = False

    @validator("check", "mate")
    def parse_checks(cls, v):
        if not isinstance(v, str):
            raise ValueError
        if any(v.lower() == status.lower() for status in ["fromWhite", "fromBlack", "Both"]):
            return True
        return False


async def _get_response(destination: str, body: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(urljoin(API_URL, destination), data=json.dumps(body)) as r:
            res_text = await r.text()
            res_obj = json.loads(res_text)
            return res_obj


async def _request(destination: str, body: dict,
                   response_model: Type[BaseModel]):
    try:
        response = response_model.parse_obj(await _get_response(destination, body))
    except (
        aiohttp.ClientError,
        aiohttp.ClientResponseError,
        json.decoder.JSONDecodeError,
        ValidationError
    ) as e:
        logging.error(f"Error in logic API - {e}")
        return None
    return response


async def pick(picked: str):
    return await _request("pick", {
        "picked": picked
    }, PickResponse)


async def move(move_to: str):
    return await _request("move", {
        "moveTo": move_to
    }, MoveResponse)


async def promote(piece: str):
    return await _request("promote", {
        "piece": piece
    }, MoveResponse)
