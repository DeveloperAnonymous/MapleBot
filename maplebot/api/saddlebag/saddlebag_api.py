import aiohttp

import configs

from .models import SaddlebagItem

BASE_URL = configs.SADDLEBAG_BASE_URL


async def get_marketshare():
    url = f"{BASE_URL}/marketshare"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

            return SaddlebagItem(data)
