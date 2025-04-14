from discord.ext import commands
from discord.ext.commands import Context

import configs


class ServerConverter(commands.Converter):
    """Converts a string to a valid server name."""

    async def convert(self, _: Context, argument: str) -> str:
        servers = [
            server.lower()
            for _, dc_servers in configs.DATACENTERS.items()
            for server in dc_servers
        ]

        if argument.lower() not in servers:
            raise commands.BadArgument(
                f"Provided server is invalid. Please use `{configs.PREFIX}servers` to see the available servers."
            )

        return argument.title()
