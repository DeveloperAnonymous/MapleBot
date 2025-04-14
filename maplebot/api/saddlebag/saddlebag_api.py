import aiohttp

import configs

from . import SaddlebagItem

BASE_URL = configs.SADDLEBAG_BASE_URL


async def get_marketshares(
    time_period: int,
    sales_amount: int,
    sort_by: str,
    server: str,
):
    async with aiohttp.ClientSession() as session:
        data = {
            "server": server.title(),
            "time_period": time_period,
            "sales_amount": sales_amount,
            "sort_by": sort_by,
        }
        async with session.post(f"{BASE_URL}/ffxivmarketshare", data=data) as response:
            response.raise_for_status()
            response = await response.json()

            return [SaddlebagItem(item) for item in response["data"]]
