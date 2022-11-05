import json
from urllib.parse import urljoin

import aiohttp

from ..bot_config import API_URL


async def _request(destination: str, body: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(urljoin(API_URL, destination), data=json.dumps(body)) as r:
            res_text = await r.text()
            res_obj = json.loads(res_text)
            return res_obj


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
