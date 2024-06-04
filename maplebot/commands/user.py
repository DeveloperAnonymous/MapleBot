"""Commands module for user settings."""

from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, Context

import configs
from maplebot import Bot, emojis, util
from maplebot.util import MarketAlertException


class User(commands.Cog):
    """Commands for user settings."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def datacenter(self, ctx: Context, datacenter: Optional[str]):
        """
        Set your preferred datacenter for the market commands.

        Syntax:
        ma!datacenter
        ma!datacenter (datacenter)

        Example:
        ma!datacenter Dynamis
        """
        if not datacenter:
            # Show the user's current datacenter
            async with self.bot.db_pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT datacenter FROM user_settings WHERE discord_id = %s",
                        (ctx.author.id,),
                    )
                    result = await cursor.fetchone()

            if result is None:
                return await ctx.send(
                    "You don't have a preferred datacenter set. Use `ma!datacenter <datacenter>` to set one."
                )

            return await ctx.send(f"Your preferred datacenter is set to {result[0]}")

        if not any(datacenter.lower() == x.lower() for x in configs.SERVERS):
            raise MarketAlertException(
                ctx.channel,
                "Invalid datacenter, please use `ma!datacenters` to see the available datacenters.",
            )

        # open a connection to the database
        async with self.bot.db_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Insert or udpate the user's default datacenter
                await cursor.execute(
                    """
                    INSERT INTO user_settings (discord_id, datacenter)
                    VALUES (%s, %s)
                    ON CONFLICT (discord_id)
                    DO UPDATE SET datacenter = EXCLUDED.datacenter
                    """,
                    (ctx.author.id, datacenter.capitalize()),
                )

        await ctx.send(f"Preferred datacenter set to **{datacenter.capitalize()}**")

    @commands.command()
    async def datacenters(self, ctx: Context):
        """List all available datacenters."""
        await ctx.send(
            "Available datacenters:\n- " + "\n- ".join(sorted(configs.SERVERS.keys()))
        )

    async def cog_command_error(self, ctx: Context, error):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(
                    f"Unable to send Exception message, \n{error.message}"
                )

        await ctx.message.add_reaction(emojis.QUESTION)
        raise error


async def setup(bot: Bot):
    """Load the User cog."""
    await bot.add_cog(User(bot))
