import json

import aiohttp

from ..config import BACK_URL


async def call_logic_API(picked, field):
    async with aiohttp.ClientSession() as session:
        async with session.post(BACK_URL, data=json.dumps({
            "picked": picked,
            "field": field
        })) as r:
            return await r.text()
