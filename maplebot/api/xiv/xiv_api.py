import aiohttp
from pyxivapi.client import XIVAPIClient

import configs
from maplebot.api.xiv.models.items import XivApiItem

BASE_URL = configs.XIVAPI_BASE_URL
client: XIVAPIClient = None


async def conn():
    global client
    if client is None:
        client = XIVAPIClient(configs.XIVAPI_KEY)
    return client


async def get_item_by_name(item_name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/search?sheets=Item&query=Name~\"{item_name}\"&fields=Icon,Name,Description") as response:
            raw_data = await response.json()

            if len(raw_data["results"]) == 0:
                return None

            return XivApiItem(raw_data["results"][0])

