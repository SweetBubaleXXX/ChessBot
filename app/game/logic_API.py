import json

import aiohttp

from ..bot_config import API_URL


async def pick(picked, field) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, data=json.dumps({
            "picked": picked,
            "field": field
        })) as r:
            res_text = await r.text()
            res_obj = json.loads(res_text)
            return res_obj
