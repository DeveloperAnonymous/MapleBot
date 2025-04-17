import aiohttp

import configs
from maplebot.api.universalis.models.item import UniversalisItem

BASE_URL = configs.UNIVERSALIS_BASE_URL

FIELDS = [
    "itemID",
    "lastUploadTime",
    "minPriceNQ",
    "minPriceHQ",
    "listings.lastReviewTime",
    "listings.pricePerUnit",
    "listings.quantity",
    "listings.worldName",
    "listings.hq",
    "listings.total",
]


async def get_item(item_id: int, listings: int, hq: bool, world: str) -> UniversalisItem:
    """
    This function gets an item from the Universalis API.

    Parameters
    ----------
    item_id : int
        The item ID.
    listings : int
        The number of listings to get.
    hq : bool
        Whether to get the HQ item or not.
    world : str, optional
        The world to get the market info from.

    Returns
    -------
    UniversalisItem
        The item with the market info.
    """
    if world is None:
        world = "Aether"

    request_fields = ",".join(FIELDS)
    request_params = f"listings={listings}&entries=0&statsWithin=0&entriesWithin=0&hq={hq}&fields={request_fields}"

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/{world}/{item_id}?{request_params}") as response:
            response.raise_for_status()

            data = await response.json()
            return UniversalisItem(data)
