import aiohttp
from pyxivapi.client import XIVAPIClient

import configs
from maplebot.api.xiv.models.items import XivApiItem

BASE_URL = configs.XIVAPI_BASE_URL
client: XIVAPIClient = None


async def get_item_by_name(item_name: str) -> XivApiItem | None:
    """
    Get an item by its name.

    :param item_name: The name of the item to search for.
    :param language_code: The language code to use for the search.
    :return: The item object if found, otherwise None.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{BASE_URL}/search?sheets=Item&query=Singular@ja~"{item_name}" Singular@en~"{item_name}" Singular@de~"{item_name}" Singular@fr~"{item_name}"&fields=Icon,Name,Description'
        ) as response:
            raw_data = await response.json()

            if len(raw_data["results"]) == 0:
                return None

            return XivApiItem(raw_data["results"][0])
