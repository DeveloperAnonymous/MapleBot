"""Commands module for user settings."""

import discord
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, Context

import configs
from maplebot import Bot, emojis, util
from maplebot.commands.interactions import WorldSelectionInteraction
from maplebot.util import MarketAlertException


class User(commands.Cog):
    """Commands for user settings."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command(brief="Set your preferred world for the market commands.")
    async def setworld(self, ctx: Context):
        f"""
        Set your preferred world for the market commands.

        Syntax:
        {configs.PREFIX}setworld
        """
        view = WorldSelectionInteraction(ctx.author)
        message = await ctx.send("Please select your world from the dropdown menu below:", view=view)
        await view.wait()

        selection = view.selection
        if selection is None:
            return await message.edit(content="You didn't select a world in time. Please try again.", view=None)

        async with self.bot.db_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO user_settings (id, region, datacenter, world)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id)
                    DO UPDATE SET region = EXCLUDED.region, datacenter = EXCLUDED.datacenter, world = EXCLUDED.world
                    """,
                    (ctx.author.id, selection.region, selection.datacenter, selection.world),
                )

        await message.edit(content=f"Preferred server set to **{selection.datacenter} - {selection.world}**")

    @commands.hybrid_command(brief="Get your preferred world.")
    async def world(self, ctx: Context):
        f"""
        Get your preferred world.

        Syntax:
        {configs.PREFIX}world
        """
        async with self.bot.db_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT datacenter, world FROM user_settings WHERE id = %s",
                    (ctx.author.id,),
                )
                result = await cursor.fetchone()

        if result is None or result[1] is None:
            return await ctx.send(f"You don't have a preferred world set. Use `{configs.PREFIX}setworld` to set one.")

        datacenter, world = result
        await ctx.send(f"Your preferred world is set to **{datacenter} - {world}**")

    @commands.hybrid_command(brief="Remove all your data from our database.")
    async def forgetme(self, ctx: Context, confirm: bool = None):
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
                    "DELETE FROM user_settings WHERE id = %s",
                    (ctx.author.id,),
                )

        await message.edit(content="All your data has been removed from our database.")

    async def cog_command_error(self, ctx: Context, error):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                return await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(f"Unable to send Exception message, \n{error.message}")

        await ctx.message.add_reaction(emojis.QUESTION)
        raise error


async def setup(bot: Bot):
    await bot.add_cog(User(bot))
    util.logger.info("User cog loaded")
