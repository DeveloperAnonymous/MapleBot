import aiohttp

import configs


async def get_item_name(item_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{configs.XIVAPI_BASE_URL}/item/{item_id}") as response:
            response.raise_for_status()

            json = await response.json()
            return json["Name"]
