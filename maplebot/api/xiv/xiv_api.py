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


async def get_raw_item(item_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{configs.XIVAPI_BASE_URL}/item/{item_id}") as response:
            response.raise_for_status()

            json = await response.json()
            return json


async def get_item_by_id(item_id: int):
    """
    This function gets an item from the xivapi API.

    Parameters
    ----------
    item_id : int
        The item ID.

    Returns
    -------
    XivApiItem
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{configs.XIVAPI_BASE_URL}/item/{item_id}") as response:
            response.raise_for_status()

            data = await response.json()
            return XivApiItem(data)


async def get_item_by_name(item_name: str):
    client = await conn()
    raw_data = await client.index_search(name=item_name, language="en", indexes=["Item"],
                                         columns=["ID", "Name", "IconHD", "Description"])

    if len(raw_data["Results"]) == 0:
        return None

    return XivApiItem(raw_data["Results"][0])


async def get_item_name(item_id: int):
    item = await get_raw_item(item_id)
    return item["Name"]


async def get_item_icon(item_id: int):
    item = await get_raw_item(item_id)
    return configs.XIVAPI_BASE_URL + item["IconHD"]


async def get_item_description(item_id: int):
    item = await get_raw_item(item_id)
    return item["Description"].split("\n")[0]
