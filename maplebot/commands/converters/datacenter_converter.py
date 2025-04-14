from discord.ext import commands
from discord.ext.commands import Context

import configs


class DatacenterConverter(commands.Converter):
    """Converts a string to a valid datacenter name."""

    async def convert(self, _: Context, argument: str) -> str:
        if argument.title() not in configs.DATACENTERS:
            raise commands.BadArgument(
                f"Provided datacenter is invalid. Please use `{configs.PREFIX}datacenters` to see the available datacenters."
            )

        return argument.title()
