import json
import logging
from urllib.parse import urljoin

import aiohttp

from ..bot_config import API_URL


async def _get_response(destination: str, body: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(urljoin(API_URL, destination), data=json.dumps(body)) as r:
            res_text = await r.text()
            res_obj = json.loads(res_text)
            return res_obj


async def _request(destination: str, body: dict):
    try:
        response = await _get_response(destination, body)
    except (
        aiohttp.ClientError,
        aiohttp.ClientResponseError,
        json.decoder.JSONDecodeError
    ) as e:
        logging.error(f"Error in logic API - {e}")
        return None
    return response

async def pick(picked: str) -> dict:
    return await _request("pick", {
        "picked": picked
    })


async def move(move_to: str) -> dict:
    return await _request("move", {
        "moveTo": move_to
    })


async def promote(piece: str) -> dict:
    return await _request("promote", {
        "piece": piece
    })
