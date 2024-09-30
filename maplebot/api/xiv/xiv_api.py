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
    client = await conn()
    raw_data = await client.index_search(
        name=item_name,
        indexes=["Item"],
        columns=["ID", "Name", "IconHD", "Description"],
    )

    if len(raw_data["Results"]) == 0:
        return None

    return XivApiItem(raw_data["Results"][0])
