"""Commands module for user settings."""

import discord
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, Context

import configs
from maplebot import Bot, emojis, util
from maplebot.commands.converters import DatacenterConverter, ServerConverter
from maplebot.util import MarketAlertException


class User(commands.Cog):
    """Commands for user settings."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def datacenter(self, ctx: Context, datacenter: DatacenterConverter | None):
        f"""
        Set your preferred datacenter for the market commands.

        Syntax:
        {configs.PREFIX}datacenter (datacenter)

        Example:
        {configs.PREFIX}datacenter
        {configs.PREFIX}datacenter Aether
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
                    f"You don't have a preferred datacenter set. Use `{configs.PREFIX}datacenter <datacenter>` to set one."
                )

            return await ctx.send(f"Your preferred datacenter is set to {result[0]}")

        if not any(datacenter.lower() == x.lower() for x in configs.DATACENTERS):
            raise MarketAlertException(
                ctx.channel,
                f"Invalid datacenter, please use `{configs.PREFIX}datacenters` to see the available datacenters.",
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
                    (ctx.author.id, datacenter),
                )

        await ctx.send(f"Preferred datacenter set to **{datacenter}**")

    @commands.command()
    async def datacenters(self, ctx: Context):
        """List all available datacenters."""
        await ctx.send("Available datacenters:\n- " + "\n- ".join(sorted(configs.DATACENTERS.keys())))

    @commands.command()
    async def server(self, ctx: Context, server: ServerConverter | None):
        f"""
        Set your preferred server for the saddlebag commands.

        This will also override (or set) your preferred datacenter for the server's datacenter.

        Syntax:
        {configs.PREFIX}server (server)

        Example:
        {configs.PREFIX}server
        {configs.PREFIX}server Jenova
        """
        if not server:
            # Show the user's current server
            async with self.bot.db_pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT server FROM user_settings WHERE discord_id = %s",
                        (ctx.author.id,),
                    )
                    result = await cursor.fetchone()

            if result is None:
                return await ctx.send(
                    "You don't have a preferred server set. Use `{configs.PREFIX}server <server>` to set one."
                )

            return await ctx.send(f"Your preferred server is set to **{result[0]}**")

        # get the datacenter for the server, override the datacenter if it's set
        datacenter = next(dc for dc, servers in configs.DATACENTERS.items() if server in servers)

        async with self.bot.db_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Insert or udpate the user's default server
                await cursor.execute(
                    """
                    INSERT INTO user_settings (discord_id, datacenter, server)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (discord_id)
                    DO UPDATE SET datacenter = EXCLUDED.datacenter, server = EXCLUDED.server
                    """,
                    (ctx.author.id, datacenter, server),
                )

        await ctx.send(f"Preferred server set to **{server}**")

    @commands.command()
    async def servers(self, ctx: Context, datacenter: DatacenterConverter | None):
        f"""
        List all available servers. If datacenter is specified, it will list the servers for that datacenter.

        Syntax:
        {configs.PREFIX}servers (datacenter)

        Example:
        {configs.PREFIX}servers
        {configs.PREFIX}servers Aether
        """
        if datacenter:
            servers = configs.DATACENTERS[datacenter]
            await ctx.send(f"**{datacenter}**\n- " + "\n- ".join(servers))
        else:
            datacenters = "\n".join(
                f"**{datacenter}**: " + ", ".join(servers) for datacenter, servers in configs.DATACENTERS.items()
            )
            await ctx.send(datacenters)

    async def cog_command_error(self, ctx: Context, error):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(f"Unable to send Exception message, \n{error.message}")

        await ctx.message.add_reaction(emojis.QUESTION)
        raise error

    @commands.command()
    async def forgetme(self, ctx: Context, confirm: bool | None):
        f"""
        This will remove all the data linked to your discord account from our database.

        Syntax:
        {configs.PREFIX}forgetme (confirm)

        Example:
        {configs.PREFIX}forgetme
        {configs.PREFIX}forgetme True
        {configs.PREFIX}forgetme yes
        {configs.PREFIX}forgetme y
        {configs.PREFIX}forgetme 1

        Note: This action is irreversible.
        """
        if confirm is None:
            return await ctx.send(
                "This actioon is **irreversible** and will remove all the data linked to your discord account from our database. "
                + f"Are you sure you want to proceed? Type `{configs.PREFIX}forgetme True` to confirm."
            )

        if not confirm:
            return await ctx.send("Understood, I won't remove your data")

        message = await ctx.send("Removing all your data from our database...")

        async with self.bot.db_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM user_settings WHERE discord_id = %(discord_id)s",
                    {"discord_id": ctx.author.id},
                )

        await message.edit(content="All your data has been removed from our database.")


async def setup(bot: Bot):
    """Load the User cog."""
    await bot.add_cog(User(bot))
    util.logger.info("User cog loaded")
