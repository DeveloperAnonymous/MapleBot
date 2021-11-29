import aiohttp

import configs
from bot.api.universalis.models.item import UniversalisItem

BASE_URL = configs.UNIVERSALIS_BASE_URL


async def get_item(item_id: int, world: str | None = "Aether") -> UniversalisItem:
    """
    This function gets an item from the Universalis API.

    Parameters
    ----------
    item_id : int
        The item ID.
    world : str, optional
        The world to get the market info from. Defaults to "Aether".

    Returns
    -------
    UniversalisItem
    """
    if world is None:
        world = "Aether"

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/{world}/{item_id}") as response:
            response.raise_for_status()

            data = await response.json()
            return UniversalisItem(data)
